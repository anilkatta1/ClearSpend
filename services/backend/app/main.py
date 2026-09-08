import hashlib
import json
from contextvars import ContextVar
from typing import Annotated, Any
from uuid import uuid4

import structlog
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.audit import append_audit, verify_chain
from app.db import (
    AuditEvent,
    Expense,
    OutboxEvent,
    PolicyRule,
    PolicySection,
    PolicyVersion,
    get_session,
    utcnow,
)
from app.domain import ExpenseState, Role, validate_rule_params
from app.jobs import enqueue_assessment
from app.schemas import DecisionIn, ExpenseIn, PolicyDraftIn, ResubmissionIn
from app.security import Principal, PrincipalDep, require_roles
from app.services import DomainConflict, active_policy, decide, serialize_expense

logger = structlog.get_logger()
correlation_context: ContextVar[str] = ContextVar("correlation_id", default="")
app = FastAPI(title="ClearSpend API", version="0.1.0", openapi_url="/api/v1/openapi.json")
SessionDep = Annotated[Session, Depends(get_session)]


def problem(
    status_code: int, code: str, title: str, detail: str, correlation_id: str
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        media_type="application/problem+json",
        content={
            "type": f"https://clears-spend.local/problems/{code.lower().replace('_', '-')}",
            "title": title,
            "status": status_code,
            "code": code,
            "correlationId": correlation_id,
            "detail": detail,
        },
    )


@app.middleware("http")
async def correlation_middleware(request: Request, call_next: Any) -> Response:
    supplied = request.headers.get("X-Correlation-ID", "")
    correlation_id = supplied if 8 <= len(supplied) <= 80 else str(uuid4())
    token = correlation_context.set(correlation_id)
    try:
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        logger.info(
            "request.completed",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            correlation_id=correlation_id,
        )
        return response
    finally:
        correlation_context.reset(token)


@app.exception_handler(DomainConflict)
async def domain_conflict_handler(_: Request, exc: DomainConflict) -> JSONResponse:
    return problem(
        409,
        "DOMAIN_CONFLICT",
        "The operation conflicts with current state",
        str(exc),
        correlation_context.get(),
    )


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return problem(
        422,
        "VALIDATION_ERROR",
        "The request is invalid",
        str(exc.errors()),
        correlation_context.get(),
    )


@app.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready")
def ready(session: SessionDep) -> dict[str, str]:
    session.execute(text("select 1"))
    return {"status": "ready"}


@app.get("/api/v1/me")
def me(principal: PrincipalDep) -> dict[str, str]:
    return {
        "id": principal.user_id,
        "email": principal.email,
        "name": principal.name,
        "role": principal.role,
        "organization_id": principal.organization_id,
    }


@app.post("/api/v1/policies/drafts", status_code=201)
def create_policy(
    body: PolicyDraftIn,
    session: SessionDep,
    principal: Annotated[Principal, Depends(require_roles(Role.ADMIN))],
) -> dict[str, Any]:
    for section_input in body.sections:
        for rule in section_input.rules:
            validate_rule_params(rule.rule_type, rule.params)
    version = (
        session.scalar(
            select(PolicyVersion.version)
            .where(PolicyVersion.organization_id == principal.organization_id)
            .order_by(PolicyVersion.version.desc())
            .limit(1)
        )
        or 0
    ) + 1
    policy = PolicyVersion(
        organization_id=principal.organization_id, version=version, title=body.title
    )
    for sequence, section_in in enumerate(body.sections, 1):
        policy_section = PolicySection(
            section_key=section_in.section_key,
            title=section_in.title,
            source_text=section_in.source_text,
            sequence=sequence,
        )
        policy_section.rules = [
            PolicyRule(rule_type=rule.rule_type, params=rule.params, priority=rule.priority)
            for rule in section_in.rules
        ]
        policy.sections.append(policy_section)
    session.add(policy)
    session.flush()
    append_audit(
        session,
        organization_id=principal.organization_id,
        actor_id=principal.user_id,
        entity_type="policy",
        entity_id=policy.id,
        action="policy.draft_created",
        metadata={"version": version},
        correlation_id=correlation_context.get(),
    )
    session.commit()
    return {
        "id": policy.id,
        "version": policy.version,
        "status": policy.status,
        "title": policy.title,
    }


@app.post("/api/v1/policies/{policy_id}/publish", status_code=201)
def publish_policy(
    policy_id: str,
    session: SessionDep,
    principal: Annotated[Principal, Depends(require_roles(Role.ADMIN))],
) -> dict[str, Any]:
    policy = session.scalar(
        select(PolicyVersion)
        .where(
            PolicyVersion.id == policy_id,
            PolicyVersion.organization_id == principal.organization_id,
        )
        .with_for_update()
    )
    if policy is None:
        raise HTTPException(404, "Policy not found")
    if policy.status != "DRAFT":
        raise DomainConflict("Published policies are immutable")
    for current in session.scalars(
        select(PolicyVersion).where(
            PolicyVersion.organization_id == principal.organization_id,
            PolicyVersion.status == "PUBLISHED",
        )
    ):
        current.status = "SUPERSEDED"
    canonical = json.dumps(
        [
            {
                "key": s.section_key,
                "text": s.source_text,
                "rules": [{"type": r.rule_type, "params": r.params} for r in s.rules],
            }
            for s in policy.sections
        ],
        sort_keys=True,
        separators=(",", ":"),
    )
    policy.content_hash = hashlib.sha256(canonical.encode()).hexdigest()
    policy.status = "PUBLISHED"
    policy.publisher_id = principal.user_id
    policy.published_at = utcnow()
    append_audit(
        session,
        organization_id=principal.organization_id,
        actor_id=principal.user_id,
        entity_type="policy",
        entity_id=policy.id,
        action="policy.published",
        metadata={"version": policy.version, "content_hash": policy.content_hash},
        correlation_id=correlation_context.get(),
    )
    session.commit()
    return {
        "id": policy.id,
        "version": policy.version,
        "status": policy.status,
        "content_hash": policy.content_hash,
    }


@app.get("/api/v1/policies")
def list_policies(session: SessionDep, principal: PrincipalDep) -> list[dict[str, Any]]:
    items = session.scalars(
        select(PolicyVersion)
        .where(PolicyVersion.organization_id == principal.organization_id)
        .order_by(PolicyVersion.version.desc())
    ).all()
    return [
        {
            "id": p.id,
            "version": p.version,
            "title": p.title,
            "status": p.status,
            "content_hash": p.content_hash,
            "sections": [
                {"id": s.id, "key": s.section_key, "title": s.title, "source_text": s.source_text}
                for s in p.sections
            ],
        }
        for p in items
    ]


@app.post("/api/v1/expenses", status_code=202)
async def submit_expense(
    body: ExpenseIn,
    session: SessionDep,
    principal: Annotated[Principal, Depends(require_roles(Role.EMPLOYEE, Role.ADMIN))],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
) -> dict[str, Any]:
    existing = session.scalar(
        select(Expense).where(
            Expense.organization_id == principal.organization_id,
            Expense.idempotency_key == idempotency_key,
        )
    )
    if existing:
        return serialize_expense(existing)
    policy = active_policy(session, principal.organization_id)
    expense = Expense(
        organization_id=principal.organization_id,
        submitter_id=principal.user_id,
        policy_version_id=policy.id,
        idempotency_key=idempotency_key,
        **body.model_dump(),
    )
    session.add(expense)
    session.flush()
    append_audit(
        session,
        organization_id=principal.organization_id,
        actor_id=principal.user_id,
        entity_type="expense",
        entity_id=expense.id,
        action="expense.submitted",
        metadata={
            "policy_version": policy.version,
            "amount_minor": expense.amount_minor,
            "currency": expense.currency,
        },
        correlation_id=correlation_context.get(),
    )
    session.add(
        OutboxEvent(
            organization_id=principal.organization_id,
            aggregate_id=expense.id,
            event_type="assessment.requested",
            payload={
                "expense_id": expense.id,
                "revision": expense.revision,
                "correlation_id": correlation_context.get(),
            },
        )
    )
    session.commit()
    try:
        await enqueue_assessment(expense.id, correlation_context.get())
    except Exception as exc:
        logger.warning("assessment.enqueue_failed", expense_id=expense.id, error=type(exc).__name__)
    return serialize_expense(expense)


@app.get("/api/v1/expenses")
def list_expenses(session: SessionDep, principal: PrincipalDep) -> list[dict[str, Any]]:
    query = (
        select(Expense)
        .where(Expense.organization_id == principal.organization_id)
        .order_by(Expense.created_at.desc())
    )
    if principal.role == Role.EMPLOYEE:
        query = query.where(Expense.submitter_id == principal.user_id)
    return [serialize_expense(item) for item in session.scalars(query).unique().all()]


@app.get("/api/v1/expenses/{expense_id}")
def get_expense(expense_id: str, session: SessionDep, principal: PrincipalDep) -> dict[str, Any]:
    query = select(Expense).where(
        Expense.id == expense_id, Expense.organization_id == principal.organization_id
    )
    if principal.role == Role.EMPLOYEE:
        query = query.where(Expense.submitter_id == principal.user_id)
    expense = session.scalar(query)
    if expense is None:
        raise HTTPException(404, "Expense not found")
    return serialize_expense(expense)


@app.post("/api/v1/expenses/{expense_id}/decisions", status_code=201)
def create_decision(
    expense_id: str,
    body: DecisionIn,
    session: SessionDep,
    principal: Annotated[Principal, Depends(require_roles(Role.REVIEWER, Role.ADMIN))],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
) -> dict[str, Any]:
    expense = session.scalar(
        select(Expense)
        .where(Expense.id == expense_id, Expense.organization_id == principal.organization_id)
        .with_for_update()
    )
    if expense is None:
        raise HTTPException(404, "Expense not found")
    decision = decide(
        session,
        expense=expense,
        actor_id=principal.user_id,
        action=body.action,
        reason=body.reason,
        expected_version=body.expected_row_version,
        idempotency_key=idempotency_key,
        correlation_id=correlation_context.get(),
    )
    return {
        "id": decision.id,
        "action": decision.action,
        "reason": decision.reason,
        "expense": serialize_expense(expense),
    }


@app.post("/api/v1/expenses/{expense_id}/resubmissions", status_code=202)
async def resubmit(
    expense_id: str,
    body: ResubmissionIn,
    session: SessionDep,
    principal: Annotated[Principal, Depends(require_roles(Role.EMPLOYEE))],
) -> dict[str, Any]:
    expense = session.scalar(
        select(Expense)
        .where(
            Expense.id == expense_id,
            Expense.organization_id == principal.organization_id,
            Expense.submitter_id == principal.user_id,
        )
        .with_for_update()
    )
    if expense is None:
        raise HTTPException(404, "Expense not found")
    if expense.state != ExpenseState.INFORMATION_REQUESTED:
        raise DomainConflict("Expense is not awaiting additional information")
    expense.purpose = body.purpose
    expense.receipt_present = body.receipt_present
    expense.receipt_hash = body.receipt_hash
    expense.revision += 1
    expense.row_version += 1
    expense.state = ExpenseState.SUBMITTED
    append_audit(
        session,
        organization_id=principal.organization_id,
        actor_id=principal.user_id,
        entity_type="expense",
        entity_id=expense.id,
        action="expense.resubmitted",
        metadata={"revision": expense.revision},
        correlation_id=correlation_context.get(),
    )
    session.add(
        OutboxEvent(
            organization_id=principal.organization_id,
            aggregate_id=expense.id,
            event_type="assessment.requested",
            payload={
                "expense_id": expense.id,
                "revision": expense.revision,
                "correlation_id": correlation_context.get(),
            },
        )
    )
    session.commit()
    try:
        await enqueue_assessment(expense.id, correlation_context.get())
    except Exception as exc:
        logger.warning("assessment.enqueue_failed", expense_id=expense.id, error=type(exc).__name__)
    return serialize_expense(expense)


@app.get("/api/v1/audit-events")
def audit_events(
    session: SessionDep,
    principal: Annotated[Principal, Depends(require_roles(Role.ADMIN, Role.AUDITOR))],
) -> dict[str, Any]:
    events = session.scalars(
        select(AuditEvent)
        .where(AuditEvent.organization_id == principal.organization_id)
        .order_by(AuditEvent.sequence)
    ).all()
    return {
        "chain_valid": verify_chain(list(events)),
        "events": [
            {
                "id": e.id,
                "sequence": e.sequence,
                "action": e.action,
                "entity_type": e.entity_type,
                "entity_id": e.entity_id,
                "actor_id": e.actor_id,
                "metadata": e.metadata_json,
                "correlation_id": e.correlation_id,
                "event_hash": e.event_hash,
                "occurred_at": e.occurred_at,
            }
            for e in events
        ],
    }

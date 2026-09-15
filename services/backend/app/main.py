import asyncio
import hashlib
import json
import statistics
from contextvars import ContextVar
from typing import Annotated, Any
from uuid import uuid4

import structlog
from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, Response, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.audit import append_audit, verify_chain
from app.db import (
    AccountingExport,
    ApprovalDecision,
    AssessmentAttempt,
    AuditEvent,
    Expense,
    Organization,
    OutboxEvent,
    PolicyRule,
    PolicySection,
    PolicyVersion,
    Receipt,
    get_session,
    utcnow,
)
from app.domain import ExpenseState, Role, ensure_transition, validate_rule_params
from app.jobs import enqueue_assessment
from app.receipts import MAX_RECEIPT_BYTES, ReceiptError, extract_receipt, validate_receipt
from app.schemas import DecisionIn, ExpenseIn, ExportIn, PolicyDraftIn, ResubmissionIn
from app.security import Principal, PrincipalDep, require_roles
from app.services import DomainConflict, active_policy, decide, export_expense, serialize_expense

logger = structlog.get_logger()
correlation_context: ContextVar[str] = ContextVar("correlation_id", default="")
app = FastAPI(title="ClearSpend API", version="0.1.0", openapi_url="/api/v1/openapi.json")
SessionDep = Annotated[Session, Depends(get_session)]


def request_hash(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(encoded).hexdigest()


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
    fields = [
        ".".join(str(part) for part in item["loc"] if part != "body") for item in exc.errors()
    ]
    return problem(
        422,
        "VALIDATION_ERROR",
        "The request is invalid",
        f"Invalid fields: {', '.join(fields)}",
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


@app.post("/api/v1/receipts", status_code=201)
async def upload_receipt(
    session: SessionDep,
    principal: Annotated[Principal, Depends(require_roles(Role.EMPLOYEE, Role.ADMIN))],
    file: Annotated[UploadFile, File()],
) -> dict[str, Any]:
    content = await file.read(MAX_RECEIPT_BYTES + 1)
    content_type = file.content_type or ""
    try:
        validate_receipt(content, content_type)
    except ReceiptError as exc:
        raise HTTPException(415, str(exc)) from exc
    extracted = await asyncio.to_thread(extract_receipt, content, content_type)
    receipt = Receipt(
        organization_id=principal.organization_id,
        uploader_id=principal.user_id,
        filename=(file.filename or "receipt")[:200],
        content_type=content_type,
        size_bytes=len(content),
        content_hash=hashlib.sha256(content).hexdigest(),
        content=content,
        extraction_status=extracted.status,
        extracted_text=extracted.text,
        extracted_merchant=extracted.merchant,
        extracted_date=extracted.incurred_date,
        extracted_amount_minor=extracted.amount_minor,
        extracted_currency=extracted.currency,
    )
    session.add(receipt)
    session.flush()
    append_audit(
        session,
        organization_id=principal.organization_id,
        actor_id=principal.user_id,
        entity_type="receipt",
        entity_id=receipt.id,
        action="receipt.uploaded",
        metadata={"content_type": content_type, "status": extracted.status},
        correlation_id=correlation_context.get(),
    )
    session.commit()
    return {
        "id": receipt.id,
        "filename": receipt.filename,
        "content_type": receipt.content_type,
        "extraction_status": receipt.extraction_status,
        "extracted_merchant": receipt.extracted_merchant,
        "extracted_date": receipt.extracted_date,
        "extracted_amount_minor": receipt.extracted_amount_minor,
        "extracted_currency": receipt.extracted_currency,
        "preview_url": f"/api/v1/receipts/{receipt.id}/content",
    }


@app.get("/api/v1/receipts/{receipt_id}/content")
def receipt_content(receipt_id: str, session: SessionDep, principal: PrincipalDep) -> Response:
    query = select(Receipt).where(
        Receipt.id == receipt_id, Receipt.organization_id == principal.organization_id
    )
    if principal.role == Role.EMPLOYEE:
        query = query.where(Receipt.uploader_id == principal.user_id)
    receipt = session.scalar(query)
    if receipt is None:
        raise HTTPException(404, "Receipt not found")
    return Response(
        content=receipt.content,
        media_type=receipt.content_type,
        headers={"Content-Disposition": f'inline; filename="{receipt.id}"'},
    )


@app.post("/api/v1/expenses", status_code=202)
async def submit_expense(
    body: ExpenseIn,
    session: SessionDep,
    principal: Annotated[Principal, Depends(require_roles(Role.EMPLOYEE, Role.ADMIN))],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=128)],
) -> dict[str, Any]:
    body_hash = request_hash(body.model_dump(mode="json"))
    session.scalar(
        select(Organization.id)
        .where(Organization.id == principal.organization_id)
        .with_for_update()
    )
    existing = session.scalar(
        select(Expense).where(
            Expense.organization_id == principal.organization_id,
            Expense.submitter_id == principal.user_id,
            Expense.idempotency_key == idempotency_key,
        )
    )
    if existing:
        if existing.submitter_id != principal.user_id or existing.request_hash != body_hash:
            raise DomainConflict("Idempotency key was already used for a different submission")
        return serialize_expense(existing)
    receipt = session.scalar(
        select(Receipt).where(
            Receipt.id == body.receipt_id,
            Receipt.organization_id == principal.organization_id,
            Receipt.uploader_id == principal.user_id,
        )
    )
    if receipt is None:
        raise HTTPException(404, "Receipt not found")
    policy = active_policy(session, principal.organization_id)
    fields = body.model_dump(exclude={"receipt_id"})
    expense = Expense(
        organization_id=principal.organization_id,
        submitter_id=principal.user_id,
        policy_version_id=policy.id,
        idempotency_key=idempotency_key,
        request_hash=body_hash,
        receipt_id=receipt.id,
        receipt_present=True,
        receipt_hash=receipt.content_hash,
        **fields,
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
        request_hash=request_hash({"expense_id": expense_id, **body.model_dump(mode="json")}),
        requested_fields=list(body.requested_fields),
        reviewer_active_ms=body.reviewer_active_ms,
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
    ensure_transition(ExpenseState(expense.state), ExpenseState.SUBMITTED)
    if body.receipt_id:
        receipt = session.scalar(
            select(Receipt).where(
                Receipt.id == body.receipt_id,
                Receipt.organization_id == principal.organization_id,
                Receipt.uploader_id == principal.user_id,
            )
        )
        if receipt is None:
            raise HTTPException(404, "Receipt not found")
        expense.receipt_id = receipt.id
        expense.receipt_present = True
        expense.receipt_hash = receipt.content_hash
    expense.purpose = body.purpose
    expense.revision += 1
    expense.row_version += 1
    expense.state = ExpenseState.SUBMITTED
    expense.information_request_message = None
    expense.requested_fields = []
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


@app.post("/api/v1/expenses/{expense_id}/exports", status_code=201)
def create_export(
    expense_id: str,
    body: ExportIn,
    session: SessionDep,
    principal: Annotated[Principal, Depends(require_roles(Role.REVIEWER, Role.ADMIN))],
) -> dict[str, Any]:
    expense = session.scalar(
        select(Expense)
        .where(Expense.id == expense_id, Expense.organization_id == principal.organization_id)
        .with_for_update()
    )
    if expense is None:
        raise HTTPException(404, "Expense not found")
    record = export_expense(
        session,
        expense=expense,
        actor_id=principal.user_id,
        account_code=body.account_code,
        cost_center=body.cost_center,
        expected_version=body.expected_row_version,
        correlation_id=correlation_context.get(),
    )
    return {
        "id": record.id,
        "status": record.status,
        "download_url": f"/api/v1/exports/{record.id}/csv",
    }


@app.get("/api/v1/exports/{export_id}/csv")
def download_export(
    export_id: str,
    session: SessionDep,
    principal: Annotated[
        Principal, Depends(require_roles(Role.REVIEWER, Role.ADMIN, Role.AUDITOR))
    ],
) -> Response:
    record = session.scalar(
        select(AccountingExport).where(
            AccountingExport.id == export_id,
            AccountingExport.organization_id == principal.organization_id,
        )
    )
    if record is None or record.status != "EXPORTED" or record.csv_content is None:
        raise HTTPException(404, "Export not found")
    return Response(
        content=record.csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="clears-spend-{record.id}.csv"'},
    )


@app.get("/api/v1/metrics/product")
def product_metrics(
    session: SessionDep,
    principal: Annotated[Principal, Depends(require_roles(Role.ADMIN, Role.AUDITOR))],
) -> dict[str, Any]:
    decisions = session.scalars(
        select(ApprovalDecision).where(
            ApprovalDecision.organization_id == principal.organization_id
        )
    ).all()
    attempts = session.scalars(
        select(AssessmentAttempt).where(
            AssessmentAttempt.organization_id == principal.organization_id
        )
    ).all()
    expenses = (
        session.scalars(select(Expense).where(Expense.organization_id == principal.organization_id))
        .unique()
        .all()
    )
    elapsed = [
        (decision.created_at - expense.submitted_at).total_seconds()
        for decision in decisions
        for expense in expenses
        if decision.expense_id == expense.id
    ]
    overrides = sum(
        (d.action == "APPROVE" and d.observed_recommendation != "APPROVE_RECOMMENDED")
        or (d.action == "REJECT" and d.observed_recommendation != "REJECT_RECOMMENDED")
        for d in decisions
    )
    valid_sections_by_expense = {
        expense.id: {section.id for section in expense.policy_version.sections}
        for expense in expenses
    }
    citation_checks = [
        (attempt.expense_id, check) for attempt in attempts for check in attempt.checks
    ]
    citation_valid = sum(
        bool(check.get("policy_section_ids"))
        and set(check["policy_section_ids"]).issubset(
            valid_sections_by_expense.get(expense_id, set())
        )
        for expense_id, check in citation_checks
    )
    return {
        "claims_submitted": len(expenses),
        "decisions_completed": len(decisions),
        "median_submission_to_decision_seconds": statistics.median(elapsed) if elapsed else None,
        "median_active_reviewer_seconds": (
            statistics.median(
                [d.reviewer_active_ms / 1000 for d in decisions if d.reviewer_active_ms is not None]
            )
            if any(d.reviewer_active_ms is not None for d in decisions)
            else None
        ),
        "request_information_rate": (
            sum(d.action == "REQUEST_INFORMATION" for d in decisions) / len(decisions)
            if decisions
            else None
        ),
        "recommendation_override_rate": overrides / len(decisions) if decisions else None,
        "safe_fallback_rate": (
            sum(a.technical_status == "FALLBACK" for a in attempts) / len(attempts)
            if attempts
            else None
        ),
        "citation_validity_rate": (
            citation_valid / len(citation_checks) if citation_checks else None
        ),
        "exports_completed": sum(e.state == ExpenseState.EXPORTED for e in expenses),
        "note": "System workflow signals; not proof of payment or customer time savings.",
    }


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

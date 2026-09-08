import hashlib
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import AuditEvent

ZERO_HASH = "0" * 64


def canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def append_audit(
    session: Session,
    *,
    organization_id: str,
    actor_id: str | None,
    entity_type: str,
    entity_id: str,
    action: str,
    metadata: dict[str, Any],
    correlation_id: str,
) -> AuditEvent:
    last = session.scalar(
        select(AuditEvent)
        .where(AuditEvent.organization_id == organization_id)
        .order_by(AuditEvent.sequence.desc())
        .limit(1)
        .with_for_update()
    )
    sequence = (last.sequence + 1) if last else 1
    prior_hash = last.event_hash if last else ZERO_HASH
    body = {
        "organization_id": organization_id,
        "sequence": sequence,
        "actor_id": actor_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "action": action,
        "metadata": metadata,
        "correlation_id": correlation_id,
        "prior_hash": prior_hash,
    }
    event = AuditEvent(
        organization_id=organization_id,
        sequence=sequence,
        actor_id=actor_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        metadata_json=metadata,
        correlation_id=correlation_id,
        prior_hash=prior_hash,
        event_hash=hashlib.sha256(canonical_json(body).encode()).hexdigest(),
    )
    session.add(event)
    return event


def verify_chain(events: list[AuditEvent]) -> bool:
    prior = ZERO_HASH
    for event in sorted(events, key=lambda item: item.sequence):
        body = {
            "organization_id": event.organization_id,
            "sequence": event.sequence,
            "actor_id": event.actor_id,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "action": event.action,
            "metadata": event.metadata_json,
            "correlation_id": event.correlation_id,
            "prior_hash": prior,
        }
        expected = hashlib.sha256(canonical_json(body).encode()).hexdigest()
        if event.prior_hash != prior or event.event_hash != expected:
            return False
        prior = event.event_hash
    return True

from types import SimpleNamespace

from app.audit import ZERO_HASH, canonical_json, verify_chain


def event(sequence: int, prior_hash: str, event_hash: str):
    return SimpleNamespace(
        organization_id="org",
        sequence=sequence,
        actor_id="actor",
        entity_type="expense",
        entity_id="expense",
        action="expense.submitted",
        metadata_json={"amount_minor": 1000},
        correlation_id="correlation",
        prior_hash=prior_hash,
        event_hash=event_hash,
    )


def test_canonical_json_has_stable_key_order() -> None:
    assert canonical_json({"b": 2, "a": 1}) == '{"a":1,"b":2}'


def test_modified_audit_event_is_rejected() -> None:
    assert verify_chain([event(1, ZERO_HASH, "bad")]) is False

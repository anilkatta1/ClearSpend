from sqlalchemy import select

from app.db import (
    Base,
    Membership,
    Organization,
    PolicyRule,
    PolicySection,
    PolicyVersion,
    SessionLocal,
    User,
    engine,
    utcnow,
)
from app.domain import Role


def create_org(session, slug: str, name: str, users: list[tuple[str, str, Role]]) -> Organization:
    org = Organization(slug=slug, name=name)
    session.add(org)
    session.flush()
    for email, user_name, role in users:
        user = User(email=email, name=user_name)
        session.add(user)
        session.flush()
        session.add(Membership(organization_id=org.id, user_id=user.id, role=role))
    policy = PolicyVersion(
        organization_id=org.id,
        version=1,
        status="PUBLISHED",
        title="Demo reimbursement policy",
        content_hash="seed-demo-policy-v1",
        published_at=utcnow(),
    )
    section = PolicySection(
        section_key="general",
        title="General reimbursement rules",
        source_text=(
            "Receipts are required from INR 1,000. Alcohol is prohibited. "
            "Claims must be submitted within 30 days. The maximum claim is INR 50,000."
        ),
        sequence=1,
    )
    section.rules = [
        PolicyRule(
            rule_type="receipt_required",
            params={"threshold_minor": 100000, "currency": "INR"},
            priority=10,
        ),
        PolicyRule(
            rule_type="amount_limit",
            params={"limit_minor": 5000000, "currency": "INR"},
            priority=20,
        ),
        PolicyRule(
            rule_type="prohibited_category",
            params={"categories": ["alcohol", "personal"]},
            priority=30,
        ),
        PolicyRule(rule_type="business_purpose_required", params={}, priority=40),
        PolicyRule(rule_type="submission_window", params={"days": 30}, priority=50),
    ]
    policy.sections = [section]
    session.add(policy)
    return org


def main() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        if session.scalar(select(Organization.id).limit(1)):
            return
        create_org(
            session,
            "acme",
            "Acme India",
            [
                ("employee@acme.test", "Esha Employee", Role.EMPLOYEE),
                ("reviewer@acme.test", "Ravi Reviewer", Role.REVIEWER),
                ("admin@acme.test", "Aditi Admin", Role.ADMIN),
                ("auditor@acme.test", "Arun Auditor", Role.AUDITOR),
            ],
        )
        create_org(
            session,
            "globex",
            "Globex India",
            [("employee@globex.test", "Gita Employee", Role.EMPLOYEE)],
        )
        session.commit()


if __name__ == "__main__":
    main()

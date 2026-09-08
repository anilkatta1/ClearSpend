"""Exercise the deployed local workflow using synthetic demo identities."""

import time
from uuid import uuid4

import httpx

BASE_URL = "http://localhost:8000/api/v1"


def headers(identity: str, *, idempotent: bool = False) -> dict[str, str]:
    result = {"X-Demo-User": identity, "X-Correlation-ID": f"smoke-{uuid4()}"}
    if idempotent:
        result["Idempotency-Key"] = str(uuid4())
    return result


def main() -> None:
    with httpx.Client(base_url=BASE_URL, timeout=10) as client:
        response = client.post(
            "/expenses",
            headers=headers("employee@acme.test", idempotent=True),
            json={
                "merchant": "Synthetic Conference Hotel",
                "amount_minor": 225_000,
                "currency": "INR",
                "incurred_date": "2026-09-08",
                "category": "travel",
                "purpose": "Customer architecture workshop",
                "receipt_present": True,
            },
        )
        response.raise_for_status()
        expense = response.json()

        isolated = client.get(
            f"/expenses/{expense['id']}", headers=headers("employee@globex.test")
        )
        assert isolated.status_code == 404, isolated.text

        deadline = time.monotonic() + 15
        while expense["state"] != "AWAITING_REVIEW" and time.monotonic() < deadline:
            time.sleep(0.5)
            expense_response = client.get(
                f"/expenses/{expense['id']}", headers=headers("reviewer@acme.test")
            )
            expense_response.raise_for_status()
            expense = expense_response.json()
        assert expense["state"] == "AWAITING_REVIEW", expense
        assert expense["recommendation"] == "APPROVE_RECOMMENDED", expense

        decision = client.post(
            f"/expenses/{expense['id']}/decisions",
            headers=headers("reviewer@acme.test", idempotent=True),
            json={"action": "APPROVE", "reason": "", "expected_row_version": expense["row_version"]},
        )
        decision.raise_for_status()
        assert decision.json()["expense"]["state"] == "APPROVED"

        audit = client.get("/audit-events", headers=headers("auditor@acme.test"))
        audit.raise_for_status()
        assert audit.json()["chain_valid"] is True
        print(f"smoke passed: expense={expense['id']} audit_chain=valid")


if __name__ == "__main__":
    main()

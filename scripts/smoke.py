"""Exercise the deployed receipt-to-accounting workflow with synthetic data."""

import io
import time
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import httpx
from PIL import Image, ImageDraw, ImageFont

BASE_URL = "http://localhost:8000/api/v1"


def headers(identity: str, *, idempotent: bool = False) -> dict[str, str]:
    result = {"X-Demo-User": identity, "X-Correlation-ID": f"smoke-{uuid4()}"}
    if idempotent:
        result["Idempotency-Key"] = str(uuid4())
    return result


def upload_receipt_for_audit_race(content: bytes) -> None:
    with httpx.Client(base_url=BASE_URL, timeout=15) as client:
        response = client.post(
            "/receipts",
            headers=headers("employee@acme.test"),
            files={"file": (f"concurrent-{uuid4()}.png", content, "image/png")},
        )
        response.raise_for_status()


def main() -> None:
    with httpx.Client(base_url=BASE_URL, timeout=10) as client:
        image = Image.new("RGB", (1100, 500), "white")
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default(size=36)
        draw.multiline_text(
            (40, 40),
            "Synthetic Conference Hotel\nInvoice\nDate: 15/09/2026\nGrand Total INR 2,250.00",
            fill="black",
            spacing=25,
            font=font,
        )
        receipt_bytes = io.BytesIO()
        image.save(receipt_bytes, format="PNG")
        receipt = client.post(
            "/receipts",
            headers=headers("employee@acme.test"),
            files={
                "file": ("synthetic-receipt.png", receipt_bytes.getvalue(), "image/png")
            },
        )
        receipt.raise_for_status()
        receipt_data = receipt.json()
        assert receipt_data["extraction_status"] == "EXTRACTED", receipt_data
        isolated_receipt = client.get(
            f"/receipts/{receipt_data['id']}/content",
            headers=headers("employee@globex.test"),
        )
        assert isolated_receipt.status_code == 404, isolated_receipt.text

        submission_key = str(uuid4())
        payload = {
            "merchant": receipt_data["extracted_merchant"],
            "amount_minor": receipt_data["extracted_amount_minor"],
            "currency": "INR",
            "incurred_date": receipt_data["extracted_date"],
            "category": "travel",
            "purpose": "Customer architecture workshop",
            "receipt_id": receipt_data["id"],
        }
        response = client.post(
            "/expenses",
            headers={
                **headers("employee@acme.test"),
                "Idempotency-Key": submission_key,
            },
            json=payload,
        )
        response.raise_for_status()
        expense = response.json()
        changed_replay = client.post(
            "/expenses",
            headers={
                **headers("employee@acme.test"),
                "Idempotency-Key": submission_key,
            },
            json={**payload, "amount_minor": 999_00},
        )
        assert changed_replay.status_code == 409, changed_replay.text

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

        unauthorized_decision = client.post(
            f"/expenses/{expense['id']}/decisions",
            headers=headers("employee@acme.test", idempotent=True),
            json={
                "action": "APPROVE",
                "reason": "",
                "expected_row_version": expense["row_version"],
                "requested_fields": [],
            },
        )
        assert unauthorized_decision.status_code == 403, unauthorized_decision.text

        decision = client.post(
            f"/expenses/{expense['id']}/decisions",
            headers=headers("reviewer@acme.test", idempotent=True),
            json={
                "action": "APPROVE",
                "reason": "",
                "expected_row_version": expense["row_version"],
                "requested_fields": [],
                "reviewer_active_ms": 2_500,
            },
        )
        decision.raise_for_status()
        expense = decision.json()["expense"]
        assert expense["state"] == "READY_TO_EXPORT"

        exported = client.post(
            f"/expenses/{expense['id']}/exports",
            headers=headers("reviewer@acme.test"),
            json={
                "account_code": "TRAVEL",
                "cost_center": "INDIA-SALES",
                "expected_row_version": expense["row_version"],
            },
        )
        exported.raise_for_status()
        csv_file = client.get(
            exported.json()["download_url"].removeprefix("/api/v1"),
            headers=headers("auditor@acme.test"),
        )
        csv_file.raise_for_status()
        assert expense["id"] in csv_file.text

        with ThreadPoolExecutor(max_workers=3) as executor:
            list(
                executor.map(
                    upload_receipt_for_audit_race, [receipt_bytes.getvalue()] * 3
                )
            )

        audit = client.get("/audit-events", headers=headers("auditor@acme.test"))
        audit.raise_for_status()
        assert audit.json()["chain_valid"] is True
        metrics = client.get("/metrics/product", headers=headers("auditor@acme.test"))
        metrics.raise_for_status()
        assert metrics.json()["exports_completed"] >= 1
        print(
            f"smoke passed: expense={expense['id']} receipt=extracted export=csv audit=valid"
        )


if __name__ == "__main__":
    main()

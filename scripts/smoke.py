"""Exercise the deployed receipt-to-accounting workflow with synthetic data."""

import io
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from uuid import uuid4

import httpx
from PIL import Image, ImageDraw, ImageFont

BASE_URL = "http://localhost:8000/api/v1"
READY_URL = "http://localhost:8000/health/ready"


def wait_until_ready(timeout_seconds: float = 180) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            response = httpx.get(READY_URL, timeout=2)
            response.raise_for_status()
            return
        except (httpx.HTTPError, OSError) as exc:
            last_error = exc
            time.sleep(1)
    raise RuntimeError(f"API did not become ready within {timeout_seconds}s") from last_error


def headers(identity: str, *, idempotent: bool = False) -> dict[str, str]:
    result = {"X-Demo-User": identity, "X-Correlation-ID": f"smoke-{uuid4()}"}
    if idempotent:
        result["Idempotency-Key"] = str(uuid4())
    return result


def view_receipt_for_audit_race(receipt_id: str) -> None:
    with httpx.Client(base_url=BASE_URL, timeout=60) as client:
        response = client.get(
            f"/receipts/{receipt_id}/content",
            headers=headers("employee@acme.test"),
        )
        response.raise_for_status()


def synthetic_receipt(merchant: str, amount: str) -> bytes:
    image = Image.new("RGB", (1100, 500), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=36)
    draw.multiline_text(
        (40, 40),
        f"{merchant}\nBusiness travel receipt\nDate: 15/09/2026\nGrand Total INR {amount}",
        fill="black",
        spacing=25,
        font=font,
    )
    receipt_bytes = io.BytesIO()
    image.save(receipt_bytes, format="PNG")
    return receipt_bytes.getvalue()


def upload_synthetic_receipt(file_spec: tuple[str, bytes]) -> dict[str, Any]:
    filename, content = file_spec
    with httpx.Client(base_url=BASE_URL, timeout=60) as client:
        response = client.post(
            "/receipts",
            headers=headers("employee@acme.test"),
            files={"file": (filename, content, "image/png")},
        )
        response.raise_for_status()
        return response.json()


def main() -> None:
    wait_until_ready()
    with httpx.Client(base_url=BASE_URL, timeout=60) as client:
        hotel_bytes = synthetic_receipt("Synthetic Conference Hotel", "2,250.00")
        transit_bytes = synthetic_receipt("Synthetic City Rail", "750.00")
        batch = [
            ("synthetic-hotel.png", hotel_bytes),
            ("synthetic-transit.png", transit_bytes),
        ]
        with ThreadPoolExecutor(max_workers=len(batch)) as executor:
            uploaded = list(executor.map(upload_synthetic_receipt, batch))
        for receipt_data in uploaded:
            assert receipt_data["extraction_status"] == "EXTRACTED", receipt_data
            assert receipt_data["scan_status"] == "CLEAN", receipt_data
        hotel, transit = uploaded
        isolated_receipt = client.get(
            f"/receipts/{hotel['id']}/content",
            headers=headers("employee@globex.test"),
        )
        assert isolated_receipt.status_code == 404, isolated_receipt.text

        submission_key = str(uuid4())
        payload = {
            "category": "travel",
            "purpose": "Customer architecture workshop trip",
            "items": [
                {
                    "receipt_id": item["id"],
                    "merchant": item["extracted_merchant"],
                    "amount_minor": item["extracted_amount_minor"],
                    "currency": "INR",
                    "incurred_date": item["extracted_date"],
                }
                for item in uploaded
            ],
        }
        response = client.post(
            "/expense-reports",
            headers={
                **headers("employee@acme.test"),
                "Idempotency-Key": submission_key,
            },
            json=payload,
        )
        response.raise_for_status()
        expense = response.json()
        changed_replay = client.post(
            "/expense-reports",
            headers={
                **headers("employee@acme.test"),
                "Idempotency-Key": submission_key,
            },
            json={**payload, "purpose": "Changed replay must fail"},
        )
        assert changed_replay.status_code == 409, changed_replay.text

        isolated = client.get(
            f"/expenses/{expense['id']}", headers=headers("employee@globex.test")
        )
        assert isolated.status_code == 404, isolated.text

        deadline = time.monotonic() + 45
        while expense["state"] != "AWAITING_REVIEW" and time.monotonic() < deadline:
            time.sleep(0.5)
            expense_response = client.get(
                f"/expenses/{expense['id']}", headers=headers("reviewer@acme.test")
            )
            expense_response.raise_for_status()
            expense = expense_response.json()
        assert expense["state"] == "AWAITING_REVIEW", expense
        assert expense["recommendation"] == "APPROVE_RECOMMENDED", expense
        assert expense["amount_minor"] == 300_000, expense
        assert len(expense["receipt_items"]) == 2, expense
        assert len(expense["receipt_history"]) == 2, expense
        assert all(item["is_current"] for item in expense["receipt_history"]), expense
        receipt_checks = [
            check for check in expense["checks"] if check["check_key"].startswith("receipt_match:")
        ]
        assert len(receipt_checks) == 2, expense
        assert all(check["status"] == "PASS" for check in receipt_checks), expense

        information_request = client.post(
            f"/expenses/{expense['id']}/decisions",
            headers=headers("reviewer@acme.test", idempotent=True),
            json={
                "action": "REQUEST_INFORMATION",
                "reason": "Please add the missed airport transfer receipt.",
                "expected_row_version": expense["row_version"],
                "requested_fields": ["receipt"],
            },
        )
        information_request.raise_for_status()
        expense = information_request.json()["expense"]
        assert expense["state"] == "INFORMATION_REQUESTED", expense

        additional_bytes = synthetic_receipt("Synthetic Airport Taxi", "250.00")
        additional = client.post(
            "/receipts",
            headers=headers("employee@acme.test"),
            files={
                "file": (
                    "synthetic-airport-taxi.png",
                    additional_bytes,
                    "image/png",
                )
            },
        )
        additional.raise_for_status()
        additional_data = additional.json()
        assert additional_data["scan_status"] == "CLEAN", additional_data
        resubmission = client.post(
            f"/expenses/{expense['id']}/resubmissions",
            headers=headers("employee@acme.test"),
            json={
                "purpose": "Customer architecture workshop (airport transfer added)",
                "items": [
                    {
                        "receipt_id": additional_data["id"],
                        "merchant": additional_data["extracted_merchant"]
                        or "Synthetic Airport Taxi",
                        "amount_minor": additional_data["extracted_amount_minor"],
                        "currency": "INR",
                        "incurred_date": additional_data["extracted_date"],
                    },
                ],
            },
        )
        assert resubmission.is_success, resubmission.text
        expense = resubmission.json()
        deadline = time.monotonic() + 45
        while expense["state"] != "AWAITING_REVIEW" and time.monotonic() < deadline:
            time.sleep(0.5)
            expense_response = client.get(
                f"/expenses/{expense['id']}", headers=headers("reviewer@acme.test")
            )
            expense_response.raise_for_status()
            expense = expense_response.json()
        assert expense["state"] == "AWAITING_REVIEW", expense
        assert expense["revision"] == 2, expense
        assert expense["amount_minor"] == 325_000, expense
        assert len(expense["receipt_history"]) == 5, expense
        assert sum(item["is_current"] for item in expense["receipt_history"]) == 3, expense
        assert [item["receipt_id"] for item in expense["receipt_items"]] == [
            hotel["id"],
            transit["id"],
            additional_data["id"],
        ]

        eicar = (
            b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
        )
        infected_file = (
            b"%PDF-1.4\n1 0 obj\n<< /Type /EmbeddedFile /Length 68 >>\nstream\n"
            + eicar
            + b"\nendstream\nendobj\n%%EOF\n"
        )
        infected = client.post(
            "/receipts",
            headers=headers("employee@acme.test"),
            files={"file": ("eicar-test.pdf", infected_file, "application/pdf")},
        )
        infected.raise_for_status()
        infected_data = infected.json()
        assert infected_data["scan_status"] == "INFECTED", infected_data
        blocked_download = client.get(
            f"/receipts/{infected_data['id']}/content",
            headers=headers("employee@acme.test"),
        )
        assert blocked_download.status_code == 423, blocked_download.text

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
        assert hotel["id"] in csv_file.text
        assert transit["id"] in csv_file.text
        assert additional_data["id"] in csv_file.text
        assert len(csv_file.text.strip().splitlines()) == 4, csv_file.text

        with ThreadPoolExecutor(max_workers=3) as executor:
            list(
                executor.map(
                    view_receipt_for_audit_race, [additional_data["id"]] * 3
                )
            )

        audit = client.get("/audit-events", headers=headers("auditor@acme.test"))
        audit.raise_for_status()
        assert audit.json()["chain_valid"] is True
        metrics = client.get("/metrics/product", headers=headers("auditor@acme.test"))
        metrics.raise_for_status()
        assert metrics.json()["exports_completed"] >= 1
        print(
            f"smoke passed: expense={expense['id']} report=3-lines append=preserved "
            "malware=blocked export=3-line-csv audit=valid"
        )


if __name__ == "__main__":
    main()

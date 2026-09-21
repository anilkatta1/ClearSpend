from datetime import date

from app.receipts import extract_receipt_fields


def test_extracts_editable_fields_from_receipt_text() -> None:
    extracted = extract_receipt_fields(
        "Synthetic Conference Hotel\nInvoice\nDate: 08/09/2026\nGrand Total INR 2,250.00"
    )
    assert extracted.merchant == "Synthetic Conference Hotel"
    assert extracted.incurred_date == date(2026, 9, 8)
    assert extracted.amount_minor == 225_000
    assert extracted.currency == "INR"
    assert extracted.status == "EXTRACTED"


def test_taxi_merchant_is_not_misclassified_as_a_tax_label() -> None:
    extracted = extract_receipt_fields(
        "Synthetic Airport Taxi\nReceipt\nDate: 15/09/2026\nGrand Total INR 250.00"
    )

    assert extracted.merchant == "Synthetic Airport Taxi"
    assert extracted.status == "EXTRACTED"

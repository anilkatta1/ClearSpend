import io
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, ConfigDict

ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_RECEIPT_BYTES = 5 * 1024 * 1024


class ReceiptError(ValueError):
    pass


class ExtractedReceipt(BaseModel):
    model_config = ConfigDict(frozen=True)
    status: str
    merchant: str | None = None
    incurred_date: date | None = None
    amount_minor: int | None = None
    currency: str | None = None
    text: str = ""


def validate_receipt(content: bytes, content_type: str) -> None:
    if content_type not in ALLOWED_TYPES:
        raise ReceiptError("Only JPEG, PNG, and PDF receipts are accepted")
    if not content or len(content) > MAX_RECEIPT_BYTES:
        raise ReceiptError("Receipt must be between 1 byte and 5 MB")
    signatures = {
        "image/jpeg": content.startswith(b"\xff\xd8\xff"),
        "image/png": content.startswith(b"\x89PNG\r\n\x1a\n"),
        "application/pdf": content.startswith(b"%PDF-"),
    }
    if not signatures[content_type]:
        raise ReceiptError("Receipt content does not match its declared type")


def receipt_text(content: bytes, content_type: str) -> str:
    validate_receipt(content, content_type)
    if content_type == "application/pdf":
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)[:20_000]

    import pytesseract  # type: ignore[import-untyped]
    from PIL import Image

    with Image.open(io.BytesIO(content)) as image:
        return pytesseract.image_to_string(image)[:20_000]


def extract_receipt_fields(text: str) -> ExtractedReceipt:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    amount_match = re.search(
        r"(?i)(?:grand\s+total|total|amount)(?:\s+due)?\s*[:\-]?\s*"
        r"(?:(INR|Rs\.?|₹)\s*)?([0-9][0-9,]*(?:\.\d{1,2})?)",
        text,
    )
    date_match = re.search(
        r"(?i)(?:date\s*[:\-]?\s*)?"
        r"(\d{4}-\d{1,2}-\d{1,2}|\d{1,2}[/-]\d{1,2}[/-]\d{4})",
        text,
    )
    merchant = next(
        (
            line[:160]
            for line in lines
            if not re.search(r"(?i)invoice|receipt|tax|gst|date|total|amount", line)
        ),
        None,
    )
    amount_minor = None
    if amount_match:
        try:
            amount_minor = int(
                (Decimal(amount_match.group(2).replace(",", "")) * 100).quantize(Decimal("1"))
            )
        except InvalidOperation:
            amount_minor = None
    incurred_date = None
    if date_match:
        raw = date_match.group(1)
        for pattern in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                incurred_date = datetime.strptime(raw, pattern).date()
                break
            except ValueError:
                continue
    complete = merchant is not None and incurred_date is not None and amount_minor is not None
    return ExtractedReceipt(
        status="EXTRACTED" if complete else "UNREADABLE",
        merchant=merchant,
        incurred_date=incurred_date,
        amount_minor=amount_minor,
        currency="INR" if amount_match else None,
        text=text,
    )


def extract_receipt(content: bytes, content_type: str) -> ExtractedReceipt:
    try:
        return extract_receipt_fields(receipt_text(content, content_type))
    except Exception:
        return ExtractedReceipt(status="UNREADABLE")

import io
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, cast

from pydantic import BaseModel, ConfigDict

ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_RECEIPT_BYTES = 5 * 1024 * 1024
MAX_IMAGE_PIXELS = 25_000_000
MAX_PDF_PAGES = 20


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


def _contains_prohibited_pdf_entry(
    value: Any,
    *,
    seen: set[int] | None = None,
    depth: int = 0,
) -> bool:
    """Resolve the PDF object graph and fail safely on active-content entries."""
    if depth > 30:
        raise ReceiptError("PDF object graph is too deeply nested")
    try:
        resolved = value.get_object()
    except AttributeError:
        resolved = value
    seen = seen if seen is not None else set()
    marker = id(resolved)
    if marker in seen:
        return False
    seen.add(marker)
    prohibited = {"/OpenAction", "/AA", "/JavaScript", "/JS", "/EmbeddedFiles"}
    if isinstance(resolved, dict):
        return any(
            str(key) in prohibited
            or _contains_prohibited_pdf_entry(child, seen=seen, depth=depth + 1)
            for key, child in resolved.items()
        )
    if isinstance(resolved, (list, tuple)):
        return any(
            _contains_prohibited_pdf_entry(child, seen=seen, depth=depth + 1)
            for child in resolved
        )
    return False


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


def validate_safe_document(content: bytes, content_type: str) -> None:
    """Deep validation performed only after malware scanning."""
    validate_receipt(content, content_type)
    if content_type == "application/pdf":
        from pypdf import PdfReader

        try:
            reader = PdfReader(io.BytesIO(content), strict=True)
            if reader.is_encrypted:
                raise ReceiptError("Encrypted PDF receipts are not accepted")
            if len(reader.pages) > MAX_PDF_PAGES:
                raise ReceiptError(f"PDF receipts may contain at most {MAX_PDF_PAGES} pages")
            root = reader.trailer.get("/Root", {})
            if _contains_prohibited_pdf_entry(root):
                raise ReceiptError("PDF contains active or embedded content")
        except ReceiptError:
            raise
        except Exception as exc:
            raise ReceiptError("PDF structure is invalid") from exc
        return

    from PIL import Image

    try:
        with Image.open(io.BytesIO(content)) as image:
            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise ReceiptError("Receipt image dimensions are too large")
            expected = "JPEG" if content_type == "image/jpeg" else "PNG"
            if image.format != expected:
                raise ReceiptError("Receipt image format does not match its declared type")
            if getattr(image, "n_frames", 1) != 1:
                raise ReceiptError("Animated or multi-frame images are not accepted")
            image.verify()
    except ReceiptError:
        raise
    except Exception as exc:
        raise ReceiptError("Receipt image structure is invalid") from exc


def receipt_text(content: bytes, content_type: str) -> str:
    validate_safe_document(content, content_type)
    if content_type == "application/pdf":
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)[:20_000]

    import pytesseract  # type: ignore[import-untyped]
    from PIL import Image

    with Image.open(io.BytesIO(content)) as image:
        return cast(str, pytesseract.image_to_string(image))[:20_000]


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
            if not re.search(r"(?i)\b(?:invoice|receipt|tax|gst|date|total|amount)\b", line)
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

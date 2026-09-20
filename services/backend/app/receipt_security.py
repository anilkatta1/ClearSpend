import io
import re
from dataclasses import dataclass

import clamd  # type: ignore[import-untyped]

from app.config import settings
from app.receipts import ExtractedReceipt, ReceiptError, extract_receipt, validate_safe_document

PROMPT_INJECTION_PATTERNS = (
    re.compile(r"(?i)ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions?"),
    re.compile(r"(?i)(?:system|developer)\s+(?:message|prompt)"),
    re.compile(r"(?i)(?:reveal|print|return|export)\s+(?:the\s+)?(?:secret|password|token|data)"),
    re.compile(r"(?i)(?:bypass|disable|override)\s+(?:policy|security|approval|guardrails?)"),
    re.compile(r"(?i)you\s+are\s+now\s+(?:an?|the)"),
)


class MalwareScanError(RuntimeError):
    pass


@dataclass(frozen=True)
class ReceiptInspection:
    scan_status: str
    scan_result: str
    security_flags: list[str]
    extracted: ExtractedReceipt


def prompt_injection_flags(text: str) -> list[str]:
    return [
        f"PROMPT_INJECTION_PATTERN_{index}"
        for index, pattern in enumerate(PROMPT_INJECTION_PATTERNS, 1)
        if pattern.search(text)
    ]


def scan_for_malware(content: bytes) -> str:
    try:
        client = clamd.ClamdNetworkSocket(
            host=settings.clamav_host,
            port=settings.clamav_port,
            timeout=15,
        )
        if not client.ping():
            raise MalwareScanError("Malware scanner is unavailable")
        result = client.instream(io.BytesIO(content))
    except MalwareScanError:
        raise
    except Exception as exc:
        raise MalwareScanError("Malware scanner is unavailable") from exc
    status, signature = result.get("stream", ("ERROR", "missing scan result"))
    if status == "FOUND":
        return f"INFECTED:{signature or 'unknown-signature'}"
    if status != "OK":
        raise MalwareScanError(f"Malware scanner returned {status}")
    return "CLEAN"


def malware_scanner_ready() -> bool:
    try:
        return bool(
            clamd.ClamdNetworkSocket(
                host=settings.clamav_host,
                port=settings.clamav_port,
                timeout=2,
            ).ping()
        )
    except Exception:
        return False


def inspect_receipt(content: bytes, content_type: str) -> ReceiptInspection:
    scan_result = scan_for_malware(content) if settings.malware_scan_required else "CLEAN"
    if scan_result.startswith("INFECTED:"):
        return ReceiptInspection(
            scan_status="INFECTED",
            scan_result=scan_result,
            security_flags=["MALWARE_DETECTED"],
            extracted=ExtractedReceipt(status="BLOCKED"),
        )
    try:
        validate_safe_document(content, content_type)
        extracted = extract_receipt(content, content_type)
    except ReceiptError as exc:
        return ReceiptInspection(
            scan_status="REJECTED",
            scan_result=str(exc),
            security_flags=["UNSAFE_DOCUMENT_STRUCTURE"],
            extracted=ExtractedReceipt(status="BLOCKED"),
        )
    flags = prompt_injection_flags(extracted.text)
    return ReceiptInspection(
        scan_status="CLEAN",
        scan_result="CLEAN",
        security_flags=flags,
        extracted=extracted,
    )

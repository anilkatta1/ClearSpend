import re
from collections.abc import Iterable
from datetime import date
from typing import Any

from app.domain import CheckStatus, ClaimFacts, PolicyCheck, validate_rule_params


def _check(key: str, status: CheckStatus, reason: str, section_id: str) -> PolicyCheck:
    return PolicyCheck(
        check_key=key,
        source="DETERMINISTIC",
        status=status,
        reason_code=reason,
        explanation=reason.replace("_", " ").capitalize(),
        policy_section_ids=[section_id],
    )


def evaluate_rules(
    facts: ClaimFacts, rules: Iterable[tuple[str, dict[str, Any], str]]
) -> list[PolicyCheck]:
    results: list[PolicyCheck] = []
    for index, (rule_type, params, section_id) in enumerate(rules):
        validate_rule_params(rule_type, params)
        key = f"{rule_type}:{index}"
        if rule_type == "receipt_required":
            if facts.currency != str(params.get("currency", "INR")):
                results.append(_check(key, CheckStatus.UNKNOWN, "CURRENCY_MISMATCH", section_id))
                continue
            required = facts.amount_minor >= int(params["threshold_minor"])
            status = (
                CheckStatus.FAIL if required and not facts.receipt_present else CheckStatus.PASS
            )
            results.append(
                _check(
                    key,
                    status,
                    "RECEIPT_MISSING" if status == CheckStatus.FAIL else "RECEIPT_OK",
                    section_id,
                )
            )
        elif rule_type == "amount_limit":
            if facts.currency != str(params.get("currency", "INR")):
                results.append(_check(key, CheckStatus.UNKNOWN, "CURRENCY_MISMATCH", section_id))
                continue
            passed = facts.amount_minor <= int(params["limit_minor"])
            results.append(
                _check(
                    key,
                    CheckStatus.PASS if passed else CheckStatus.FAIL,
                    "AMOUNT_WITHIN_LIMIT" if passed else "AMOUNT_LIMIT_EXCEEDED",
                    section_id,
                )
            )
        elif rule_type == "prohibited_category":
            prohibited = {str(value).lower() for value in params["categories"]}
            passed = facts.category.lower() not in prohibited
            results.append(
                _check(
                    key,
                    CheckStatus.PASS if passed else CheckStatus.FAIL,
                    "CATEGORY_ALLOWED" if passed else "CATEGORY_PROHIBITED",
                    section_id,
                )
            )
        elif rule_type == "business_purpose_required":
            passed = bool(facts.purpose.strip())
            results.append(
                _check(
                    key,
                    CheckStatus.PASS if passed else CheckStatus.FAIL,
                    "PURPOSE_PRESENT" if passed else "PURPOSE_MISSING",
                    section_id,
                )
            )
        elif rule_type == "submission_window":
            age = (facts.submitted_date - facts.incurred_date).days
            passed = 0 <= age <= int(params["days"])
            results.append(
                _check(
                    key,
                    CheckStatus.PASS if passed else CheckStatus.FAIL,
                    "WITHIN_SUBMISSION_WINDOW" if passed else "SUBMISSION_TOO_LATE",
                    section_id,
                )
            )
    return results


def evaluate_receipt_match(
    facts: ClaimFacts,
    *,
    extracted_amount_minor: int | None,
    extracted_currency: str | None,
    extracted_merchant: str | None,
    extracted_date: date | None,
    extraction_status: str,
    section_id: str,
) -> PolicyCheck:
    if extraction_status != "EXTRACTED":
        return _check("receipt_match", CheckStatus.UNKNOWN, "RECEIPT_UNREADABLE", section_id)
    if extracted_currency != facts.currency:
        return _check("receipt_match", CheckStatus.UNKNOWN, "RECEIPT_CURRENCY_MISMATCH", section_id)
    if extracted_amount_minor != facts.amount_minor:
        return _check("receipt_match", CheckStatus.UNKNOWN, "RECEIPT_AMOUNT_MISMATCH", section_id)
    if extracted_date != facts.incurred_date:
        return _check("receipt_match", CheckStatus.UNKNOWN, "RECEIPT_DATE_MISMATCH", section_id)
    normalized_claim = re.sub(r"\W+", "", facts.merchant).lower()
    normalized_receipt = re.sub(r"\W+", "", extracted_merchant or "").lower()
    if not normalized_receipt or not (
        normalized_claim in normalized_receipt or normalized_receipt in normalized_claim
    ):
        return _check("receipt_match", CheckStatus.UNKNOWN, "RECEIPT_MERCHANT_MISMATCH", section_id)
    return _check("receipt_match", CheckStatus.PASS, "RECEIPT_MATCHED", section_id)

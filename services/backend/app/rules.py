from collections.abc import Iterable
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

from datetime import date
from pathlib import Path
from typing import Any, cast

import pytest
import yaml

from app.domain import ClaimFacts, Recommendation
from app.graph import assess_claim

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
MANIFEST_PATH = REPOSITORY_ROOT / "evals" / "manifest.yaml"
CASES_DIRECTORY = REPOSITORY_ROOT / "evals" / "cases"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        return cast(dict[str, Any], yaml.safe_load(stream))


MANIFEST = load_yaml(MANIFEST_PATH)
CASE_PATHS = sorted(CASES_DIRECTORY.glob("*.yaml"))


def test_release_manifest_has_exactly_the_required_case_corpus() -> None:
    required_ids = set(MANIFEST["required_case_ids"])
    available_ids = {load_yaml(path)["id"] for path in CASE_PATHS}
    assert available_ids == required_ids
    assert len(available_ids) >= 4


@pytest.mark.parametrize("case_path", CASE_PATHS, ids=lambda path: path.stem)
def test_deterministic_release_case(case_path: Path) -> None:
    case = load_yaml(case_path)
    facts_data = case["facts"]
    facts = ClaimFacts(
        amount_minor=facts_data["amount_minor"],
        currency=facts_data["currency"],
        category=facts_data["category"],
        merchant=facts_data["merchant"],
        purpose=facts_data["purpose"],
        incurred_date=date.fromisoformat(str(facts_data["incurred_date"])),
        submitted_date=date.fromisoformat(str(facts_data["submitted_date"])),
        receipt_present=facts_data["receipt_present"],
    )
    rules = [
        (rule["type"], rule["params"], rule["section_id"])
        for rule in case["rules"]
    ]

    result = assess_claim(facts, rules)

    assert result["recommendation"] == Recommendation(case["expected_recommendation"])
    if result["recommendation"] == Recommendation.REJECT:
        assert any(check.source == "DETERMINISTIC" for check in result["checks"])

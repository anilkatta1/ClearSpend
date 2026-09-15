from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain import DecisionAction


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RuleIn(StrictModel):
    rule_type: str
    params: dict[str, Any]
    priority: int = 100


class SectionIn(StrictModel):
    section_key: str = Field(min_length=1, max_length=80)
    title: str = Field(min_length=1, max_length=160)
    source_text: str = Field(min_length=1, max_length=5000)
    rules: list[RuleIn] = Field(min_length=1, max_length=20)


class PolicyDraftIn(StrictModel):
    title: str = Field(min_length=1, max_length=160)
    sections: list[SectionIn] = Field(min_length=1, max_length=30)


class ExpenseIn(StrictModel):
    merchant: str = Field(min_length=1, max_length=160)
    amount_minor: int = Field(gt=0, le=100_000_000)
    currency: Literal["INR"] = "INR"
    incurred_date: date
    category: str = Field(min_length=1, max_length=80)
    purpose: str = Field(max_length=500)
    receipt_id: str = Field(min_length=36, max_length=36)


class DecisionIn(StrictModel):
    action: DecisionAction
    reason: str = Field(default="", max_length=500)
    expected_row_version: int = Field(gt=0)
    requested_fields: list[Literal["purpose", "receipt"]] = Field(default_factory=list)
    reviewer_active_ms: int | None = Field(default=None, ge=0, le=3_600_000)

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str) -> str:
        return value.strip()


class ResubmissionIn(StrictModel):
    purpose: str = Field(min_length=1, max_length=500)
    receipt_id: str | None = Field(default=None, min_length=36, max_length=36)


class ExportIn(StrictModel):
    account_code: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9._-]+$")
    cost_center: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9 ._-]+$")
    expected_row_version: int = Field(gt=0)


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    merchant: str
    amount_minor: int
    currency: str
    incurred_date: date
    category: str
    purpose: str
    state: str
    row_version: int
    revision: int
    receipt_present: bool
    created_at: datetime
    recommendation: str | None = None
    checks: list[dict[str, Any]] = Field(default_factory=list)


class Problem(StrictModel):
    type: str
    title: str
    status: int
    code: str
    correlationId: str
    detail: str

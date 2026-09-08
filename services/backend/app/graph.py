from typing import Any, TypedDict, cast

from langgraph.graph import END, START, StateGraph

from app.ai import AIProvider, AssessmentAIInput, FakeAIProvider, OpenAIProvider, ai_check
from app.config import settings
from app.domain import ClaimFacts, PolicyCheck, Recommendation, aggregate_recommendation
from app.rules import evaluate_rules


class AssessmentState(TypedDict, total=False):
    facts: ClaimFacts
    rules: list[tuple[str, dict[str, Any], str]]
    checks: list[PolicyCheck]
    section_ids: list[str]
    technical_failure: bool
    recommendation: Recommendation
    provider: str
    model: str | None


def load_context(state: AssessmentState) -> AssessmentState:
    section_ids = list(dict.fromkeys(rule[2] for rule in state["rules"]))
    return {"section_ids": section_ids, "technical_failure": False}


def run_rules(state: AssessmentState) -> AssessmentState:
    return {"checks": evaluate_rules(state["facts"], state["rules"])}


def semantic_needed(state: AssessmentState) -> str:
    return "aggregate" if any(check.status == "FAIL" for check in state["checks"]) else "semantic"


def run_semantic(state: AssessmentState) -> AssessmentState:
    facts = state["facts"]
    provider: AIProvider
    if settings.ai_provider == "openai" and settings.openai_api_key:
        provider = OpenAIProvider()
    else:
        provider = FakeAIProvider()
    result = provider.assess(
        AssessmentAIInput(
            merchant=facts.merchant,
            category=facts.category,
            purpose=facts.purpose,
            supplied_section_ids=state["section_ids"],
        ),
        timeout_seconds=5,
    )
    if result.kind != "success" or result.value is None:
        return {"technical_failure": True, "provider": result.provider, "model": result.model}
    return {
        "checks": [*state["checks"], ai_check(result.value)],
        "provider": result.provider,
        "model": result.model,
    }


def aggregate(state: AssessmentState) -> AssessmentState:
    return {
        "recommendation": aggregate_recommendation(
            state["checks"], technical_failure=state.get("technical_failure", False)
        )
    }


builder = StateGraph(AssessmentState)
builder.add_node("load_context", load_context)
builder.add_node("run_deterministic_rules", run_rules)
builder.add_node("semantic_policy_assessment", run_semantic)
builder.add_node("aggregate_recommendation", aggregate)
builder.add_edge(START, "load_context")
builder.add_edge("load_context", "run_deterministic_rules")
builder.add_conditional_edges(
    "run_deterministic_rules",
    semantic_needed,
    {"semantic": "semantic_policy_assessment", "aggregate": "aggregate_recommendation"},
)
builder.add_edge("semantic_policy_assessment", "aggregate_recommendation")
builder.add_edge("aggregate_recommendation", END)
assessment_graph = builder.compile()


def assess_claim(
    facts: ClaimFacts, rules: list[tuple[str, dict[str, Any], str]]
) -> AssessmentState:
    return cast(
        AssessmentState,
        assessment_graph.invoke({"facts": facts, "rules": rules, "checks": []}),
    )

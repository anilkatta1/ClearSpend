# ADR 0002: Deterministic rules own facts; humans own final decisions

- Status: accepted
- Date: 2026-09-08

## Context

Expense decisions affect money and require consistent, explainable enforcement. A language model is probabilistic and its input may contain adversarial instructions.

## Decision

Run allowlisted deterministic rules first. LangGraph may add a bounded semantic check, but it cannot approve, reject, publish policy, or mutate an expense. The aggregation function fails closed to `REVIEW_RECOMMENDED` on unknown results or technical failure. An authorized reviewer makes the final decision and must explain overrides.

## Consequences

The system remains usable without an AI provider and every recommendation is decomposable into checks and cited policy section IDs. Semantic recall must be measured before enabling a live provider.


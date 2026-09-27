# AI collaboration disclosure

## Use in this implementation

OpenAI Codex assisted with repository inspection, architecture synthesis, code generation, documentation, and test execution. The accountable engineer remains responsible for reviewing, understanding, and accepting every change.

Material AI-assisted areas include:

- FastAPI, SQLAlchemy, Alembic, and Procrastinate scaffolding;
- deterministic policy domain and LangGraph workflow implementation;
- Next.js demonstration interface;
- Docker Compose, CI, tests, ADRs, threat model, and runbook;
- diagnosis of dependency, lint, container import-path, and worker enqueue issues.

## Verification and rejected suggestions

Generated work was checked using strict mypy, Ruff, Pytest/Hypothesis, ESLint, TypeScript, Vitest, a Next.js production build, container image builds, health checks, and a live synthetic end-to-end test. Corrections made during verification included replacing unsupported Procrastinate defer arguments, removing nested event-loop execution, pinning an ESLint-compatible major version, carrying pnpm's build allowlist into Docker, setting the backend container import path, and adding outbox recovery.

The design rejects autonomous AI decisions, AI write tools, model-only policy enforcement, Redis/Kafka for the MVP, and production claims based on synthetic evidence.

## Prashant Chouksey — interview documentation

**Contributor:** Prashant Chouksey. **Consolidated:** 27 September 2026. The original disclosure's declaration date was not recorded; this consolidation date does not replace it.

Prashant's source disclosure states that he supplied the interview insights, process steps, approval rules and exception-handling context for operations expenses, IT procurement and relocation reimbursement. AI assisted with organization, Markdown formatting, language refinement and consistency checks. The source states that Prashant reviewed the resulting documents for accuracy and retained responsibility for the domain facts. These are contributor-reported statements, not independent authentication of the interviews or a new signature on his behalf.

The anonymized research is maintained in [INT-03](interviews/INT-03-head-of-operations.md), [INT-04](interviews/INT-04-it-head.md) and [INT-05](interviews/INT-05-relocation-stakeholder.md). Recommendations and their boundaries are in [research insights](interviews/research-insights.md#prashants-research-to-product-recommendations); attribution and the PM responsibility split are in [Prashant's role evidence](../ROLE_EVIDENCE_Prashant_Chouksey.md).

AI assistance with documents does not establish that the application implements the described stakeholder processes, that the participants evaluated ClearSpend, or that customer outcomes were measured. No new interviews, consent records, measured savings or purchase commitments were generated during consolidation.

Prashant subsequently confirmed using `gpt-5.6-terra`, `gpt-5.5`, `gpt-5.6-sol`, Gemini 3.1 and Grok for different project tasks. The [model-level spend log](evidence/prashant-ai-spend-log.md) follows Diya's table format and records these as contributor-reported use, not billing-verified usage. Task-to-model allocation, the exact Gemini variant, Grok version and their access tools remain unrecorded.

At Prashant's request, the log also includes an illustrative PM-workload estimate of 84 requests and 286,800 input-plus-output tokens, with per-model assumptions and calculations. These are hypothetical planning values, not measured usage, billing evidence or a whole-team total. Actual token counts and costs remain unknown.

The original interview-writing tool/model identifiers, token counts and billed spend are not recorded in the supplied disclosure. They remain unknown, not zero. OpenAI Codex assisted with this documentation consolidation; its billed cost and token counts are not available in the repository. Verification for this change covers content preservation, attribution, document links and removal of obsolete references; it does not add a new application-test or live-demo result.

## Spend

- Product runtime AI spend during the verified demo: **USD 0.00** (`AI_PROVIDER=fake`).
- Prashant's development/tool AI spend: **unknown; billing evidence not supplied**. Known activities, usage fields and reconciliation requirements are recorded in [Prashant's AI spend log](evidence/prashant-ai-spend-log.md). Unknown is not zero.
- Diya's Codex development spend: **USD 16.7903** (reported account-usage total; details in [`docs/evidence/diya-ai-spend-log.md`](evidence/diya-ai-spend-log.md)).
- Local compute and engineering time are not included in the USD figure and must not be represented as zero total cost.

Before final submission, add the actual model/tool identifiers, available token counts, and billed AI amount from the team account.

# Anil AI spend log

- **Recorded:** 2026-09-27 (IST)
- **Owner:** Anil Katta
- **Source:** local Codex session token counters under `~/.codex/sessions/2026`
- **Scope:** sessions whose recorded working directory is the ClearSpend `Assignment-3` workspace
- **Currency:** USD
- **Evidence type:** reconstructed estimate, not an account invoice

## Exact locally recorded usage

The local Codex event logs expose cumulative token counters but do not expose billed cost. In these counters, cached input is a subset of input tokens and is not added again when calculating total tokens.

| Usage class | Sessions | Models recorded | Input tokens | Cached-input subset | Output tokens | Total tokens |
|---|---:|---|---:|---:|---:|---:|
| Anil-directed Codex sessions | 2 | Predominantly `gpt-5.6-sol`; one auxiliary session also records `gpt-5.6-terra` | 149,403,779 | 144,990,976 | 518,080 | 149,921,859 |
| Project-scoped automated review sessions | 4 | `codex-auto-review` | 51,374,883 | 48,484,352 | 32,947 | 51,407,830 |
| **Inclusive local total** | **6** |  | **200,778,662** | **193,475,328** | **551,027** | **201,329,689** |

## Cost-estimation method

No provider invoice or per-session cost field was available locally. The estimate therefore uses the effective blended rate in Diya's supplied `gpt-5.6-sol` usage report:

```text
Observed proxy rate = USD 2.8641 / 3,084,158 tokens
                    = USD 0.9286489 per million tokens
```

This is an empirical project proxy, not a claim about published provider pricing. It is applied to total locally recorded tokens because the local logs do not provide a model-by-model billed-cost breakdown.

| Estimate | Calculation | Estimated cost |
|---|---|---:|
| Interactive lower estimate | 149,921,859 tokens × proxy rate | **USD 139.2248** |
| Automated-review allowance | 51,407,830 tokens × proxy rate | **USD 47.7398** |
| **Anil inclusive estimate** | 201,329,689 tokens × proxy rate | **USD 186.9646** |

The submission uses the inclusive estimate so project-scoped automated review is not silently omitted. A reasonable reconstructed range is **USD 139.2248–186.9646**, depending on whether automated-review traffic was separately billed at a comparable rate.

## Known documented subtotal

| Contributor/runtime | Basis | Amount |
|---|---|---:|
| Product runtime | Verified fake provider | USD 0.0000 |
| Diya Mondal | Reported account-usage total | USD 16.7903 |
| Anil Katta | Inclusive reconstructed estimate | USD 186.9646 |
| **Current documented subtotal** |  | **USD 203.7549** |

Prashant Chouksey has since declared AI tool use but has not supplied a billed amount; Niraj Gupta's AI usage declaration was not present when this log was prepared. Neither unknown amount is assumed to be zero. The team-wide final total must add any amounts they report.

## Limitations

- Local counters are usage telemetry, not billing records.
- The proxy rate comes from another contributor's observed model/account mix.
- One auxiliary session used a mixed `gpt-5.6-sol`/`gpt-5.6-terra` model history that cannot be separated from the cumulative session counter.
- `codex-auto-review` billing behavior is not exposed locally.
- Any ClearSpend work performed from a differently named working directory or another account/device is outside this reconstruction.

If an account usage export becomes available, replace the estimated dollar amount with the billed amount while retaining this methodology as verification history.

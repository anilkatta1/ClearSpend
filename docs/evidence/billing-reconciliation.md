# AI billing reconciliation

The current submission uses the workspace's reported Niraj total of **USD 23.47** and
its [supplied breakdown](niraj-ai-spend-log.md). That is a reported individual figure,
not a verified complete assignment total. Publication of community posts does not change
the billing evidence.

| Source | Recorded amount | Treatment |
|---|---:|---|
| Current workspace Niraj spend log | USD 23.47 | Retained as the canonical reported amount pending billing confirmation. |
| Earlier `ClearSpend_Niraj_Gupta_RECONCILED_v2_DRAFT.zip`, Niraj spend log | USD 24.5081 | Conflicting reported amount. The interval and reason for the difference are unknown; do not add it to USD 23.47. |
| Same earlier ZIP, Diya spend log | USD 16.7903 | Historical reported amount with a usage table in that archive. Attribution, period and overlap have not been reconfirmed; it is not silently promoted into the current team total. |
| Prashant, Anil and additional tool/remediation costs | Unknown | Contributor confirmation required; unknown does not mean zero. |
| Synthetic runtime using the fake provider | USD 0.00 | Runtime model calls only; excludes development tools, compute and labor. |

Ask each contributor for the tool/provider, billing interval, currency, amount and whether
charges are personal or shared. Record whether subscription costs are full or allocated
and the allocation method. Count overlapping account charges once. A final team total
cannot currently be computed from non-overlapping, confirmed charges.

Retain only non-sensitive usage totals. Do not include credentials, account IDs or raw
personal invoices in the submission. Older ZIPs remain local reference copies; submit
only the newly rebuilt package after reviewing its remaining evidence limitations.

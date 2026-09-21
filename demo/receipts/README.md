# Synthetic demo receipts

These files contain synthetic data only and are safe to use for the ClearSpend local demo.

| File | Extracted merchant | Date | Amount |
|---|---|---|---:|
| `Hotel_Receipt.pdf` | Synthetic Conference Hotel | 2026-09-15 | INR 2,250.00 |
| `Train_Receipt.pdf` | Synthetic City Rail | 2026-09-15 | INR 750.00 |
| `Taxi_Receipt.pdf` | Synthetic Airport Taxi | 2026-09-15 | INR 250.00 |

## Recommended UI walkthrough

1. Sign in as the demo Employee and upload `Hotel_Receipt.pdf` and `Train_Receipt.pdf` together.
2. Confirm the extracted merchant, date, and amount for both lines, then submit the travel report.
3. As the Reviewer, inspect both receipts and request the missing airport-transfer receipt.
4. As the Employee, upload only `Taxi_Receipt.pdf` from the report's **Action Required** panel and resubmit.
5. As the Reviewer, verify that all three receipts are present, make a decision, and complete the accounting export.

For the clean-match path, leave the extracted values unchanged. To demonstrate a control failure, change a claimed amount, date, or merchant before submitting. The upload still succeeds, but the deterministic receipt-matching check records the corresponding mismatch and routes the report for human review.


# ClearSpend live-demo narrative

> **Use with:** the synthetic files in [`receipts/`](receipts/) and the screenshots in [`images/`](images/).
>
> **Demo boundary:** ClearSpend supports reimbursement review and an accounting handoff. It does **not** make payments or move money.

## Opening — the problem

“Expense reimbursement should not be a choice between slow manual review and opaque automation. ClearSpend turns the receipts from one business trip into one reviewable, auditable approval, while keeping the final decision with a human.”

## 1. Employee: submit one trip, not disconnected receipts

**Show:** [`images/assets1.png`](images/assets1.png), or the empty submission form.

“An employee starts with a shared category and a business purpose: here, travel for a Bangalore client visit. They can upload up to 20 receipts for the same trip.”

**Action:** Upload `Hotel_Receipt.pdf` and `Train_Receipt.pdf`.

“Before extraction, ClearSpend scans uploaded files for malware. Clean receipts are stored encrypted and then made available for review.”

## 2. Verify the evidence, line by line

**Show:** [`images/assets2.png`](images/assets2.png) and [`images/assets3.png`](images/assets3.png).

“ClearSpend extracts the merchant, amount, and date, but extraction is not silently treated as truth. The employee verifies each receipt line.”

“The demo receipts are a hotel for INR 2,250, train travel for INR 750, and an airport taxi for INR 250. The server derives the INR 3,250 total, so a client cannot assert a different aggregate.”

**Action:** Leave extracted fields unchanged and submit the report.

## 3. Human-in-the-loop: request missing evidence

**Show:** [`images/assets4.png`](images/assets4.png), or switch to the Reviewer view.

“On the review queue, the system presents a recommendation—but it is explicitly not a decision.”

**Action:** Open the submitted report and select **Request info** for the missing airport-transfer receipt.

“Instead of rejecting a legitimate trip because one receipt is missing, the reviewer requests the specific evidence required.”

**Action:** Switch back to the Employee view. From **Action Required**, upload only `Taxi_Receipt.pdf` and resubmit.

“The additional receipt is appended as new evidence. The prior evidence remains visible in the audit history; ClearSpend does not silently rewrite the record.”

## 4. Automation is bounded and explainable

**Show:** [`images/assets5.png`](images/assets5.png).

“ClearSpend runs deterministic controls first: receipt presence, claim limits, allowed category, stated purpose, submission window, and merchant, date, and amount matching for every receipt.”

“AI assistance is limited to ambiguity—for example, whether the stated business purpose is plausible under the selected policy. AI does not approve claims, change policy, or move money.”

## 5. A reviewer owns the decision

**Show:** [`images/assets6.png`](images/assets6.png).

“With all three lines present and every check visible, the reviewer can approve, reject, or request more information. The relevant reimbursement rules stay pinned on the report.”

“Automation organizes evidence and offers a recommendation. Finance retains authority for the final decision.”

**Action:** Approve the completed report.

## 6. Accounting handoff, not payment

**Show:** [`images/assets7.png`](images/assets7.png).

“After approval, the reviewer confirms the accounting code and downloads an accountant-ready CSV with one line per receipt.”

**Action:** Select **Confirm coding & export CSV**.

“This is an accounting handoff. It is explicitly not payment execution or money movement.”

## Closing — prove the workflow

**Show:** [`images/assets8.png`](images/assets8.png).

“ClearSpend also records operating signals and a hash-linked event trail. We can show submission, evidence changes, checks, decision, and export—and verify that the audit chain remains intact.”

“ClearSpend’s promise is not that AI reimburses expenses. It is that every reimbursement decision is faster to review, easier to explain, and still owned by a human.”

## Demo receipt reference

| File | Merchant | Date | Amount |
|---|---|---|---:|
| `receipts/Hotel_Receipt.pdf` | Synthetic Conference Hotel | 2026-09-15 | INR 2,250.00 |
| `receipts/Train_Receipt.pdf` | Synthetic City Rail | 2026-09-15 | INR 750.00 |
| `receipts/Taxi_Receipt.pdf` | Synthetic Airport Taxi | 2026-09-15 | INR 250.00 |

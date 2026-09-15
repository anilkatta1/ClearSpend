# ClearSpend domain glossary

| Term | Meaning |
|---|---|
| Organization | A tenant whose policies, claims, members, and audit history are isolated from every other tenant. |
| Member | A user acting in one Organization with exactly one demo role: Employee, Reviewer, Admin, or Auditor. |
| Policy Version | An immutable, published set of policy sections and typed rules captured by a claim at submission. |
| Expense Claim | An employee's reimbursement request and its revisioned workflow state. |
| Policy Check | A PASS, FAIL, or UNKNOWN evidence item produced by deterministic code or the bounded AI assessment. |
| Assessment Attempt | Append-only evidence and recommendation for one claim revision. It is not a final decision. |
| Recommendation | APPROVE_RECOMMENDED, REJECT_RECOMMENDED, or NEEDS_REVIEW; advice presented to a human reviewer. |
| Approval Decision | The final human action: approve, reject, or request information. |
| Override | A human decision that differs from the observed recommendation and therefore requires a reason. |
| Audit Event | An append-only, hash-linked record of a material domain action. |
| Receipt | Evidence uploaded before a claim; extraction proposes editable fields and never overrides employee confirmation. |
| Receipt Match | A deterministic comparison of receipt amount, currency, and merchant against the confirmed claim. An unreadable or mismatched receipt requires review. |
| Information Request | A reviewer-authored message plus explicit fields the employee must correct before reassessment. |
| Ready to Export | An approved claim awaiting human confirmation of accounting code and cost center. It is not paid. |
| Accounting Export | An idempotent accountant-ready record generated after approval and human coding confirmation. It does not move money. |

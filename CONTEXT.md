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

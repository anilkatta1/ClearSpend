# Submission remediation evidence

**Scope:** source/document remediation after the rubric review. No application, container
stack, live AI service or customer session was run for this remediation.

## Executed checks

Exact output and timestamp are retained in [regression-checks.txt](regression-checks.txt).
Changed Python files passed syntax parsing; the report helper and React page passed
TypeScript syntax transpilation. New-document relative links and pricing arithmetic were
also checked. Syntax transpilation is not a full project type check.

`make test-regressions` passes locally using Python 3.12.8 and Node 22.13.0, without
installing project dependencies. Python 3.13 remains the full application's declared runtime.

- CSV: two unittest methods pass, including 16 formula-prefix/path subcases and ordinary
  comma/quote/newline round trips. Before the fix, all 16 prefix subcases failed.
- Submission retry: three Node tests pass. The simulated server commits before dropping
  its first response; retry now reuses the key and leaves one report. The test failed with
  a fresh key per attempt. Actor/body separation and key release after success also pass.

These tests exercise the extracted production renderer and submission helper. The renderer
uses structural expense fixtures; the retry test models an idempotent server and does not
exercise React or a live API/database. Browser and full-stack verification remain unexecuted.

## Changes and boundaries

- CSV serialization is isolated in `app/accounting_csv.py`; textual formula prefixes are
  escaped without mutating stored evidence or numeric amounts.
- The report form calls `createReportSubmitter`; identical pending actor/body requests keep
  their key within the mounted page. This is not cross-reload or content-hash duplicate detection.
- Numerical pricing scenarios are explicit assumptions, not observed customer economics.
- The role file distinguishes documented accountability from personal authorship.
- The interview index records an unresolved source conflict; participant independence has
  not been guessed.
- Existing pitch/roadmap artifacts are correctly indexed. No new customer outcome, community
  post, paid commitment or billing amount is asserted.

## Release verification still required

The existing CI configuration and historical prose are not a fresh passing CI run. Run
backend quality/tests with the migrated PostgreSQL test database, frontend lint/type/test/build,
and the documented synthetic smoke before claiming the exact revised release is fully verified.
The earlier dependency installation attempt was blocked by HTTP 403; it was not a test failure.

## Package reconciliation

The subsequent review found that the latest Sales role file had been combined with an
older copy of its supporting documents and source. Thirty-three missing or older files
were restored from the previously verified draft archive after comparing their contents.
The latest standalone Niraj role file and newer evidence index were retained; the index
was updated to distinguish described external community activity from inspectable evidence.

The recovered code and tests were rerun. The packager now checks all packaged local
Markdown links and heading anchors, requires the CSV/retry implementation and test files,
and packages only the selected learner's role file. Four additional packaging regression
tests cover absent evidence, absent headings, valid relative links and external/example
links. These tests are included in `make test-regressions` and CI.

The fresh output for this reconciliation is [reconciliation-checks.txt](reconciliation-checks.txt).
Neither source restoration nor packaging supplies missing customer observations, community
posts, interview attribution or billing totals.

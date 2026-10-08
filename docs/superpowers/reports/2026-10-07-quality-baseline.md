# Quality Hardening Baseline

Recorded on 2026-10-07 before quality hardening implementation.

## Protected User Work

- `.DS_Store` is modified and must remain unstaged.
- `app/services/fragment_stars.py` is modified and must remain unstaged unless
  the user explicitly requests otherwise.
- Initial Fragment diff size: 158 insertions, 2 deletions across 160 changed
  lines.
- No files were staged when this baseline was recorded.

No configuration values, environment variables, or secrets were inspected or
copied into this report.

## Checks

| Check | Baseline result |
| --- | --- |
| `python -m unittest discover -s tests -v` | 26 tests passed |
| `python -m compileall -q app migrations scripts tests` | Passed |
| `ruff check .` | 2 E501 errors in `015_balance_topups.py` |
| `ruff format --check .` | 54 files require formatting |
| `mypy .` | 86 errors in 19 files; 321 files checked |
| `pyright` | 4 errors: 3 in Platega, 1 in Redis |

## Error Groups

The mypy baseline is dominated by 53 `no-any-return` errors in stars-order
support modules. The remaining groups are incorrect Optional annotations,
untyped vendored Platega and Telethon boundaries, implicit re-exports, one
Redis key type mismatch, and isolated assignment or return narrowing errors.

The pyright failures reproduce the same adapter-boundary problems:

- optional Platega return/failure URLs passed to a non-optional SDK signature;
- a configurable Platega API URL inferred as a string literal;
- Redis `keys()` declared as returning `bytes | str` while the repository
  requires only bytes.

## Final Result

Recorded on 2026-10-08 after the refactor and integration hardening work.

| Check | Final result |
| --- | --- |
| `python -m unittest discover -s tests -v` | 63 tests passed; 5 infrastructure tests skipped without opt-in URLs |
| `python -m compileall -q app migrations scripts tests` | Passed |
| `ruff check app tests migrations scripts` | Passed |
| `ruff format --check app tests migrations scripts` | 334 files already formatted |
| `mypy app tests migrations scripts` | Passed; 334 source files checked |
| `pyright` | 0 errors, 0 warnings |
| `make integration-test` | 17 tests passed against disposable PostgreSQL 18 and Redis 8.4 |
| `docker compose -f docker-compose.test.yml ps -a` | No remaining test containers |

The integration target applies all Alembic revisions through `018`, verifies
the database revision against the repository head, exercises Redis
serialization and wildcard deletion, checks repository status transitions and
the atomic balance top-up credit transaction, and runs payment/Telegram HTTP
boundaries in-process without contacting live provider APIs.

`StarsOrderService` retains its public facade while top-up identity, invoice,
verification, fulfillment, and webhook behavior now live in the focused
`stars_order_support.topups` module. Provider adapters and support
collaborators have precise type boundaries instead of leaking `Any` through
the orchestration layer.

The protected `.DS_Store` and `app/services/fragment_stars.py` changes remain
unstaged and are absent from every hardening commit. The Fragment file remains
part of the clean static-analysis run through small local typing adjustments,
but its complete user-owned diff is still uncommitted for independent review.

Known non-failing tool output:

- Pyright reports that a newer release is available; the locked project
  version completes with zero diagnostics.
- FastAPI/Pydantic emits an upstream `UnsupportedFieldAttributeWarning` while
  generating the request schema for `aiogram.Update`; Telegram webhook parsing
  and dispatch tests pass.

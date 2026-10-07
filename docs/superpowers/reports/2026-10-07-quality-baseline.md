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

To be completed after all implementation and integration tasks.

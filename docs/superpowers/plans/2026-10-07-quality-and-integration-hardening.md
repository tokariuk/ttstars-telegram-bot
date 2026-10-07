# Quality and Integration Hardening Implementation Plan

## Objective

Make all configured local quality checks pass, further decompose
`StarsOrderService` behind its unchanged public facade, and add opt-in integration
coverage for local infrastructure and external-system boundaries. Do not add CI
and do not call live Telegram or payment APIs.

## Working Rules

- Preserve `.DS_Store` and the existing uncommitted
  `app/services/fragment_stars.py` work.
- Inspect the staged diff before every commit.
- Use one red-green-refactor cycle for every runtime behavior moved or fixed.
- Treat a static checker error as evidence: identify where the imprecise type
  originates before adding a cast or ignore.
- Do not weaken Ruff, mypy, or pyright configuration.
- Keep formatting, typing, orchestration, and integration changes in separate
  commits.

## Task 1: Protect User Work and Record the Baseline

Files:

- Read only: `.DS_Store`
- Read only initially: `app/services/fragment_stars.py`
- Create: `docs/superpowers/reports/2026-10-07-quality-baseline.md`

Steps:

1. Record `git status --short`, the names of user-owned files, and the current
   checks in the report without copying secrets or environment values.
2. Run and record exact counts for unit tests, Ruff, format-check, mypy, pyright,
   and compileall.
3. Record the current `fragment_stars.py` diff statistics and relevant checker
   diagnostics so later edits can be distinguished from user work.
4. Confirm no files are staged.

Verification:

```bash
git status --short
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy .
.venv/bin/pyright
```

No commit is required until the report is complete.

## Task 2: Isolate Mechanical Formatting

Files:

- Modify: the 54 files reported by `ruff format --check .`
- Modify: `migrations/versions/015_balance_topups.py`
- Preserve unstaged: `app/services/fragment_stars.py`

Steps:

1. Reproduce the two E501 failures and the formatter list.
2. Reflow only the two long SQL expressions without changing SQL tokens.
3. Run `ruff format` over the project.
4. Compare `app/services/fragment_stars.py` with the recorded user diff and
   leave it unstaged.
5. Stage all other mechanically formatted files explicitly.
6. Inspect `git diff --cached --word-diff=porcelain` for non-whitespace changes.

Verification:

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m compileall -q app migrations scripts tests
git diff --cached --check
```

Commit:

```text
style: normalize project formatting
```

## Task 3: Type the Platega Adapter Boundary

Files:

- Modify: `app/vendor/platega_sdk/exceptions.py`
- Modify: `app/vendor/platega_sdk/callback.py`
- Modify: `app/vendor/platega_sdk/platega.py`
- Modify: `app/services/platega_pay.py`
- Create: `tests/test_platega_sdk.py`

Red-green-refactor sequence:

1. Add behavior tests that hand-check the request payload produced for omitted
   and supplied optional fields, exception string rendering, and configurable
   API base URL.
2. Verify each new test fails for the intended mutation or missing test seam.
3. Add precise `str | None`, `int | None`, `dict[str, Any]`, callback parameter,
   return, and class-attribute annotations.
4. Keep payload keys, URL construction, exception messages, and synchronous
   SDK behavior unchanged.
5. Narrow the wrapper only after its `configured` guard proves required values
   are non-empty.

Verification:

```bash
.venv/bin/python -m unittest tests.test_platega_sdk -v
.venv/bin/mypy app/vendor/platega_sdk app/services/platega_pay.py
.venv/bin/pyright app/vendor/platega_sdk app/services/platega_pay.py
.venv/bin/ruff check app/vendor/platega_sdk app/services/platega_pay.py tests/test_platega_sdk.py
```

Commit:

```text
refactor: type platega adapter boundary
```

## Task 4: Fix Redis, Telethon, and Export Boundaries

Files:

- Modify: `app/services/redis/repository.py`
- Modify: `app/services/telegram_gifts.py`
- Modify: `scripts/generate_gifts_userbot_session.py`
- Modify: `app/services/promo_codes.py`
- Modify: `app/telegram/dialogs/flows/storefront/check_card.py`
- Modify: `app/telegram/dialogs/flows/storefront/router_parts/check_inline_chosen.py`
- Modify: `app/telegram/dialogs/flows/admin/handlers/stars_sell.py`
- Modify: `app/telegram/dialogs/flows/storefront/handlers/__init__.py`
- Create or extend focused unit tests under `tests/`

Red-green-refactor sequence:

1. Add a Redis fake test proving wildcard deletion accepts both byte and string
   keys and deletes the same values returned by Redis.
2. Add narrow behavior tests for each Optional branch whose current type is
   unsafe.
3. Add explicit public aliases or `__all__` entries for intended re-exports.
4. Contain Telethon's missing typing metadata at its adapter imports; do not
   disable untyped-import checking globally.
5. Remove the obsolete ignore only after its target expression type-checks.

Verification:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/mypy app/services/redis app/services/telegram_gifts.py scripts/generate_gifts_userbot_session.py app/telegram
.venv/bin/pyright app/services/redis app/services/telegram_gifts.py app/telegram
.venv/bin/ruff check app/services/redis app/services/telegram_gifts.py scripts app/telegram tests
```

Commit:

```text
refactor: tighten infrastructure type boundaries
```

## Task 5: Introduce Typed Stars-Order Collaborator Protocols

Files:

- Create: `app/services/crud/stars_order_support/contracts.py`
- Modify: `app/services/crud/stars_order_support/invoices.py`
- Modify: `app/services/crud/stars_order_support/fulfillment.py`
- Modify: `app/services/crud/stars_order_support/runtime_ops.py`
- Modify: `app/services/crud/stars_order_support/webhooks.py`
- Modify as required: other `stars_order_support/*.py`
- Create: `tests/test_stars_order_contracts.py`

Red-green-refactor sequence:

1. Add focused tests with minimal real fakes for one invoice path, one
   fulfillment path, one refund path, and one webhook transition. Assert DTOs,
   transition arguments, and errors rather than mock existence.
2. Define structural protocols for the exact attributes and async methods used
   by each collaborator. Split protocols when invoice, fulfillment, and runtime
   dependencies differ materially.
3. Replace `service: Any`, `checkout_pricing: Any`, and `list[Any]` with the
   protocols and concrete DTO/result types.
4. Type repository DTO conversion at the model/repository boundary when that is
   the source of `Any`; use a cast only where a third-party API cannot express
   the contract.
5. Preserve support function names and exports.

Verification:

```bash
.venv/bin/python -m unittest tests.test_stars_order_contracts -v
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/mypy app/services/crud/stars_order_support
.venv/bin/pyright app/services/crud/stars_order_support
.venv/bin/ruff check app/services/crud/stars_order_support tests
```

Commit:

```text
refactor: type stars order collaborators
```

## Task 6: Correct `StarsOrderService` Type Ambiguities

Files:

- Modify: `app/services/crud/stars_order.py`
- Modify only if the source is there: relevant DTO or SQL model modules
- Extend: `tests/test_stars_order_contracts.py`

Red-green-refactor sequence:

1. Add characterization tests for virtual top-up IDs and order verification
   branches that currently share incompatible local variable types.
2. Give top-up and order locals distinct names/types and narrow union results
   before returning them.
3. Replace remaining `Any` returns by fixing the called boundary's annotation.
4. Preserve `PaymentCheckResult`, exception, and public method contracts.

Verification:

```bash
.venv/bin/python -m unittest tests.test_stars_order_contracts -v
.venv/bin/mypy app/services/crud/stars_order.py app/services/crud/stars_order_support
.venv/bin/pyright app/services/crud/stars_order.py app/services/crud/stars_order_support
```

Commit:

```text
refactor: clarify stars order verification types
```

## Task 7: Extract Top-Up Orchestration

Files:

- Create: `app/services/crud/stars_order_support/topups.py`
- Modify: `app/services/crud/stars_order_support/contracts.py`
- Modify: `app/services/crud/stars_order_support/__init__.py`
- Modify: `app/services/crud/stars_order.py`
- Create: `tests/test_stars_order_topups.py`

Red-green-refactor sequence:

1. Characterize ID encoding/decoding, record creation, invoice attachment,
   payment verification, terminal statuses, fulfillment, and failure results.
2. Move one behavior at a time to `topups.py`, running the focused test after
   every move.
3. Leave facade methods and private compatibility wrappers in
   `StarsOrderService`; each wrapper delegates without reshaping arguments or
   results.
4. Keep database transactions and status transitions in their existing order.

Verification:

```bash
.venv/bin/python -m unittest tests.test_stars_order_topups -v
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/mypy app/services/crud/stars_order.py app/services/crud/stars_order_support
.venv/bin/pyright app/services/crud/stars_order.py app/services/crud/stars_order_support
```

Commit:

```text
refactor: isolate balance topup orchestration
```

## Task 8: Complete Provider and Fulfillment Delegation

Files:

- Modify: `app/services/crud/stars_order_support/invoices.py`
- Modify: `app/services/crud/stars_order_support/fulfillment.py`
- Modify: `app/services/crud/stars_order_support/webhooks.py`
- Modify: `app/services/crud/stars_order.py`
- Extend: stars-order focused tests

Steps:

1. Identify remaining provider-specific branches in the facade.
2. Add a failing characterization test for each branch before moving it.
3. Move implementation into the existing support owner and retain a thin
   facade wrapper.
4. Verify call ordering for locks, status transitions, delivery, referral
   rewards, and refunds.

Verification:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/ruff check app/services/crud/stars_order.py app/services/crud/stars_order_support tests
.venv/bin/mypy app/services/crud/stars_order.py app/services/crud/stars_order_support
.venv/bin/pyright app/services/crud/stars_order.py app/services/crud/stars_order_support
```

Commit:

```text
refactor: complete stars order orchestration boundaries
```

## Task 9: Reach a Clean Static-Analysis Baseline

Files:

- Modify only files named by the remaining checker output
- Possibly modify, but never stage without explicit review:
  `app/services/fragment_stars.py`
- Update: `docs/superpowers/reports/2026-10-07-quality-baseline.md`

Steps:

1. Run project-wide mypy and pyright.
2. For each remaining error, trace the originating imprecise annotation and
   fix that source in isolation.
3. If the only remaining diagnostics are in the user-owned Fragment file, make
   the smallest local annotation changes, keep the complete file unstaged, and
   show the exact additional hunks separately.
4. Record the zero-error result in the report.

Verification:

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy .
.venv/bin/pyright
.venv/bin/python -m unittest discover -s tests -v
```

Commit all non-user-owned fixes as:

```text
refactor: complete static type coverage
```

## Task 10: Add Disposable PostgreSQL and Redis Integration Infrastructure

Files:

- Create: `docker-compose.test.yml`
- Create: `tests/integration/__init__.py`
- Create: `tests/integration/support.py`
- Create: `tests/integration/test_healthcheck.py`
- Create: `tests/integration/test_repositories.py`
- Modify: `Makefile`
- Modify: `README.md`

Red-green-refactor sequence:

1. Add integration tests that skip unless `TEST_POSTGRES_URL` and
   `TEST_REDIS_URL` are explicitly set.
2. Verify the skip behavior without infrastructure.
3. Add isolated Compose services with fixed test-only credentials, health
   checks, disposable volumes, and ports distinct from development defaults.
4. Add a Make target that starts services, waits on health conditions, applies
   Alembic migrations, runs only `tests/integration`, and tears down with
   volumes.
5. Test PostgreSQL/Redis readiness, Redis round trips and wildcard deletion,
   and representative repository create/read/status-transition behavior.

Verification:

```bash
.venv/bin/python -m unittest discover -s tests/integration -v
docker compose -f docker-compose.test.yml config
make integration-test
docker compose -f docker-compose.test.yml ps -a
```

The final command must show no leftover running test containers.

Commit:

```text
test: add postgres and redis integration coverage
```

## Task 11: Add HTTP, Payment, and Telegram Boundary Integration Tests

Files:

- Create: `tests/integration/test_payment_webhooks.py`
- Create: `tests/integration/test_telegram_wiring.py`
- Create or extend: `tests/integration/fakes.py`
- Modify only if a test exposes a real defect: corresponding endpoint/factory
  module
- Update: `README.md`

Red-green-refactor sequence:

1. Exercise every payment webhook router in-process with hand-authored valid,
   invalid-signature, malformed, and unknown-order fixtures.
2. Assert HTTP status, response body, and order-facade outcome; fake only the
   network/provider boundary.
3. Construct Telegram dispatcher, routers, dialogs, and middleware using a
   local session double and representative updates. Assert observable routing
   or produced API request data, not mock existence.
4. Confirm no test invokes provider hosts or Telegram's API.

Verification:

```bash
.venv/bin/python -m unittest tests.integration.test_payment_webhooks -v
.venv/bin/python -m unittest tests.integration.test_telegram_wiring -v
.venv/bin/python -m unittest discover -s tests -v
```

Commit:

```text
test: cover payment and telegram boundaries
```

## Task 12: Final Verification and Handoff

Steps:

1. Run all local checks and the disposable integration suite.
2. Inspect every commit and the aggregate diff from `53b5623`.
3. Verify public imports, route paths, callback/state keys, and Alembic head.
4. Verify `.DS_Store` and `app/services/fragment_stars.py` remain uncommitted.
5. Update the baseline report with final commands and results.

Commands:

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m compileall -q app migrations scripts tests
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy .
.venv/bin/pyright
make integration-test
git diff --check
git status --short
git log --oneline 53b5623..HEAD
```

Completion requires zero local checker errors, passing unit and integration
tests, no live external calls, no CI changes, and no accidental commit of user
work.

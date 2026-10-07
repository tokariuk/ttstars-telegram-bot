# Quality and Integration Hardening Design

## Context

The first maintainability refactor is complete in commit `f737e6d`. It added
characterization tests, shared route and dialog-state helpers, isolated checkout
pricing, and decomposed service construction. The remaining work is broader:
make the configured quality checks pass, reduce the responsibilities of
`StarsOrderService`, and add integration coverage for local infrastructure and
external-system boundaries.

The project is a Python 3.14 Telegram commerce bot using aiogram,
aiogram-dialog, FastAPI, SQLAlchemy, PostgreSQL, Redis, Alembic, and several
payment providers. Existing behavior, public imports, database formats, HTTP
routes, callback data, dialog state, and configuration remain compatibility
constraints.

The user has explicitly excluded CI configuration from this stage.

## Current Baseline

- Ruff reports two line-length errors in migration `015_balance_topups.py`.
- Ruff format-check reports 54 files that require formatting.
- mypy reports 86 errors in 19 files. The largest groups are unsafe `Any`
  returns in stars-order support modules, untyped vendored Platega code, missing
  Telethon typing metadata, and incorrect optional or re-export annotations.
- pyright reports four errors in Platega and Redis integration code.
- The Docker CLI and Compose plugin are installed, but the Docker daemon is not
  currently running.
- The repository contains a Compose example but no active Compose file.
- `.DS_Store` and `app/services/fragment_stars.py` contain pre-existing user
  changes. They must not be accidentally staged or committed.

## Goals

1. Make project-wide Ruff check, Ruff format-check, mypy, and pyright pass
   without weakening their configuration or adding blanket suppressions.
2. Reduce `StarsOrderService` orchestration complexity while preserving its
   public facade and all existing behavior.
3. Add repeatable integration checks for PostgreSQL, Redis, HTTP webhook
   boundaries, and Telegram wiring without contacting live payment or Telegram
   APIs.
4. Keep changes reviewable through small, purpose-specific commits.

## Non-Goals

- No new product features or behavior changes.
- No database schema or data migration changes unless an integration fixture
  exposes a genuine migration defect; such a defect would be reported before
  expanding scope.
- No live payment creation, Telegram message delivery, or other externally
  visible side effects.
- No CI workflow in this stage.
- No replacement of the existing dependency-injection or persistence
  architecture.

## Selected Approach

Work proceeds incrementally instead of rewriting `StarsOrderService` or hiding
type errors through configuration. Each type error is classified by root cause,
then fixed at the narrowest ownership boundary. Existing support modules become
typed collaborators behind the unchanged service facade.

Mass formatting is isolated from semantic changes. This makes later diffs
reviewable and prevents formatter output from obscuring type and orchestration
changes.

## Workstream 1: Mechanical Quality Baseline

Run Ruff formatting across project-owned files and fix the two migration line
length violations without changing SQL contents. The formatting change is
committed separately from semantic work.

`app/services/fragment_stars.py` is protected because it contains user work. A
snapshot of its pre-stage diff will be retained for comparison. Formatting may
be applied so the project-wide format check can pass, but the file will remain
unstaged unless the user later explicitly asks to include it. Any required type
fix in that file will be minimal and reported separately.

Success criteria:

- `ruff check .` passes;
- `ruff format --check .` passes in the working tree;
- the mechanical commit contains no behavior changes and no user-owned file.

## Workstream 2: Type-Safety Root Causes

Errors will be handled in small groups using the systematic-debugging and TDD
workflow where runtime behavior is involved.

### Stars-order collaborators

Replace unbounded `service: Any` and `checkout_pricing: Any` parameters with
small structural protocols describing only the methods and attributes each
module consumes. Give polling, fulfillment, invoice, runtime, and webhook
helpers concrete return types. This removes `Any` propagation without coupling
support modules back to the concrete `StarsOrderService` class.

Correct ambiguous local variable types in `StarsOrderService`, particularly the
shared top-up/order verification paths. Public return types remain unchanged.

### Platega boundary

Type the bundled Platega SDK's optional parameters, dictionaries, callbacks,
exception fields, and class attributes. The wrapper will pass values matching
the SDK signature and retain the configurable base URL. No HTTP request or
payload behavior changes.

### Redis, Telethon, and re-exports

- Accept Redis' declared `bytes | str` key result and pass it through without
  changing deletion behavior.
- Contain untyped Telethon imports at the adapter boundary using precise local
  annotations or targeted import handling, not a project-wide relaxation.
- Replace implicit re-exports with explicit aliases or `__all__` declarations.
- Resolve Optional narrowing and obsolete `type: ignore` comments at their
  source.

Success criteria:

- `mypy .` reports zero errors;
- `pyright` reports zero errors;
- existing and new regression tests pass.

## Workstream 3: `StarsOrderService` Decomposition

`StarsOrderService` remains the public entry point. Callers, constructor
arguments, public methods, exceptions, DTOs, and status transitions do not
change.

The next internal boundaries are:

1. **Provider invoice orchestration** — typed dispatch for creating and
   attaching provider invoices.
2. **Fulfillment orchestration** — typed gift, Fragment, balance, retry, refund,
   and referral collaborators.
3. **Top-up orchestration** — top-up record lifecycle, verification, and
   fulfillment currently embedded in the main service.
4. **Webhook orchestration** — provider-specific lookup and transition logic.

Existing functions in `stars_order_support` will be strengthened rather than
replaced by a second service framework. The facade delegates to these modules,
and thin private wrappers are retained when other modules depend on their
current names.

Before moving each behavior, characterization tests will cover its observable
return value, state-transition request, exception, and external boundary call.
Tests will use real domain calculations and focused fakes only for database,
network, or Telegram boundaries.

Success criteria:

- no public signature or import changes;
- the main service contains coordination rather than provider-specific branch
  implementations;
- all extracted modules have explicit dependency protocols and concrete return
  types;
- test behavior is identical before and after each extraction.

## Workstream 4: Integration Coverage

### PostgreSQL and Redis

Add an isolated test Compose definition with disposable PostgreSQL and Redis
services and non-production credentials. Integration tests are opt-in through
dedicated test URLs so normal unit-test discovery remains fast and does not
silently connect to developer or production infrastructure.

The integration suite will:

- apply Alembic migrations to an empty PostgreSQL database;
- execute PostgreSQL and Redis health checks;
- exercise representative repository create/read/transition operations;
- verify Redis serialization, retrieval, wildcard deletion, and shutdown.

Containers and volumes are scoped to the test project and are removable without
touching development data.

### HTTP, payment, and Telegram boundaries

Webhook routers will be exercised in-process with signed or otherwise valid
provider fixtures and focused fake provider services. Tests verify route paths,
payload parsing, signature rejection, status codes, and delegation into the
order facade. They do not call provider networks.

Telegram coverage will validate dispatcher/dialog/router construction and
representative update handling with a local Bot session double below the
application boundary. It will not send messages or configure real webhooks.

External live API smoke tests are deliberately excluded because they require
secrets and can create financial or user-visible side effects.

Success criteria:

- a documented command starts disposable infrastructure and runs integration
  tests;
- tests skip with a clear reason when integration URLs are absent;
- no test reads normal production secrets by default;
- teardown removes test containers and volumes.

## Error Handling and Compatibility

Existing exception types, messages, status transitions, retry decisions, and
refund behavior are preserved. Type narrowing must not convert runtime
validation into static assumptions. External responses remain validated at the
adapter boundary.

No public API, persistent data shape, environment variable used by production,
or webhook contract will change. Test-only environment variables use a distinct
`TEST_` prefix.

## Commit Strategy

1. Mechanical Ruff formatting and lint cleanup.
2. Typed infrastructure and third-party adapter boundaries.
3. Typed stars-order support protocols and return values.
4. Incremental stars-order orchestration extractions, one responsibility per
   commit.
5. PostgreSQL/Redis integration harness and tests.
6. HTTP/payment/Telegram boundary integration tests and documentation.

Before every commit, inspect the staged diff and ensure `.DS_Store` and the
user-owned Fragment work are absent.

## Verification

After each logical change:

- run its focused test first;
- run the complete unit suite;
- run Ruff on touched files;
- run the relevant mypy and pyright targets.

At completion:

1. run all unit tests;
2. run the opt-in integration suite against disposable containers;
3. compile `app`, `migrations`, `scripts`, and tests;
4. run `ruff check .` and `ruff format --check .`;
5. run `mypy .` and `pyright`;
6. inspect `git diff --check`, every staged diff, and final Git status;
7. confirm the two original user changes are preserved and not committed.

## Known Operational Constraint

Docker Desktop must be running for the container integration suite. Starting it
is an environment operation, not a code change, and will be requested only when
the tests are ready to run.

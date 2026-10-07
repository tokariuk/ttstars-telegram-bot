# Maintainability Refactor Design

## Context

The project is a Python 3.14 Telegram commerce bot built with aiogram,
aiogram-dialog, FastAPI, SQLAlchemy, PostgreSQL, Redis, Alembic, and Fluent.
Its runtime entry point is `app.__main__`; dependency construction lives under
`app.factory`, HTTP endpoints under `app.endpoints`, and Telegram UI flows under
`app.telegram.dialogs`.

The refactor must preserve business behavior, public imports, persisted data,
configuration formats, HTTP routes, Telegram callback/state keys, and runtime
compatibility. Existing user changes in `.DS_Store` and
`app/services/fragment_stars.py` are outside the scope and must remain intact.

## Problems in Scope

### Repeated route-path normalization

Webhook paths are normalized with the same conditional expression in the
FastAPI factory, payment endpoint factories, a Telegram handler, and provider
URL helpers. The repetition makes it easy for path behavior to diverge between
registration and callback URL generation.

### Repeated dialog-state parsing

The storefront and admin flows independently implement equivalent helpers for
positive integers, non-negative pages, optional identifiers, stripped strings,
and stars-sell draft state. The copies already have small implementation
differences and make state behavior harder to verify.

### Pricing logic embedded in the order orchestrator

`StarsOrderService` combines persistence, payment orchestration, fulfillment,
webhook handling, reporting, and checkout pricing. The checkout-pricing block
is deterministic domain calculation and can be tested independently, but is
currently coupled to a large service with many runtime dependencies.

### Monolithic dependency construction

`create_services` performs secret extraction, configuration normalization,
payment-client construction, and CRUD-service wiring in one function. This is
hard to scan and makes individual construction paths difficult to test.

### Missing regression tests

The repository has no automated test suite. Structural movement in payment
code therefore needs characterization tests before implementation.

## Proposed Design

### 1. Characterization tests

Add tests using the standard-library `unittest` runner so no dependency is
introduced. Tests will cover:

- current path normalization for relative, absolute, empty, and repeated-slash
  inputs;
- current dialog-state handling for integers, numeric strings, invalid values,
  whitespace, deletion, and draft clearing;
- checkout pricing for balance, an on-top-fee provider, a deducted-fee
  provider, fixed payout fees, rounding, invalid fee configuration, and display
  formatting;
- service-factory helper outputs where they can be tested without external
  services.

Tests that characterize existing functions will be written and run before
moving their implementations.

### 2. Shared path helper

Introduce a small helper under `app.utils` that implements the exact existing
rule: retain a path beginning with `/`; otherwise prefix one `/`. Replace exact
copies in endpoint factories and application setup. The helper will not strip
whitespace, collapse repeated slashes, or reject empty input because those
changes would alter behavior.

Endpoint factory signatures and registered route paths remain unchanged.

### 3. Shared dialog-state primitives

Introduce internal helpers under `app.telegram.dialogs.common` for:

- reading a non-negative integer;
- reading a positive integer;
- reading a stripped non-empty string;
- setting or removing integer/string values;
- clearing a supplied set of keys.

Existing flow-specific functions retain their names, modules, parameters, and
state keys. They delegate only the repeated parsing/storage mechanics to the
common helpers. Flow-specific rules, including username normalization, gift
validation, and start-data fallback, stay in their current modules.

### 4. Isolated checkout-pricing calculation

Create `app/services/crud/stars_order_support/pricing.py` containing the
deterministic pricing data type and calculations. The module will accept fee
maps and required error construction explicitly; it will not depend on a live
database, Redis client, or payment provider.

`StarsOrderService` remains the public facade. Existing methods such as
`preview_checkout_pricing`, `checkout_pricing_for_order`, and fee-display
methods preserve their signatures and results. `CheckoutPricing` remains
importable from `app.services.crud.stars_order` through an explicit re-export.
Private compatibility wrappers will remain where existing support modules call
them.

Referral calculations and provider availability stay outside this extraction;
they are separate responsibilities and moving them would expand scope.

### 5. Service-factory decomposition

Split `create_services` into private construction helpers for external payment
clients and application/CRUD services. `Services`, `create_services`, service
instances, constructor arguments, and workflow-data keys remain unchanged.
No dependency-injection framework or new abstraction layer will be added.

## Error Handling

The refactor will preserve current exception types and messages. Broad
exception handling elsewhere in the project will be reported as follow-up work
unless a moved code path requires a mechanical relocation. No existing failure
will be silently converted into a success or a different HTTP/Telegram result.

## Compatibility Constraints

- No database or Alembic changes.
- No configuration or environment-variable changes.
- No changes to HTTP paths, payloads, callback data, localization keys, dialog
  state keys, or public method signatures.
- No new runtime or development dependencies.
- No mass formatting.
- No edits to the user's in-progress Fragment/TonConnect work.
- No deletion of apparently unused exports without evidence that external and
  dynamic use is impossible.

## Verification

After each logical change, run its focused `unittest` tests and Ruff on the
touched files. At completion run:

1. the full `unittest` discovery suite;
2. Python bytecode compilation for `app`, `migrations`, `scripts`, and tests;
3. Ruff check and format-check on touched files;
4. project-wide Ruff, mypy, and pyright to compare with the recorded baseline;
5. `git diff --check` and a manual review of the final diff.

Known baseline failures will be kept distinct from regressions: two Ruff line
length errors, 55 files failing format-check, 86 mypy errors, and four pyright
errors. The absence of integration infrastructure means external payment,
Telegram, PostgreSQL, and Redis behavior can be validated only through isolated
tests and static checks in this refactor.

## Delivery Sequence

1. Add and run characterization tests.
2. Consolidate path normalization.
3. Consolidate dialog-state primitives.
4. Extract pricing calculations behind the existing facade.
5. Decompose service construction.
6. Run focused and project-wide verification.
7. Review the diff for behavioral or unrelated changes.

Each step is independently reviewable and may be reverted without requiring a
data migration.

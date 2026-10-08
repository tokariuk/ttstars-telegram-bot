# Telegram UX/UI Hardening Implementation Plan

## Objective

Make the storefront and administrative Telegram interfaces safer, clearer, and
more consistent across Russian, Ukrainian, and English without changing payment
logic, persistence, callback data, dialog states, or external API contracts.

## Working Rules

- Preserve the approved design in
  `docs/superpowers/specs/2026-10-08-telegram-ux-ui-hardening-design.md`.
- Use a red-green-refactor cycle for every runtime helper or rendering change.
- Keep raw text, escaped text, and intentionally trusted HTML visibly separate.
- Preserve all callback IDs, deep-link payloads, states, financial calculations,
  and the order of financial side effects.
- Keep Fluent copy translator-friendly; do not build prose in Python.
- Do not add dependencies or perform real paid Telegram operations.
- Keep commits small and inspect each diff for accidental behavioral changes.

## Task 1: Establish UI and Localization Contract Tests

Files:

- Create: `tests/test_i18n_catalogs.py`
- Create: `tests/test_telegram_ui_contracts.py`
- Read: `assets/messages/{ru,uk,en}/**/*.ftl`
- Read: `app/telegram/dialogs/flows/**/windows/*.py`

Red-green-refactor sequence:

1. Add a real Fluent-parser test for every catalog file.
2. Compare relative file topology, message keys, and variable placeholders for
   `ru`, `uk`, and `en` with hand-readable failure diagnostics.
3. Add Telegram boundary tests for callback data byte length, custom-emoji
   Unicode fallback, and supported HTML produced by shared UI helpers.
4. Add focused navigation/style checks for concrete dialog windows, avoiding
   assertions on incidental source formatting or exact prose.
5. Run the tests and record expected failures before production changes.

Verification:

```bash
uv run python -m unittest tests.test_i18n_catalogs tests.test_telegram_ui_contracts -v
```

## Task 2: Introduce the Safe Telegram HTML Boundary

Files:

- Create: `app/telegram/html.py`
- Create: `tests/test_telegram_html.py`
- Modify: `app/telegram/dialogs/flows/storefront/getters/common.py`
- Modify: focused storefront/admin getters and handlers identified by the audit

Red-green-refactor sequence:

1. Test hostile plain text containing `<`, `>`, `&`, quotes, complete tags, and
   incomplete tags.
2. Test copyable identifiers and spoiler identifiers as complete trusted
   fragments, including empty and long values.
3. Test visible-text measurement and diagnostic truncation at Telegram limits.
4. Implement the smallest helpers needed for plain-text escaping, identifier
   rendering, safe link attributes, diagnostic truncation, and visible length.
5. Replace local helper duplication without double-escaping trusted fragments.

Verification:

```bash
uv run python -m unittest tests.test_telegram_html -v
uv run ruff check app/telegram/html.py tests/test_telegram_html.py
uv run pyright app/telegram/html.py
```

## Task 3: Escape Dynamic Storefront and Inline Data

Files:

- Modify: storefront getters for menu, gifts, checks, history, promo, and sale
- Modify: storefront checkout/result handlers
- Modify: inline-check rendering modules
- Extend: focused UI/HTML tests

Red-green-refactor sequence:

1. Add representative tests proving hostile display names, usernames, gift
   messages, promo codes, transaction references, provider errors, and wallet
   values cannot create Telegram entities.
2. Pass escaped plain values to Fluent messages and pass trusted helper markup
   only to placeholders explicitly intended to contain markup.
3. Remove nested `<code>`/`<tg-spoiler>` composition in checks and history.
4. Preserve admin-authored broadcast HTML as an explicit trusted boundary while
   escaping button labels and URLs.
5. Check normal message and media-caption visible lengths after interpolation.

Verification:

```bash
uv run python -m unittest tests.test_telegram_html tests.test_telegram_ui_contracts -v
uv run ruff check app/telegram tests
```

## Task 4: Escape Administrative and Operational Data

Files:

- Modify: admin getters for users, orders, promo codes, sales, and broadcasts
- Modify: administrative result/error helpers where needed
- Extend: focused UI/HTML tests

Red-green-refactor sequence:

1. Characterize rendered admin summaries containing hostile provider errors,
   resolution notes, payout wallets, usernames, and promo values.
2. Escape external and database-originated text at the rendering boundary.
3. Keep technical identifiers copyable and long diagnostics in expandable
   blocks, with safe truncation before markup.
4. Preserve diagnostic value while preventing raw provider payloads or secrets
   from entering user-facing error text.

Verification:

```bash
uv run python -m unittest tests.test_telegram_html tests.test_telegram_ui_contracts -v
uv run ruff check app/telegram/dialogs/flows/admin tests
```

## Task 5: Align Copy and State Messages Across Locales

Files:

- Modify: `assets/messages/{ru,uk,en}/dialogs/storefront/*.ftl`
- Modify: `assets/messages/{ru,uk,en}/dialogs/admin/*.ftl`
- Modify only when needed: system/payment/inline Fluent files
- Extend: `tests/test_i18n_catalogs.py`

Steps:

1. Normalize storefront Russian to calm, concise informal address and adapt the
   same semantics naturally for Ukrainian and English.
2. Give error messages cause/state/next-action structure without exposing raw
   exceptions.
3. Give success messages concrete results and useful next destinations.
4. Make empty states actionable and waiting states factual rather than
   time-promising.
5. Replace unnecessary English internal terms in Russian/Ukrainian admin copy.
6. Keep key and placeholder parity after every localized group is changed.

Verification:

```bash
uv run python -m unittest tests.test_i18n_catalogs -v
```

## Task 6: Correct Button Semantics and Navigation

Files:

- Modify: storefront purchase/top-up/gift/sale windows
- Modify: admin order/sale/promo/broadcast windows
- Extend: `tests/test_telegram_ui_contracts.py`

Red-green-refactor sequence:

1. Add focused tests for the known misuse of danger styling on unavailable
   provider choices and for genuinely destructive actions.
2. Keep provider callback IDs unchanged but hide unavailable actions or label
   them clearly with a handled explanation; never simulate disabled with danger.
3. Arrange primary, alternative, edit, navigation, and cancellation actions in
   predictable groups suitable for narrow mobile screens.
4. Ensure each dialog state has a next step, logical Back action, main-menu exit,
   or explicit cancellation path.
5. Keep checkout links and important final results as separate persistent
   messages; retain editing within a dialog flow.

Verification:

```bash
uv run python -m unittest tests.test_telegram_ui_contracts -v
uv run pyright app/telegram/dialogs/flows
```

## Task 7: Consolidate Semantic Emoji Without Breaking Compatibility

Files:

- Modify: `app/telegram/dialogs/common/ttstars_interface_emoji.py`
- Modify: `app/telegram/dialogs/common/premium_emoji.py`
- Modify only where duplicated literals are confirmed: windows and Fluent files
- Extend: `tests/test_telegram_ui_contracts.py`

Steps:

1. Treat `ttstars_interface_emoji.py` as the authoritative project-sourced
   catalog and retain `premium_emoji.py` as compatibility/semantic aliases.
2. Keep provider- and gift-specific IDs whose source is already documented.
3. Replace only exact, verified duplicate literals; do not invent IDs.
4. Test that each emitted custom-emoji fragment has meaningful Unicode content.
5. Keep the interface understandable if Telegram ignores custom emoji.

Verification:

```bash
uv run python -m unittest tests.test_telegram_ui_contracts -v
```

## Task 8: Final Static, Automated, and Optional Telegram Verification

Files:

- Modify only for regressions attributable to this work
- Create: `docs/superpowers/reports/2026-10-08-telegram-ux-ui-hardening.md`

Steps:

1. Run the full unit suite, Ruff check/format, mypy, Pyright, and compileall.
2. Inspect locale parity, Telegram limits, callback IDs, state declarations,
   button styles, banners, and the complete diff.
3. Compare existing failures, if any, with the pre-change 66-test baseline.
4. If a safe non-paying admin chat can be identified without exposing secrets,
   send and delete one rendering probe for custom emoji, button colors, editing,
   and Unicode fallback. Otherwise record that eligibility remains unconfirmed.
5. Do not push or deploy unless explicitly requested.

Verification:

```bash
uv run python -m unittest discover -s tests -v
uv run ruff check app tests migrations scripts
uv run ruff format --check app tests migrations scripts
uv run mypy app tests migrations scripts
uv run pyright
uv run python -m compileall -q app migrations scripts tests
git diff --check
git status --short
```

## Acceptance Conditions

- All three locales parse and have matching keys/placeholders.
- Dynamic external text cannot alter Telegram HTML.
- Normal messages, captions, callback data, and button labels respect practical
  Telegram limits covered by tests.
- Storefront copy is consistently informal in Russian and naturally localized.
- Empty, waiting, error, and success states provide the next useful action.
- Danger styling is reserved for destructive actions.
- Custom emoji always retain meaningful Unicode fallback.
- Existing callback IDs, dialog states, financial behavior, and public service
  contracts remain unchanged.

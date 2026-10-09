# TTStars Telegram UX/UI hardening report

Date: 2026-10-09

## Scope and preserved contracts

The storefront, administrative dialogs, Fluent catalogs, system notifications,
checkout/result messages, inline checks, custom emoji catalogs, banners, and
`/start` routing were audited. Financial calculations, payment integrations,
database models, callback data, callback IDs, dialog states, deep-link payloads,
and fulfillment order were intentionally left unchanged.

The existing dialog-message editing model, separate durable checkout/result
messages, localized 1800×810 banners, rich checkout summaries, and `/start`
deep-link handling were already sound and were preserved.

## Findings by priority

1. **Message-breaking HTML risks.** Usernames, names, gift messages, promo data,
   wallets, transaction hashes, provider errors, resolution notes, and invoice
   payloads reached HTML templates through inconsistent escaping. Some templates
   also wrapped values already formatted as `<code>` or `<tg-spoiler>`, creating
   invalid nested markup.
2. **Diagnostic-data exposure and unbounded captions.** Provider exceptions and
   stored failure details could be rendered verbatim in administrative and user
   messages. Long values could overflow a media caption.
3. **Misleading button semantics.** Payment-provider buttons below the minimum
   amount used `danger`, although they remained active. Force delivery did not
   visually communicate the risk clearly.
4. **Navigation density.** The main menu used a long vertical stack. Later Gift
   steps repeated shortcuts to several earlier steps instead of emphasizing the
   logical back action.
5. **Inconsistent language and empty states.** Russian Stars-sale messages mixed
   formal and informal address; administrative screens exposed English internal
   terms. Empty history/check screens stated only that no data existed.
6. **Localization drift.** Ukrainian Gifts messages had placeholder sets that did
   not match Russian and English. This was invisible without AST-level checks.
7. **Emoji duplication.** Shared interface IDs were duplicated between two Python
   catalogs, making accidental divergence likely.

## Changes

- Added `app/telegram/html.py` as the small trust boundary for plain text,
  attributes, links, usernames, copyable/spoiler IDs, and bounded diagnostics.
  Trusted HTML fragments remain explicit and are not escaped a second time.
- Applied escaping to storefront, checkout, inline-check, result, Stars-sale,
  promo, referral, and administrative output. Provider diagnostics are truncated
  before escaping.
- Removed nested trusted markup from Fluent templates and kept presentation in
  the template while values arrive already safe.
- Shortened the main-menu introduction and grouped secondary actions into rows.
  Gift navigation now presents the previous logical step first; final edits are
  grouped into compact rows.
- Changed unavailable-minimum payment choices from destructive styling to a
  neutral active choice with an explicit `≥ amount` label. Force delivery is now
  the dangerous action; retry remains neutral.
- Made empty histories and check lists actionable and rewrote payment/send errors
  to explain the current state and next action.
- Unified Russian storefront tone on informal “ты” and localized remaining
  administrative delivery/payment terminology in Russian and Ukrainian.
- Synchronized the Ukrainian Gifts placeholders with the other locales.
- Made `ttstars_interface_emoji.py` authoritative for shared interface IDs.
  `premium_emoji.py` retains compatibility exports plus provider/gift-specific
  IDs, so existing imports and IDs remain valid. Unicode fallback is retained in
  every `<tg-emoji>` use.
- Preserved all callback identifiers and dialog states.

## Automated coverage

New tests verify:

- all Fluent files parse without `Junk`;
- identical locale file topology, keys, and placeholder sets for `ru`, `uk`, and
  `en`;
- hostile `<`, `>`, `&`, quotes, tags, unsafe links, and long diagnostics;
- supported and balanced Telegram HTML;
- rendered-message and media-caption limits;
- callback-data limits and practical mobile button-label lengths;
- numeric custom emoji IDs with meaningful Unicode fallback;
- dialog windows expose an action or message input;
- payment and dangerous-action button styles;
- compatibility exports from the legacy emoji module.

Verification result:

- `python -m unittest discover -s tests -v`: 86 passed, 5 skipped;
- skipped tests require `TEST_POSTGRES_URL` and were already environment-gated;
- Ruff lint and format check: passed;
- Mypy: passed for 339 source files;
- Pyright: 0 errors, 0 warnings;
- `compileall`: passed;
- `git diff --check`: passed.

The Pydantic `UnsupportedFieldAttributeWarning` seen in two existing wiring tests
comes from dependency schema generation and is unrelated to these changes.

## Telegram verification

The production bot was tested through the real Telegram Bot API without a paid
operation. A temporary administrative message used the existing custom emoji ID,
a primary button with a custom emoji icon, and HTML. Telegram returned a
`custom_emoji` entity, the `primary` style and icon ID, accepted an edit, and
accepted deletion. The message was deleted immediately. No token or chat ID was
printed.

This confirms the concrete bot can currently use the tested custom emoji in a
direct message. The automated/API check does not replace visual inspection on
multiple Telegram clients. Light/dark theme, slow-network banner transitions, and
physical mobile widths were not manually inspected. Existing banners were kept
because their dimensions, localization, and visual family are consistent and no
important information exists only in the image.

## Remaining limitations

- Five database-backed integration tests need a configured test PostgreSQL/Redis
  environment to run instead of skip.
- Client-specific visual verification still needs a human pass in Telegram on
  representative iOS/Android/Desktop clients.
- Production remains on commit `58807bb`; this UX/UI work was not deployed as
  part of the audit task.

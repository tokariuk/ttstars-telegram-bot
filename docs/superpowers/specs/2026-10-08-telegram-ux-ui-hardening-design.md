# TTStars Telegram UX/UI hardening design

Date: 2026-10-08
Status: approved for planning

## Objective

Make the TTStars Telegram storefront and administration interface safer, clearer, and more consistent without changing financial behavior, callback contracts, deep links, dialog states, database models, or provider integrations.

The work covers all storefront and admin windows, system and payment notifications, inline checks, localized banners, custom emoji usage, and the `ru`, `uk`, and `en` Fluent catalogs.

## Constraints

- Preserve the existing aiogram-dialog structure: windows, getters, handlers, states, and IDs.
- Preserve callback IDs/data, deep-link payloads, service interfaces, payment ordering, prices, fees, and fulfillment rules.
- Keep the established edit-in-place behavior for dialog navigation.
- Keep important checkout and completion events as separate chat messages.
- Add no dependency when the standard library or an existing dependency is sufficient.
- Keep Fluent text readable to translators; do not encode layout logic into opaque Fluent expressions.
- Preserve unrelated user changes and avoid destructive Git operations.

## Audit findings

### Priority 1: message-breaking defects

- Dynamic values such as user mentions, gift messages, wallets, provider errors, promo codes, resolution notes, and external references are not consistently escaped before entering HTML templates.
- `secret_code_view` returns trusted `<code><tg-spoiler>` markup while some Fluent messages wrap the same value in another `<code>/<tg-spoiler>` pair.
- Caption and text lengths are not verified after dynamic substitution.
- Telegram HTML and Rich HTML are treated as one profile even though rich-only elements, such as tables, must remain limited to rich messages.

### Priority 2: safety and escaping

- The code does not explicitly distinguish plain external text from intentionally constructed safe HTML.
- Admin diagnostic fields may contain provider- or database-sourced markup characters.
- Broadcast content is intentionally trusted HTML, while broadcast button labels and URLs are plain external data; that distinction is currently implicit.

### Priority 3: navigation and interaction

- Gifts steps can expose several competing back actions at once.
- Empty history/check screens do not guide the user to a next action.
- The main menu gives almost equal visual weight to products, account actions, and help.
- Payment-provider buttons use `danger` to represent a minimum-amount restriction even though they remain clickable.
- Some destructive admin actions lack suitable visual prominence and consequence wording.

### Priority 4: terminology and voice

- Russian storefront messages mix informal and formal imperatives.
- User-facing Russian includes internal English terms such as `checkout`.
- Admin copy mixes Russian with `Retry fulfill`, `Force fulfill`, and other implementation terminology where a clear Russian label is available.
- `order` is translated inconsistently as both “заказ” and “ордер”.

### Priority 5: visual load

- Too many catalog/payment actions are styled as primary.
- Long technical details are displayed at the same hierarchy as actionable information.
- Some messages repeat their status in both a header and body.

### Priority 6: cosmetic consistency

- Two custom emoji catalogs duplicate IDs and aliases.
- Some Unicode fallbacks are unclear or inconsistent with their semantic role.
- Button labels vary between noun and imperative forms for equivalent navigation.

## Existing decisions to preserve

- The three locale trees currently expose matching Fluent key sets.
- Localized banners are visually consistent, readable, and all use 1800×810 assets. They remain unchanged unless a concrete rendering defect is found.
- `/start` already separates normal, referral, check, and password-protected check flows and resets the stack predictably.
- Dialog transitions edit the current message, while checkout links and material results remain separate messages.
- Callback IDs and dialog states are centralized.
- Inline-check drafts are personal, short-lived, and have fallback behavior.
- Rich checkout tables are useful and valid in the rich-message path.
- Notice normalization already reduces duplicate header blocks.

## Interface language system

Every primary screen should contain, when applicable:

1. A short title/status block.
2. The minimum information required to understand the current step.
3. Current selections or operation status.
4. A direct next-action instruction.
5. A keyboard whose hierarchy matches the text.

Formatting rules:

- `<b>` for headings, totals, and key outcomes.
- `<i>` only for secondary explanations.
- `<code>` for copyable identifiers and values.
- `<blockquote>` for a compact title or status notice.
- `<blockquote expandable>` for long diagnostics.
- `<tg-spoiler>` for lengthy or sensitive identifiers.
- `<a>` only for validated useful links.
- Rich-only tags remain restricted to `InputRichMessage` content.

Russian storefront copy consistently addresses the user with informal singular imperatives. Admin copy can stay technical but uses Russian action labels and explains consequences.

## Safe HTML boundary

Add one small Telegram HTML helper module with explicit operations:

- escape arbitrary plain text;
- escape attribute values/URLs where applicable;
- render copyable identifiers with optional spoiler markup;
- truncate plain diagnostic text before markup construction;
- measure visible text after removing supported markup.

Getters and notification builders must escape all user-, database-, and provider-sourced strings before passing them into HTML-bearing Fluent messages. Numeric values and internally selected localized labels remain plain. Trusted markup such as `<tg-time>` or a deliberately built identifier block is passed only to a Fluent placeholder that is not wrapped again.

Broadcast body HTML remains intentionally trusted admin-authored markup. Broadcast button text and URLs remain escaped/validated separately. Helper names and tests must make this trust boundary explicit.

## Localization strategy

- Keep the current functional file split.
- Apply every semantic change to `ru`, `uk`, and `en` together.
- Require identical relative file sets, message IDs, and placeholder sets.
- Render representative messages in every locale.
- Do not depend on locale fallback for a newly added key.
- Keep user-facing values localized while technical IDs remain language-neutral.

## Navigation and button hierarchy

- Primary purchase/confirmation action: `primary` or `success` when it represents a positive completion.
- Destructive cancellation, deletion, rejection, or forced fulfillment: `danger`.
- Parameter editing and navigation: default style.
- Unavailable payment providers: neutral label that explains the restriction, or hidden when the screen already explains the restriction. Existing callback IDs stay intact.
- “Back” returns to the previous logical step.
- “Main menu” exits the flow.
- “Cancel” cancels the operation and remains visually separate.
- Long rows are avoided on narrow Telegram clients.

The Gifts flow keeps all required financial steps but reduces redundant back actions to the prior logical step plus a main-menu escape.

## Main menu and start behavior

The menu stays compact for returning users. It shows product purpose, safe display name, and current balance without repeating onboarding instructions on every `/start`.

Product actions stay immediately available. Account/support utilities receive lower visual priority. Existing deep-link routing and stack-reset semantics remain unchanged.

## Status, errors, and empty states

Errors answer:

1. What happened.
2. What happened to funds/order state.
3. What the user can do now.

Provider exceptions, traceback text, secrets, and raw responses never enter storefront messages. Admin diagnostics may include sanitized details inside expandable blocks.

Success messages state the result, recipient, amount/product, and next location where useful. Processing messages do not promise an unknown completion time. Empty screens explain how to create the first item and expose an appropriate next action.

## Emoji strategy

Use `ttstars_interface_emoji.py` as the documented source for the verified TTStars sticker-set mapping. Keep `premium_emoji.py` as a compatibility/semantic alias layer for existing imports and for provider/gift IDs that are not part of the base interface set.

Define a compact semantic set for success, error, warning, waiting, info, navigation, user, balance, Stars, Premium, gifts, receipts/history, settings, and destructive actions. Do not duplicate a Unicode emoji in button text when a custom icon is already attached.

Every `<tg-emoji>` keeps a meaningful Unicode fallback. IDs are not invented. Eligibility of the production bot is reported only after a real, non-paid API rendering test or as unconfirmed if no safe test chat is available.

## Banners and message lifecycle

Keep current banners and localized asset routing. Keep important information in text, not only in images. Test caption length because banner-backed windows use caption limits.

Continue editing messages for navigation, pagination, and parameter changes. Continue sending new messages for checkout links, payment/delivery results, check receipt notifications, broadcasts, and other events that must remain in chat history.

## Testing

Add automated coverage for:

- Fluent parsing for every file;
- identical locale file/key/placeholder topology;
- representative and boundary rendering;
- hostile text containing `<`, `>`, `&`, quotes, and partial tags;
- Telegram HTML allowlists and balanced tags for normal and rich profiles;
- 4096-character text and 1024-character caption limits after entity removal;
- callback-data UTF-8 length up to 64 bytes;
- practical mobile button-label length;
- a navigation/next-action path for every window;
- preservation of state and callback identifiers;
- semantic danger-button usage;
- meaningful custom emoji fallbacks;
- prevention of nested code/spoiler identifier markup.

Run the full unit suite, integration suite when infrastructure is available, Ruff, format check, mypy, Pyright, and compileall. Compare callback IDs and state declarations against the baseline before accepting the change.

## Telegram verification

After static and automated verification, use a safe non-paid production/test call only if a known admin test chat is available. Verify custom emoji in message text and a button, button color, banner caption rendering, and message editing. Delete the test message afterward where practical. Never output or log the bot token.

Do not perform real purchases, payouts, check redemption, balance changes, or provider transactions.

## Delivery sequence

1. Add UI/i18n safety tests that expose current failures.
2. Introduce safe HTML helpers and fix high-risk dynamic output.
3. Normalize status/error/empty-state messages across locales.
4. Improve menu, checkout, Gifts, checks/history, Stars selling, and admin copy/navigation.
5. Correct button styles without changing callback contracts.
6. Consolidate emoji ownership and validate fallbacks.
7. Run the full automated gate and review the final diff for behavior changes.
8. Perform the safe Telegram rendering check if access can be confirmed.

## Acceptance criteria

- All three locales remain structurally and semantically aligned.
- User/external strings cannot alter Telegram HTML.
- Normal captions and messages use only supported markup and stay within limits.
- Storefront Russian consistently uses “ты”.
- Errors, success states, processing states, and empty states are distinct and actionable.
- Navigation is predictable and every window has a valid next action or exit.
- `danger` represents destructive behavior only.
- Callback IDs, callback data, deep links, states, financial services, and calculations remain unchanged.
- Custom emoji retain meaningful Unicode fallback and their actual production eligibility is reported accurately.
- Existing and new checks pass, or unrelated baseline failures are documented separately.

messages-admin_users_menu =
    <blockquote><b>👤 Users</b></blockquote>

    Available actions: manage user balance and lookup user contact.

messages-admin_users_add_balance_prompt =
    Format:
    <code>123456789 10</code>
    <code>123456789 -10</code>
    <code>123456789 clear</code>

    Where:
    • first value — user ID
    • second value — amount in USD (with + or - sign) or <code>clear</code>

messages-admin_users_add_balance_invalid = <blockquote>❌ Invalid format. Examples: <code>123456789 10</code>, <code>123456789 -10</code>, <code>123456789 clear</code>.</blockquote>
messages-admin_users_lookup_prompt =
    Format:
    <code>123456789</code>

    Where:
    • value — Telegram user ID
messages-admin_users_lookup_invalid = <blockquote>❌ Invalid format. Example: <code>123456789</code>.</blockquote>
messages-admin_users_lookup_done =
    <blockquote>✅ User contact found</blockquote>

    • ID: <code>{ $user_id }</code>
    • Contact: { $mention }
    • Link: <code>{ $user_url }</code>
    • Language: <code>{ $language }</code> (<code>{ $language_code }</code>)
    • Balance: <code>{ $balance } USD</code>
    • Referral balance: <code>{ $referral_balance } USD</code>
    • Referral earned: <code>{ $referral_earned } USD</code>
    • Referrer ID: <code>{ $referrer_id }</code>
    • Bot blocked: <code>{ $blocked }</code>
    • Blocked since: <code>{ $blocked_at }</code>
messages-admin_users_not_found = <blockquote>❌ User <code>{ $user_id }</code> not found.</blockquote>
messages-admin_users_add_balance_done = <blockquote>✅ Added <b>{ $amount } USD</b> to <code>{ $user_id }</code>. New balance: <b>{ $balance } USD</b>.</blockquote>
messages-admin_users_subtract_balance_done = <blockquote>✅ Subtracted <b>{ $amount } USD</b> from <code>{ $user_id }</code>. New balance: <b>{ $balance } USD</b>.</blockquote>
messages-admin_users_clear_balance_done = <blockquote>✅ Cleared balance for <code>{ $user_id }</code>. New balance: <b>{ $balance } USD</b>.</blockquote>

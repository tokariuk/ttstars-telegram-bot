messages-admin_users_menu =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Users</b></blockquote>

    Available actions: manage user balance and lookup user contact.

messages-admin_users_add_balance_prompt =
    <blockquote><b><tg-emoji emoji-id="5381926933393085632">👛</tg-emoji> User balance</b></blockquote>

    Format:
    <code>123456789 10</code>
    <code>123456789 -10</code>
    <code>123456789 clear</code>

    Where:
    • first value — user ID
    • second value — amount in USD (with + or - sign) or <code>clear</code>

    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> The change is applied immediately. Verify the user ID and amount before sending.</blockquote>

messages-admin_users_add_balance_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Invalid format. Examples: <code>123456789 10</code>, <code>123456789 -10</code>, <code>123456789 clear</code>.</blockquote>
messages-admin_users_lookup_prompt =
    <blockquote><b><tg-emoji emoji-id="5382299169618696812">🔎</tg-emoji> Find user</b></blockquote>

    Format:
    <code>123456789</code>

    Where:
    • value — Telegram user ID
messages-admin_users_lookup_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Invalid format. Example: <code>123456789</code>.</blockquote>
messages-admin_users_lookup_done =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> User found</b></blockquote>

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
messages-admin_users_not_found = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> User <code>{ $user_id }</code> was not found.</blockquote>
messages-admin_users_add_balance_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Added <b>{ $amount } USD</b> to <code>{ $user_id }</code>. New balance: <b>{ $balance } USD</b>.</blockquote>
messages-admin_users_subtract_balance_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Subtracted <b>{ $amount } USD</b> from <code>{ $user_id }</code>. New balance: <b>{ $balance } USD</b>.</blockquote>
messages-admin_users_clear_balance_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Cleared balance for <code>{ $user_id }</code>. New balance: <b>{ $balance } USD</b>.</blockquote>

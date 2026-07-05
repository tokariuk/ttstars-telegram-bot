messages-admin_users_menu =
    <blockquote><b>👤 Користувачі</b></blockquote>

    Наразі доступно: керування балансом і перегляд контакту користувача.

messages-admin_users_add_balance_prompt =
    Формат:
    <code>123456789 10</code>
    <code>123456789 -10</code>
    <code>123456789 clear</code>

    Де:
    • перше число — ID користувача
    • друге значення — сума в USD (зі знаком + або -) або <code>clear</code>

messages-admin_users_add_balance_invalid = <blockquote>❌ Некоректний формат. Приклади: <code>123456789 10</code>, <code>123456789 -10</code>, <code>123456789 clear</code>.</blockquote>
messages-admin_users_lookup_prompt =
    Формат:
    <code>123456789</code>

    Де:
    • значення — ID користувача Telegram
messages-admin_users_lookup_invalid = <blockquote>❌ Некоректний формат. Приклад: <code>123456789</code>.</blockquote>
messages-admin_users_lookup_done =
    <blockquote>✅ Контакт користувача знайдено</blockquote>

    • ID: <code>{ $user_id }</code>
    • Контакт: { $mention }
    • Посилання: <code>{ $user_url }</code>
    • Мова: <code>{ $language }</code> (<code>{ $language_code }</code>)
    • Баланс: <code>{ $balance } USD</code>
    • Реферальний баланс: <code>{ $referral_balance } USD</code>
    • Зароблено по рефералах: <code>{ $referral_earned } USD</code>
    • Referrer ID: <code>{ $referrer_id }</code>
    • Заблокував бота: <code>{ $blocked }</code>
    • Заблоковано з: <code>{ $blocked_at }</code>
messages-admin_users_not_found = <blockquote>❌ Користувача <code>{ $user_id }</code> не знайдено.</blockquote>
messages-admin_users_add_balance_done = <blockquote>✅ Додано <b>{ $amount } USD</b> користувачу <code>{ $user_id }</code>. Новий баланс: <b>{ $balance } USD</b>.</blockquote>
messages-admin_users_subtract_balance_done = <blockquote>✅ Знято <b>{ $amount } USD</b> у користувача <code>{ $user_id }</code>. Новий баланс: <b>{ $balance } USD</b>.</blockquote>
messages-admin_users_clear_balance_done = <blockquote>✅ Баланс користувача <code>{ $user_id }</code> очищено. Новий баланс: <b>{ $balance } USD</b>.</blockquote>

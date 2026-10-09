messages-admin_users_menu =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Користувачі</b></blockquote>

    Наразі доступно: керування балансом і перегляд контакту користувача.

messages-admin_users_add_balance_prompt =
    <blockquote><b><tg-emoji emoji-id="5381926933393085632">👛</tg-emoji> Баланс користувача</b></blockquote>

    Формат:
    <code>123456789 10</code>
    <code>123456789 -10</code>
    <code>123456789 clear</code>

    Де:
    • перше число — ID користувача
    • друге значення — сума в USD (зі знаком + або -) або <code>clear</code>

    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Зміна застосовується одразу. Перед надсиланням перевір ID і суму.</blockquote>

messages-admin_users_add_balance_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некоректний формат. Приклади: <code>123456789 10</code>, <code>123456789 -10</code>, <code>123456789 clear</code>.</blockquote>
messages-admin_users_lookup_prompt =
    <blockquote><b><tg-emoji emoji-id="5382299169618696812">🔎</tg-emoji> Пошук користувача</b></blockquote>

    Формат:
    <code>123456789</code>

    Де:
    • значення — ID користувача Telegram
messages-admin_users_lookup_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некоректний формат. Приклад: <code>123456789</code>.</blockquote>
messages-admin_users_lookup_done =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Користувача знайдено</b></blockquote>

    • ID: <code>{ $user_id }</code>
    • Контакт: { $mention }
    • Посилання: <code>{ $user_url }</code>
    • Мова: <code>{ $language }</code> (<code>{ $language_code }</code>)
    • Баланс: <code>{ $balance } USD</code>
    • Реферальний баланс: <code>{ $referral_balance } USD</code>
    • Зароблено по рефералах: <code>{ $referral_earned } USD</code>
    • ID запрошувача: <code>{ $referrer_id }</code>
    • Заблокував бота: <code>{ $blocked }</code>
    • Заблоковано з: <code>{ $blocked_at }</code>
messages-admin_users_not_found = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Користувача <code>{ $user_id }</code> не знайдено.</blockquote>
messages-admin_users_add_balance_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Додано <b>{ $amount } USD</b> користувачу <code>{ $user_id }</code>. Новий баланс: <b>{ $balance } USD</b>.</blockquote>
messages-admin_users_subtract_balance_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Знято <b>{ $amount } USD</b> у користувача <code>{ $user_id }</code>. Новий баланс: <b>{ $balance } USD</b>.</blockquote>
messages-admin_users_clear_balance_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Баланс користувача <code>{ $user_id }</code> очищено. Новий баланс: <b>{ $balance } USD</b>.</blockquote>

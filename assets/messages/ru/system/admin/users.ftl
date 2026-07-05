messages-admin_users_menu =
    <blockquote><b>👤 Пользователи</b></blockquote>

    Сейчас доступно: управление балансом и просмотр контакта пользователя.

messages-admin_users_add_balance_prompt =
    Формат:
    <code>123456789 10</code>
    <code>123456789 -10</code>
    <code>123456789 clear</code>

    Где:
    • первое значение — ID пользователя
    • второе значение — сумма в USD (со знаком + или -) или <code>clear</code>

messages-admin_users_add_balance_invalid = <blockquote>❌ Некорректный формат. Примеры: <code>123456789 10</code>, <code>123456789 -10</code>, <code>123456789 clear</code>.</blockquote>
messages-admin_users_lookup_prompt =
    Формат:
    <code>123456789</code>

    Где:
    • значение — Telegram ID пользователя
messages-admin_users_lookup_invalid = <blockquote>❌ Некорректный формат. Пример: <code>123456789</code>.</blockquote>
messages-admin_users_lookup_done =
    <blockquote>✅ Контакт пользователя найден</blockquote>

    • ID: <code>{ $user_id }</code>
    • Контакт: { $mention }
    • Ссылка: <code>{ $user_url }</code>
    • Язык: <code>{ $language }</code> (<code>{ $language_code }</code>)
    • Баланс: <code>{ $balance } USD</code>
    • Реферальный баланс: <code>{ $referral_balance } USD</code>
    • Заработано по рефералам: <code>{ $referral_earned } USD</code>
    • Referrer ID: <code>{ $referrer_id }</code>
    • Заблокировал бота: <code>{ $blocked }</code>
    • Заблокирован с: <code>{ $blocked_at }</code>
messages-admin_users_not_found = <blockquote>❌ Пользователь <code>{ $user_id }</code> не найден.</blockquote>
messages-admin_users_add_balance_done = <blockquote>✅ Добавлено <b>{ $amount } USD</b> пользователю <code>{ $user_id }</code>. Новый баланс: <b>{ $balance } USD</b>.</blockquote>
messages-admin_users_subtract_balance_done = <blockquote>✅ Списано <b>{ $amount } USD</b> у пользователя <code>{ $user_id }</code>. Новый баланс: <b>{ $balance } USD</b>.</blockquote>
messages-admin_users_clear_balance_done = <blockquote>✅ Баланс пользователя <code>{ $user_id }</code> очищен. Новый баланс: <b>{ $balance } USD</b>.</blockquote>

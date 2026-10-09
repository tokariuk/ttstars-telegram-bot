messages-admin_users_menu =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Пользователи</b></blockquote>

    Сейчас доступно: управление балансом и просмотр контакта пользователя.

messages-admin_users_add_balance_prompt =
    <blockquote><b><tg-emoji emoji-id="5381926933393085632">👛</tg-emoji> Баланс пользователя</b></blockquote>

    Формат:
    <code>123456789 10</code>
    <code>123456789 -10</code>
    <code>123456789 clear</code>

    Где:
    • первое значение — ID пользователя
    • второе значение — сумма в USD (со знаком + или -) или <code>clear</code>

    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Изменение применяется сразу. Перед отправкой проверь ID и сумму.</blockquote>

messages-admin_users_add_balance_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некорректный формат. Примеры: <code>123456789 10</code>, <code>123456789 -10</code>, <code>123456789 clear</code>.</blockquote>
messages-admin_users_lookup_prompt =
    <blockquote><b><tg-emoji emoji-id="5382299169618696812">🔎</tg-emoji> Поиск пользователя</b></blockquote>

    Формат:
    <code>123456789</code>

    Где:
    • значение — Telegram ID пользователя
messages-admin_users_lookup_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некорректный формат. Пример: <code>123456789</code>.</blockquote>
messages-admin_users_lookup_done =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Пользователь найден</b></blockquote>

    • ID: <code>{ $user_id }</code>
    • Контакт: { $mention }
    • Ссылка: <code>{ $user_url }</code>
    • Язык: <code>{ $language }</code> (<code>{ $language_code }</code>)
    • Баланс: <code>{ $balance } USD</code>
    • Реферальный баланс: <code>{ $referral_balance } USD</code>
    • Заработано по рефералам: <code>{ $referral_earned } USD</code>
    • ID пригласившего: <code>{ $referrer_id }</code>
    • Заблокировал бота: <code>{ $blocked }</code>
    • Заблокирован с: <code>{ $blocked_at }</code>
messages-admin_users_not_found = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Пользователь <code>{ $user_id }</code> не найден.</blockquote>
messages-admin_users_add_balance_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Добавлено <b>{ $amount } USD</b> пользователю <code>{ $user_id }</code>. Новый баланс: <b>{ $balance } USD</b>.</blockquote>
messages-admin_users_subtract_balance_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Списано <b>{ $amount } USD</b> у пользователя <code>{ $user_id }</code>. Новый баланс: <b>{ $balance } USD</b>.</blockquote>
messages-admin_users_clear_balance_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Баланс пользователя <code>{ $user_id }</code> очищен. Новый баланс: <b>{ $balance } USD</b>.</blockquote>

messages-stars_recipient_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Покупка Stars · Шаг 1/3</b></blockquote>

    Укажи username аккаунта, на который нужно отправить Stars.

    <b>Формат:</b> <code>@username</code>

messages-stars_amount_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Покупка Stars · Шаг 2/3</b></blockquote>

    Введи количество Stars для заказа.

    <b>Минимум:</b> <code>{ $min_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    <b>Максимум:</b> <code>{ $max_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    <b>Доступно по балансу:</b> <code>{ $balance_for_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> · (<code>{ $balance_for_stars_usd } USD</code>)

messages-stars_payment_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Покупка Stars · Шаг 3/3</b></blockquote>

    Проверь данные перед оплатой.

    <b>Получатель:</b> <code>{ $recipient }</code>
    <b>Количество:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    <b>Сумма:</b> <code>{ $amount } USD</code>
    <b>Баланс:</b> <code>{ $balance } USD</code>

messages-stars_count_invalid =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Количество должно быть в диапазоне <b>{ $min_stars }</b> – <b>{ $max_stars }</b>.</blockquote>

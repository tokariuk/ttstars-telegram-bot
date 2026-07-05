messages-stars_recipient_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Купівля Stars · Крок 1/3</b></blockquote>

    Вкажи username акаунта, на який потрібно надіслати Stars.

    <b>Формат:</b> <code>@username</code>

messages-stars_amount_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Купівля Stars · Крок 2/3</b></blockquote>

    Введи кількість Stars для цього замовлення.

    <b>Мінімум:</b> <code>{ $min_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    <b>Максимум:</b> <code>{ $max_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    <b>Доступно за балансом:</b> <code>{ $balance_for_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> · (<code>{ $balance_for_stars_usd } USD</code>)

messages-stars_payment_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Купівля Stars · Крок 3/3</b></blockquote>

    Перевір дані перед оплатою.

    <b>Отримувач:</b> <code>{ $recipient }</code>
    <b>Кількість:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    <b>Сума:</b> <code>{ $amount } USD</code>

    <b>Баланс:</b> <code>{ $balance } USD</code>

messages-stars_count_invalid =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Кількість має бути в діапазоні <b>{ $min_stars }</b> – <b>{ $max_stars }</b>.</blockquote>

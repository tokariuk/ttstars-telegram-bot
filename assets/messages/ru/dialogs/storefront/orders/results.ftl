messages-order_result_completed_topup =
    <tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Пополнение баланса выполнено.
    Зачислено: <mark>{ $amount } USD</mark>

messages-order_result_completed_gift =
    <tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Подарок Telegram отправлен.
    Получатель ID: <code>{ $recipient_user_id }</code>
    Сумма: <mark>{ $amount_usd } USD</mark>

messages-order_result_completed_premium =
    <tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Подарок Telegram Premium отправлен.
    Получатель: <code>@{ $recipient }</code>
    Период: <mark>{ $premium_months }</mark> мес.{ $tx_line }

messages-order_result_completed_stars =
    <tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Оплата подтверждена. Звезды уже отправлены.
    Получатель: <code>@{ $recipient }</code>
    Количество: <mark>{ $stars_count }</mark>{ $tx_line }

messages-order_result_failed_topup =
    <tg-emoji emoji-id="5382282191612978286">❓</tg-emoji> Оплата подтверждена, но пополнение еще обрабатывается.
    <tg-emoji emoji-id="5381926933393085632">💰</tg-emoji> Если статус не обновится, обратись в поддержку.

messages-order_result_failed_gift =
    <tg-emoji emoji-id="5382282191612978286">❓</tg-emoji> Оплата подтверждена, но отправка подарка не завершилась.
    <tg-emoji emoji-id="5381926933393085632">💰</tg-emoji> На баланс возвращено: <mark>{ $amount_usd } USD</mark>.

messages-order_result_failed_premium =
    <tg-emoji emoji-id="5382282191612978286">❓</tg-emoji> Оплата подтверждена, но отправка Premium не завершилась.
    <tg-emoji emoji-id="5381926933393085632">💰</tg-emoji> На баланс возвращено: <mark>{ $amount_usd } USD</mark>.

messages-order_result_failed_stars =
    <tg-emoji emoji-id="5382282191612978286">❓</tg-emoji> Оплата подтверждена, но отправка звезд не завершилась.
    <tg-emoji emoji-id="5381926933393085632">💰</tg-emoji> На баланс возвращено: <mark>{ $amount_usd } USD</mark>.

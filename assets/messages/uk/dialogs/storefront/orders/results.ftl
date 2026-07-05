messages-order_result_completed_topup =
    <tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Поповнення балансу виконано.
    Зараховано: <mark>{ $amount } USD</mark>

messages-order_result_completed_gift =
    <tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Подарунок Telegram відправлено.
    Отримувач ID: <code>{ $recipient_user_id }</code>
    Сума: <mark>{ $amount_usd } USD</mark>

messages-order_result_completed_premium =
    <tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Подарунок Telegram Premium відправлено.
    Отримувач: <code>@{ $recipient }</code>
    Період: <mark>{ $premium_months }</mark> міс.{ $tx_line }

messages-order_result_completed_stars =
    <tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Оплату підтверджено. Зірки вже відправлено.
    Отримувач: <code>@{ $recipient }</code>
    Кількість: <mark>{ $stars_count }</mark>{ $tx_line }

messages-order_result_failed_topup =
    <tg-emoji emoji-id="5382282191612978286">❓</tg-emoji> Оплату підтверджено, але поповнення ще обробляється.
    <tg-emoji emoji-id="5381926933393085632">💰</tg-emoji> Якщо стан не оновиться, звернись у підтримку.

messages-order_result_failed_gift =
    <tg-emoji emoji-id="5382282191612978286">❓</tg-emoji> Оплату підтверджено, але відправка подарунка не завершилась.
    <tg-emoji emoji-id="5381926933393085632">💰</tg-emoji> На баланс повернуто: <mark>{ $amount_usd } USD</mark>.

messages-order_result_failed_premium =
    <tg-emoji emoji-id="5382282191612978286">❓</tg-emoji> Оплату підтверджено, але відправка Premium не завершилась.
    <tg-emoji emoji-id="5381926933393085632">💰</tg-emoji> На баланс повернуто: <mark>{ $amount_usd } USD</mark>.

messages-order_result_failed_stars =
    <tg-emoji emoji-id="5382282191612978286">❓</tg-emoji> Оплату підтверджено, але відправка зірок не завершилась.
    <tg-emoji emoji-id="5381926933393085632">💰</tg-emoji> На баланс повернуто: <mark>{ $amount_usd } USD</mark>.

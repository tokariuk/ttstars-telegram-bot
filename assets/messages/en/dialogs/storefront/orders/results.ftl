messages-order_result_completed_topup =
    <tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Balance top-up completed.
    Credited: <mark>{ $amount } USD</mark>

messages-order_result_completed_gift =
    <tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Telegram gift sent.
    Recipient ID: <code>{ $recipient_user_id }</code>
    Amount: <mark>{ $amount_usd } USD</mark>

messages-order_result_completed_premium =
    <tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Telegram Premium gift sent.
    Recipient: <code>@{ $recipient }</code>
    Period: <mark>{ $premium_months }</mark> months{ $tx_line }

messages-order_result_completed_stars =
    <tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Payment confirmed. Stars were delivered.
    Recipient: <code>@{ $recipient }</code>
    Amount: <mark>{ $stars_count }</mark>{ $tx_line }

messages-order_result_failed_topup =
    <tg-emoji emoji-id="5382282191612978286">❓</tg-emoji> Payment is confirmed, but top-up is still processing.
    <tg-emoji emoji-id="5381926933393085632">💰</tg-emoji> If status does not update, contact support.

messages-order_result_failed_gift =
    <tg-emoji emoji-id="5382282191612978286">❓</tg-emoji> Payment is confirmed, but gift delivery did not finish.
    <tg-emoji emoji-id="5381926933393085632">💰</tg-emoji> Refunded to your balance: <mark>{ $amount_usd } USD</mark>.

messages-order_result_failed_premium =
    <tg-emoji emoji-id="5382282191612978286">❓</tg-emoji> Payment is confirmed, but Premium delivery did not finish.
    <tg-emoji emoji-id="5381926933393085632">💰</tg-emoji> Refunded to your balance: <mark>{ $amount_usd } USD</mark>.

messages-order_result_failed_stars =
    <tg-emoji emoji-id="5382282191612978286">❓</tg-emoji> Payment is confirmed, but stars delivery did not finish.
    <tg-emoji emoji-id="5381926933393085632">💰</tg-emoji> Refunded to your balance: <mark>{ $amount_usd } USD</mark>.

messages-order_checkout_message_stars =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Оплата · Stars</b></blockquote>

    <table>
    <tr><td>Получатель</td><td><code>@{ $recipient }</code></td></tr>
    <tr><td>Количество</td><td><code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji></td></tr>
    <tr><td>Сумма заказа</td><td><code>{ $amount } USD</code></td></tr>
    <tr><td>Комиссия</td><td><code>{ $fee_text }</code></td></tr>
    <tr><th>К оплате</th><td><mark>{ $pay_amount } USD</mark></td></tr>
    </table>

messages-order_checkout_message_premium =
    <blockquote><b><tg-emoji emoji-id="5380078671526666610">⭐</tg-emoji> Оплата · Premium</b></blockquote>

    <table>
    <tr><td>Получатель</td><td><code>@{ $recipient }</code></td></tr>
    <tr><td>Пакет</td><td><code>{ $months }</code> мес.</td></tr>
    <tr><td>Сумма заказа</td><td><code>{ $amount } USD</code></td></tr>
    <tr><td>Комиссия</td><td><code>{ $fee_text }</code></td></tr>
    <tr><th>К оплате</th><td><mark>{ $pay_amount } USD</mark></td></tr>
    </table>

messages-order_checkout_message_topup =
    <blockquote><b><tg-emoji emoji-id="5379761711530163623">⭐</tg-emoji> Оплата · Пополнение</b></blockquote>

    <table>
    <tr><td>К зачислению</td><td><code>{ $amount } USD</code></td></tr>
    <tr><td>Комиссия</td><td><code>{ $fee_text }</code></td></tr>
    <tr><th>К оплате</th><td><mark>{ $pay_amount } USD</mark></td></tr>
    </table>

messages-order_checkout_message_gift =
    <blockquote><b><tg-emoji emoji-id="5379759198974289129">🎁</tg-emoji> Оплата · Подарок</b></blockquote>

    <table>
    <tr><td>Получатель</td><td><code>{ $recipient_id }</code></td></tr>
    <tr><td>Подарок</td><td><code>{ $gift }</code></td></tr>
    <tr><td>Подпись</td><td><code>{ $message }</code></td></tr>
    <tr><td>Отправитель</td><td><code>{ $sender_visibility }</code></td></tr>
    <tr><td>Сумма заказа</td><td><code>{ $amount } USD</code></td></tr>
    <tr><td>Комиссия</td><td><code>{ $fee_text }</code></td></tr>
    <tr><th>К оплате</th><td><mark>{ $pay_amount } USD</mark></td></tr>
    </table>

messages-order_checkout_send_failed =
    <blockquote><b><tg-emoji emoji-id="5381932538325404900">⭐</tg-emoji> Требуется проверка</b></blockquote>

    Инвойс создан, но checkout-сообщение не отправлено.

messages-payment_provider_unavailable =
    <blockquote><b><tg-emoji emoji-id="5381932538325404900">⭐</tg-emoji> Требуется проверка</b></blockquote>

    Этот способ оплаты временно недоступен.

messages-balance_not_enough =
    <blockquote><b><tg-emoji emoji-id="5381932538325404900">⭐</tg-emoji> Требуется проверка</b></blockquote>

    Недостаточно средств на балансе.

messages-order_checkout_canceled_note =
    <blockquote><b><tg-emoji emoji-id="5381932538325404900">⭐</tg-emoji> Отменено</b></blockquote>

    Этот заказ закрыт.

messages-order_checkout_message_stars =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Оплата · Stars</b></blockquote>

    <table>
    <tr><td>Отримувач</td><td><code>@{ $recipient }</code></td></tr>
    <tr><td>Кількість</td><td><code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji></td></tr>
    <tr><td>Сума замовлення</td><td><code>{ $amount } USD</code></td></tr>
    <tr><td>Комісія</td><td><code>{ $fee_text }</code></td></tr>
    <tr><th>До оплати</th><td><mark>{ $pay_amount } USD</mark></td></tr>
    </table>

messages-order_checkout_message_premium =
    <blockquote><b><tg-emoji emoji-id="5380078671526666610">⭐</tg-emoji> Оплата · Premium</b></blockquote>

    <table>
    <tr><td>Отримувач</td><td><code>@{ $recipient }</code></td></tr>
    <tr><td>Пакет</td><td><code>{ $months }</code> міс.</td></tr>
    <tr><td>Сума замовлення</td><td><code>{ $amount } USD</code></td></tr>
    <tr><td>Комісія</td><td><code>{ $fee_text }</code></td></tr>
    <tr><th>До оплати</th><td><mark>{ $pay_amount } USD</mark></td></tr>
    </table>

messages-order_checkout_message_topup =
    <blockquote><b><tg-emoji emoji-id="5379761711530163623">⭐</tg-emoji> Оплата · Поповнення</b></blockquote>

    <table>
    <tr><td>До зарахування</td><td><code>{ $amount } USD</code></td></tr>
    <tr><td>Комісія</td><td><code>{ $fee_text }</code></td></tr>
    <tr><th>До оплати</th><td><mark>{ $pay_amount } USD</mark></td></tr>
    </table>

messages-order_checkout_message_gift =
    <blockquote><b><tg-emoji emoji-id="5379759198974289129">🎁</tg-emoji> Оплата · Подарунок</b></blockquote>

    <table>
    <tr><td>Отримувач</td><td><code>{ $recipient_id }</code></td></tr>
    <tr><td>Подарунок</td><td><code>{ $gift }</code></td></tr>
    <tr><td>Підпис</td><td><code>{ $message }</code></td></tr>
    <tr><td>Відправник</td><td><code>{ $sender_visibility }</code></td></tr>
    <tr><td>Сума замовлення</td><td><code>{ $amount } USD</code></td></tr>
    <tr><td>Комісія</td><td><code>{ $fee_text }</code></td></tr>
    <tr><th>До оплати</th><td><mark>{ $pay_amount } USD</mark></td></tr>
    </table>

messages-order_checkout_send_failed =
    <blockquote><b><tg-emoji emoji-id="5381932538325404900">⭐</tg-emoji> Потрібна перевірка</b></blockquote>

    Інвойс створено, але checkout-повідомлення не надійшло.

messages-payment_provider_unavailable =
    <blockquote><b><tg-emoji emoji-id="5381932538325404900">⭐</tg-emoji> Потрібна перевірка</b></blockquote>

    Цей метод оплати тимчасово недоступний.

messages-balance_not_enough =
    <blockquote><b><tg-emoji emoji-id="5381932538325404900">⭐</tg-emoji> Потрібна перевірка</b></blockquote>

    На балансі недостатньо коштів.

messages-order_checkout_canceled_note =
    <blockquote><b><tg-emoji emoji-id="5381932538325404900">⭐</tg-emoji> Скасовано</b></blockquote>

    Це замовлення закрито.

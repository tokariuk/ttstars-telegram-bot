messages-order_checkout_message_stars =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Payment · Stars</b></blockquote>

    <table>
    <tr><td>Recipient</td><td><code>@{ $recipient }</code></td></tr>
    <tr><td>Stars</td><td><code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji></td></tr>
    <tr><td>Order sum</td><td><code>{ $amount } USD</code></td></tr>
    <tr><td>Fee</td><td><code>{ $fee_text }</code></td></tr>
    <tr><th>To pay</th><td><mark>{ $pay_amount } USD</mark></td></tr>
    </table>

messages-order_checkout_message_premium =
    <blockquote><b><tg-emoji emoji-id="5380078671526666610">⭐</tg-emoji> Payment · Premium</b></blockquote>

    <table>
    <tr><td>Recipient</td><td><code>@{ $recipient }</code></td></tr>
    <tr><td>Plan</td><td><code>{ $months }</code> months</td></tr>
    <tr><td>Order sum</td><td><code>{ $amount } USD</code></td></tr>
    <tr><td>Fee</td><td><code>{ $fee_text }</code></td></tr>
    <tr><th>To pay</th><td><mark>{ $pay_amount } USD</mark></td></tr>
    </table>

messages-order_checkout_message_topup =
    <blockquote><b><tg-emoji emoji-id="5379761711530163623">⭐</tg-emoji> Payment · Top-up</b></blockquote>

    <table>
    <tr><td>To be credited</td><td><code>{ $amount } USD</code></td></tr>
    <tr><td>Fee</td><td><code>{ $fee_text }</code></td></tr>
    <tr><th>To pay</th><td><mark>{ $pay_amount } USD</mark></td></tr>
    </table>

messages-order_checkout_message_gift =
    <blockquote><b><tg-emoji emoji-id="5379759198974289129">🎁</tg-emoji> Payment · Gift</b></blockquote>

    <table>
    <tr><td>Recipient</td><td><code>{ $recipient_id }</code></td></tr>
    <tr><td>Gift</td><td><code>{ $gift }</code></td></tr>
    <tr><td>Message</td><td><code>{ $message }</code></td></tr>
    <tr><td>Sender</td><td><code>{ $sender_visibility }</code></td></tr>
    <tr><td>Order amount</td><td><code>{ $amount } USD</code></td></tr>
    <tr><td>Fee</td><td><code>{ $fee_text }</code></td></tr>
    <tr><th>To pay</th><td><mark>{ $pay_amount } USD</mark></td></tr>
    </table>

messages-order_checkout_send_failed =
    <blockquote><b><tg-emoji emoji-id="5381932538325404900">⭐</tg-emoji> Needs check</b></blockquote>

    Invoice created, but checkout message was not sent.

messages-payment_provider_unavailable =
    <blockquote><b><tg-emoji emoji-id="5381932538325404900">⭐</tg-emoji> Needs check</b></blockquote>

    This payment method is temporarily unavailable.

messages-balance_not_enough =
    <blockquote><b><tg-emoji emoji-id="5381932538325404900">⭐</tg-emoji> Needs check</b></blockquote>

    Not enough balance.

messages-order_checkout_canceled_note =
    <blockquote><b><tg-emoji emoji-id="5381932538325404900">⭐</tg-emoji> Canceled</b></blockquote>

    This order is closed.

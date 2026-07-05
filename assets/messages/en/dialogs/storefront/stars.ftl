messages-stars_recipient_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Buy Stars · Step 1/3</b></blockquote>

    Enter the username of the account that should receive Stars.

    <b>Format:</b> <code>@username</code>

messages-stars_amount_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Buy Stars · Step 2/3</b></blockquote>

    Enter Stars amount for this order.

    <b>Minimum:</b> <code>{ $min_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    <b>Maximum:</b> <code>{ $max_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    <b>Available by balance:</b> <code>{ $balance_for_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> · (<code>{ $balance_for_stars_usd } USD</code>)

messages-stars_payment_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Buy Stars · Step 3/3</b></blockquote>

    Review details before payment.

    <b>Recipient:</b> <code>{ $recipient }</code>
    <b>Amount:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    <b>Total:</b> <code>{ $amount } USD</code>
    <b>Balance:</b> <code>{ $balance } USD</code>

messages-stars_count_invalid =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Amount must be between <b>{ $min_stars }</b> and <b>{ $max_stars }</b>.</blockquote>

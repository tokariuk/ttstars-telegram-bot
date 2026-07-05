messages-gifts_recipient_screen =
    <blockquote><b><tg-emoji emoji-id="5379759198974289129">🎁</tg-emoji> Buy Telegram Gift · Step 1/5</b></blockquote>

    Enter the username of the account that should receive the gift.

    <b>Format:</b> <code>@username</code>
    <b>Current recipient:</b> <code>{ $recipient }</code>

messages-gifts_catalog_screen =
    <blockquote><b><tg-emoji emoji-id="5379759198974289129">🎁</tg-emoji> Buy Telegram Gift · Step 2/5</b></blockquote>

    Choose a gift from the list below.

    <b>Recipient:</b> <code>{ $recipient }</code>
    <b>Selected:</b> <code>{ $selected }</code>

messages-gifts_message_screen =
    <blockquote><b><tg-emoji emoji-id="5379759198974289129">🎁</tg-emoji> Buy Telegram Gift · Step 3/5</b></blockquote>

    Enter a gift message or skip this step.

    <b>Recipient:</b> <code>{ $recipient }</code>
    <b>Gift:</b> <code>{ $gift }</code>
    <b>Amount:</b> <code>{ $amount } USD</code>
    <b>Current message:</b> <code>{ $current_message }</code>

messages-gifts_sender_privacy_screen =
    <blockquote><b><tg-emoji emoji-id="5379759198974289129">🎁</tg-emoji> Buy Telegram Gift · Step 4/5</b></blockquote>

    Choose sender visibility.

    <b>Important:</b> the sender in this flow is the <b>TTStars service account</b>, not you.

    <b>Recipient:</b> <code>{ $recipient }</code>
    <b>Gift:</b> <code>{ $gift }</code>
    <b>Amount:</b> <code>{ $amount } USD</code>
    <b>Message:</b> <code>{ $message }</code>

messages-gifts_payment_screen =
    <blockquote><b><tg-emoji emoji-id="5379759198974289129">🎁</tg-emoji> Buy Telegram Gift · Step 5/5</b></blockquote>

    Review details before payment.

    <b>Recipient:</b> <code>{ $recipient }</code>
    <b>Gift:</b> <code>{ $gift }</code>
    <b>Amount:</b> <code>{ $amount } USD</code>
    <b>Message:</b> <code>{ $message }</code>
    <b>Sender visibility:</b> <code>{ $sender_visibility }</code>

    <b>Balance:</b> <code>{ $balance } USD</code>

messages-gift_sender_visible_option = Sender (TTStars service) will be visible
messages-gift_sender_private_option = Sender (TTStars service) will be hidden

messages-gift_name_new_year_tree = New Year Tree
messages-gift_name_valentine_heart = Valentine Heart
messages-gift_name_new_year_bear = New Year Bear
messages-gift_name_bear_with_heart = Bear With Heart
messages-gift_name_bear_with_bouquet = Bear With Bouquet
messages-gift_name_irish_bear = Irish Bear
messages-gift_name_clown_bear = Clown Bear
messages-gift_name_easter_bear = Easter Bear
messages-gift_name_worker_bear = Worker Bear
messages-gift_name_default_bear = Bear

messages-gift_recipient_invalid =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Invalid recipient username. Use format <code>@username</code>.</blockquote>

messages-gift_recipient_missing =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Gift recipient is not set yet.</blockquote>

messages-gift_invalid =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Gift is not selected or unavailable.</blockquote>

messages-gift_message_too_long =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Message is too long. Maximum: <b>{ $max_chars }</b> characters.</blockquote>

messages-gift_sender_visibility_required =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Select sender visibility before payment.</blockquote>

messages-gift_userbot_session_required =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Failed to verify recipient username. Please try again later.</blockquote>

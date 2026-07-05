messages-history_list_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> Operation History</b></blockquote>

    Choose an operation using the buttons below.

messages-history_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> Operation History</b></blockquote>

    No operations yet.

messages-history_operation_button = #{ $order_id } · { $product } · { $amount } USD

messages-history_page_indicator = { $current }/{ $total }

messages-history_product_stars_button = Stars { $stars }

messages-history_product_premium_button = Premium { $months } months

messages-history_product_gift_button = Gift

messages-history_product_topup_button = Top-up

messages-history_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> Operation #{ $order_id }</b></blockquote>

    <b>Status:</b> { $status }
    <b>Product:</b> { $product }
    <b>Provider:</b> { $provider }
    <b>Recipient:</b> { $recipient }
    <b>Amount:</b> <code>{ $amount } USD</code>

    <blockquote expandable><b>Technical details</b>
    <b>Created:</b> { $created }
    <b>Paid:</b> { $paid }
    <b>Fulfilled:</b> { $fulfilled }

    <b>Provider ref:</b> <code>{ $provider_ref }</code>
    <b>TX:</b> <tg-spoiler><code>{ $tx_hash }</code></tg-spoiler></blockquote>

messages-history_detail_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Operation not found or unavailable.</blockquote>

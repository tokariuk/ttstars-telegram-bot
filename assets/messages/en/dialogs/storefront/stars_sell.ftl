messages-stars_sell_days =
    { $count ->
        [one] { $count } day
       *[other] { $count } days
    }

messages-stars_sell_menu_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Stars Sale</b></blockquote>

    Create sale requests and review their history.

    <b>Price per 1 <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji></b>: <code>{ $rate_usd } USD</code>

messages-stars_sell_stars_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Stars Sale · Step 1/3</b></blockquote>

    Enter the number of stars you want to sell.

    • Minimum: <code>{ $min_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Maximum: <code>{ $max_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Payout hold: <code>{ $hold_days_text }</code>

messages-stars_sell_wallet_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Stars Sale · Step 2/3</b></blockquote>

    Enter your TON wallet (USDT) for payout.

messages-stars_sell_payment_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Stars Sale · Step 3/3</b></blockquote>

    Review details and send a stars invoice.

    • Stars: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Payout: <code>{ $payout_amount } USD</code>
    • Wallet: <code>{ $wallet }</code>
    • Hold: <code>{ $hold_days_text }</code>

messages-stars_sell_history_list_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> Requests History</b></blockquote>

    Select a request to open details.

messages-stars_sell_history_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> Requests History</b></blockquote>

    You have no sale requests yet.

messages-stars_sell_history_detail_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Request not found.</blockquote>

messages-stars_sell_history_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> Request #{ $order_id }</b></blockquote>

    • Status: <code>{ $status }</code>
    • Stars: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Payout: <code>{ $payout_amount } USD</code>
    • Wallet: <code>{ $wallet }</code>
    • Invoice amount: <code>{ $invoice_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

    <blockquote expandable><b>Timeline</b>
    • Created: { $created_at }
    • Paid: { $paid_at }
    • Payout available at: { $payout_available_at }
    • Completed: { $completed_at }
    • Rejected: { $rejected_at }
    • Refunded: { $refunded_at }

    <b>Technical details</b>
    • Invoice payload: <code>{ $invoice_payload }</code>
    • Paid in Stars: <code>{ $paid_stars }</code>
    • Failure reason: <code>{ $failure_reason }</code>
    • Resolution reason: <code>{ $resolution_reason }</code>
    • Resolution note: <code>{ $resolution_note }</code></blockquote>

messages-stars_sell_status_pending_payment = pending payment
messages-stars_sell_status_paid_hold = paid (hold)
messages-stars_sell_status_paid_hold_ready = paid (ready for payout)
messages-stars_sell_status_completed = completed
messages-stars_sell_status_canceled = canceled
messages-stars_sell_status_rejected = rejected
messages-stars_sell_status_failed = failed

messages-stars_sell_history_page_indicator = { $current }/{ $total }
messages-stars_sell_history_item_button = #{ $order_id } · { $status } · { $stars_count } Stars · { $payout_amount } USD

messages-stars_sell_stars_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Enter a positive integer (stars count).</blockquote>
messages-stars_sell_stars_out_of_range = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Stars count must be between <code>{ $min_stars }</code> and <code>{ $max_stars }</code>.</blockquote>
messages-stars_sell_wallet_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Invalid TON wallet. Use <code>UQ...</code> or <code>EQ...</code> format.</blockquote>
messages-stars_sell_stars_missing = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Set stars count first.</blockquote>
messages-stars_sell_wallet_missing = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Set payout wallet first.</blockquote>
messages-stars_sell_order_create_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Failed to create sale request. Try again later.</blockquote>
messages-stars_sell_invoice_send_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Failed to send invoice. Try again.</blockquote>
messages-stars_sell_invoice_sent = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Stars invoice sent. Request: <code>{ $order_id }</code>.</blockquote>
messages-stars_sell_invoice_resent = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> New invoice sent for open request <code>{ $order_id }</code>.</blockquote>
messages-stars_sell_invoice_replaced = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Previous unpaid request was canceled. New request created: <code>{ $order_id }</code>.</blockquote>
messages-stars_sell_invoice_canceled = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Request canceled.</blockquote>
messages-stars_sell_invoice_cancel_unavailable = <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> This request can no longer be canceled.</blockquote>
messages-stars_sell_invoice_cancel_not_found = <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Request not found.</blockquote>

messages-stars_sell_invoice_title = Sell Telegram Stars
messages-stars_sell_invoice_description = Sell { $stars_count } Stars. After payment confirmation, payout { $payout_amount } USD will be available in { $hold_days_text }.
messages-stars_sell_invoice_label = Sell { $stars_count } Stars

messages-stars_sell_payment_confirmed =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Stars payment confirmed</b></blockquote>

    <table>
    <tr><td>Request</td><td><code>{ $order_id }</code></td></tr>
    <tr><td>Paid</td><td><code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji></td></tr>
    <tr><th>Payout</th><td><mark>{ $payout_amount } USD</mark></td></tr>
    <tr><td>Wallet</td><td><code>{ $wallet }</code></td></tr>
    <tr><td>Available after</td><td><code>{ $payout_available_at }</code></td></tr>
    <tr><td>Hold</td><td><code>{ $hold_days_text }</code></td></tr>
    </table>

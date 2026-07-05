messages-admin_stars_sell_days =
    { $count ->
        [one] { $count } day
       *[other] { $count } days
    }

messages-admin_stars_sell_menu_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Stars Sale</b></blockquote>

    Create sale requests and review their history.

    <b>Overview:</b>
    • Total requests: <code>{ $total_orders }</code>
    • Paid stars: <code>{ $total_paid_stars }</code>
    • Ready for payout: <code>{ $ready_for_payout }</code>
    • Paid out: <code>{ $completed_payout } USD</code>

messages-admin_stars_sell_stars_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Stars Sale · Step 1/3</b></blockquote>

    Enter the number of stars you want to sell.

    • Minimum: <code>{ $min_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Maximum: <code>{ $max_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Current selection: <code>{ $selected_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

    • Rate: <code>{ $rate_usd } USD</code> per 1 <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Payout hold: <code>{ $hold_days_text }</code>

messages-admin_stars_sell_wallet_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Stars Sale · Step 2/3</b></blockquote>

    Enter your TON wallet (USDT) for payout.

    • Stars: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Payout: <code>{ $payout_amount } USD</code>
    • Current wallet: <code>{ $wallet }</code>

messages-admin_stars_sell_payment_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Stars Sale · Step 3/3</b></blockquote>

    Review details and send a stars invoice.

    • Stars: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Payout: <code>{ $payout_amount } USD</code>
    • Wallet: <code>{ $wallet }</code>
    • Hold: <code>{ $hold_days_text }</code>
    • Telegram invoice amount: <code>{ $invoice_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

messages-admin_stars_sell_history_list_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Stars Sale · Requests History</b></blockquote>

    Select a request to open details.
    • Page: <code>{ $page }</code>

messages-admin_stars_sell_history_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Stars Sale · Requests History</b></blockquote>

    You have no sale requests yet.

messages-admin_stars_sell_history_detail_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Request not found.</blockquote>

messages-admin_stars_sell_history_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Stars Sale · Request #{ $order_id }</b></blockquote>

    • Status: <code>{ $status }</code>
    • Stars: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Payout: <code>{ $payout_amount } USD</code>
    • Wallet: <code>{ $wallet }</code>
    • Invoice amount: <code>{ $invoice_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

    <b>Timeline:</b>
    • Created: { $created_at }
    • Paid: { $paid_at }
    • Payout available at: { $payout_available_at }
    • Completed: { $completed_at }
    • Rejected: { $rejected_at }
    • Refunded: { $refunded_at }

    <b>Technical details:</b>
    • User ID: <code>{ $user_id }</code>
    • Invoice payload: <code>{ $invoice_payload }</code>
    • Paid in Stars: <code>{ $paid_stars }</code>
    • Failure reason: <code>{ $failure_reason }</code>
    • Resolution reason: <code>{ $resolution_reason }</code>
    • Resolution note: <code>{ $resolution_note }</code>

messages-admin_stars_sell_admin_list_screen =
    <b>Stars Sale · Requests Control</b>

    Select a request to manage.
    • Page: <code>{ $page }</code>

messages-admin_stars_sell_admin_list_empty_screen =
    <b>Stars Sale · Requests Control</b>

    No requests to manage yet.

messages-admin_stars_sell_admin_detail_not_found =
    ⚠️ Request not found.

messages-admin_stars_sell_admin_detail_screen =
    <b>Manage Request #{ $order_id }</b>

    • User ID: <code>{ $user_id }</code>
    • Status: <code>{ $status }</code>
    • Stars: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Payout: <code>{ $payout_amount } USD</code>
    • Wallet: <code>{ $wallet }</code>
    • Invoice amount: <code>{ $invoice_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

    <b>Timeline:</b>
    • Created: { $created_at }
    • Paid: { $paid_at }
    • Payout available at: { $payout_available_at }
    • Completed: { $completed_at }
    • Rejected: { $rejected_at }
    • Refunded: { $refunded_at }

    <b>Technical details:</b>
    • Invoice payload: <code>{ $invoice_payload }</code>
    • Paid in Stars: <code>{ $paid_stars }</code>
    • Failure reason: <code>{ $failure_reason }</code>
    • Resolution reason: <code>{ $resolution_reason }</code>
    • Resolution note: <code>{ $resolution_note }</code>

messages-admin_stars_sell_status_pending_payment = pending payment
messages-admin_stars_sell_status_paid_hold = paid (hold)
messages-admin_stars_sell_status_paid_hold_ready = paid (ready for payout)
messages-admin_stars_sell_status_completed = completed
messages-admin_stars_sell_status_canceled = canceled
messages-admin_stars_sell_status_rejected = rejected
messages-admin_stars_sell_status_refunded = rejected
messages-admin_stars_sell_status_failed = failed

messages-admin_stars_sell_reason_replaced_by_new_request = replaced by a new request
messages-admin_stars_sell_reason_user_request = user request
messages-admin_stars_sell_reason_invalid_payout_wallet = invalid payout wallet
messages-admin_stars_sell_reason_stars_refunded = stars refunded
messages-admin_stars_sell_reason_stars_not_withdrawable = stars not withdrawable
messages-admin_stars_sell_reason_fraud_suspected = fraud suspected
messages-admin_stars_sell_reason_kyc_or_fragment_restriction = KYC/Fragment restriction
messages-admin_stars_sell_reason_payout_technical_failure = payout technical failure
messages-admin_stars_sell_reason_policy_restriction = policy restriction
messages-admin_stars_sell_reason_other = other reason

messages-admin_stars_sell_history_page_indicator = { $current }/{ $total }
messages-admin_stars_sell_history_item_button = #{ $order_id } · { $status } · { $stars_count } stars · { $payout_amount } USD

messages-admin_stars_sell_admin_page_indicator = { $current }/{ $total }
messages-admin_stars_sell_admin_item_button = #{ $order_id } · #{ $user_id } · { $status } · { $stars_count } stars · { $payout_amount } USD

messages-admin_stars_sell_stars_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Enter a positive integer (stars count).</blockquote>
messages-admin_stars_sell_stars_out_of_range = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Stars count must be between <code>{ $min_stars }</code> and <code>{ $max_stars }</code>.</blockquote>
messages-admin_stars_sell_wallet_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Invalid TON wallet. Use <code>UQ...</code> or <code>EQ...</code> format.</blockquote>
messages-admin_stars_sell_stars_missing = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Set stars count first.</blockquote>
messages-admin_stars_sell_wallet_missing = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Set payout wallet first.</blockquote>
messages-admin_stars_sell_order_create_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Failed to create sale request. Try again later.</blockquote>
messages-admin_stars_sell_invoice_send_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Failed to send invoice. Try again.</blockquote>
messages-admin_stars_sell_invoice_sent = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Stars invoice sent. Request: <code>{ $order_id }</code>.</blockquote>
messages-admin_stars_sell_invoice_resent = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> New invoice sent for open request <code>{ $order_id }</code>.</blockquote>
messages-admin_stars_sell_invoice_replaced = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Previous unpaid request was canceled. New request created: <code>{ $order_id }</code>.</blockquote>
messages-admin_stars_sell_invoice_canceled = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Request canceled.</blockquote>
messages-admin_stars_sell_invoice_cancel_unavailable = <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> This request can no longer be canceled.</blockquote>
messages-admin_stars_sell_invoice_cancel_not_found = <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Request not found.</blockquote>

messages-admin_stars_sell_admin_action_completed = ✅ Request <code>{ $order_id }</code> marked as completed.
messages-admin_stars_sell_admin_action_rejected = ✅ Request <code>{ $order_id }</code> was rejected.
messages-admin_stars_sell_admin_action_not_ready = ⚠️ Request <code>{ $order_id }</code> is still on hold. Available after: <code>{ $payout_available_at }</code>.
messages-admin_stars_sell_admin_action_conflict = ⚠️ Request <code>{ $order_id }</code> status has changed. Refresh data.
messages-admin_stars_sell_admin_action_failed = ❌ Failed to process action for request <code>{ $order_id }</code>.

messages-admin_stars_sell_invoice_title = Sell Telegram Stars
messages-admin_stars_sell_invoice_description = Sell { $stars_count } ⭐. After payment confirmation, payout { $payout_amount } USD will be available in { $hold_days_text }.
messages-admin_stars_sell_invoice_label = Sell { $stars_count } ⭐

messages-admin_stars_sell_payment_confirmed =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Stars payment confirmed</b></blockquote>

    • Request: <code>{ $order_id }</code>
    • Paid: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Payout: <code>{ $payout_amount } USD</code>
    • Wallet: <code>{ $wallet }</code>
    • Manual payout available after: <code>{ $payout_available_at }</code>
    • Hold: <code>{ $hold_days_text }</code>

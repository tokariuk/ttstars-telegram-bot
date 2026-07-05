messages-check_item_button = #{ $check_id } · { $stars } Stars · { $amount } USD

messages-check_history_item_button = #{ $check_id } · { $status } · { $stars } Stars · { $amount } USD

messages-check_claim_username_any = Anyone

messages-check_claim_password_set = Set

messages-check_claim_password_empty = Not set

messages-checks_list_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Checks ({ $active_count })</b></blockquote>

messages-checks_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Checks</b></blockquote>

    No active checks.

messages-checks_page_indicator = { $current }/{ $total }

messages-checks_history_list_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📄</tg-emoji> Checks History ({ $total_count })</b></blockquote>

messages-checks_history_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📄</tg-emoji> Checks History</b></blockquote>

    Checks history is empty.

messages-checks_history_page_indicator = { $current }/{ $total }

messages-checks_create_stars_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Create Check · Step 1/4</b></blockquote>

    Send Stars amount.

    <b>Minimum:</b> <code>{ $min_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    <b>Maximum:</b> <code>{ $max_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

messages-checks_create_recipient_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Create Check · Step 2/4</b></blockquote>

    Send <code>@username</code> who can redeem this check, or skip this step.

messages-checks_create_password_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Create Check · Step 3/4</b></blockquote>

    Send password or skip this step.

messages-checks_create_confirm_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Create Check · Step 4/4</b></blockquote>

    <b>Amount:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<code>{ $amount } USD</code>)
    <b>Recipient:</b> <code>{ $claim_username }</code>
    <b>Password:</b> <code>{ $has_password }</code>

messages-check_detail_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Check not found or already inactive.</blockquote>

messages-check_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Check #{ $check_id }</b></blockquote>

    <b>Amount:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<code>{ $amount } USD</code>)
    <b>Recipient:</b> <code>{ $claim_username }</code>
    <b>Password:</b> <code>{ $has_password }</code>
    <b>Created:</b> { $created }

    <b>Link:</b> <code>{ $link }</code>

messages-check_history_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📄</tg-emoji> Check History #{ $check_id }</b></blockquote>

    <b>Status:</b> <code>{ $status }</code>
    <b>Amount:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<code>{ $amount } USD</code>)
    <b>Recipient:</b> <code>{ $claim_username }</code>
    <b>Password:</b> <code>{ $has_password }</code>

    <b>Link:</b> <code>{ $link }</code>

    <blockquote expandable><b>Technical details</b>
    <b>Claimer ID:</b> <code>{ $recipient_id }</code>
    <b>TX:</b> <tg-spoiler><code>{ $tx_hash }</code></tg-spoiler>
    <b>Error:</b> <code>{ $last_error }</code>
    <b>Created:</b> { $created }
    <b>Redeemed:</b> { $redeemed }
    <b>Closed:</b> { $closed }</blockquote>

messages-check_status_active = Active

messages-check_status_processing = Processing

messages-check_status_redeemed = Redeemed

messages-check_status_closed = Closed

messages-check_settings_screen =
    <blockquote><b><tg-emoji emoji-id="5381935145370559125">🧾</tg-emoji> Check Settings #{ $check_id }</b></blockquote>

    <b>Recipient:</b> <code>{ $claim_username }</code>
    <b>Password:</b> <code>{ $has_password }</code>

messages-check_settings_edit_recipient_screen =
    <blockquote><b><tg-emoji emoji-id="5381935145370559125">🧾</tg-emoji> Edit Recipient</b></blockquote>

    Send username in format <code>@username</code>.

messages-check_settings_edit_password_screen =
    <blockquote><b><tg-emoji emoji-id="5381935145370559125">🧾</tg-emoji> Edit Password</b></blockquote>

    Send a new password.

messages-check_create_done =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Check created.</blockquote>

messages-check_create_failed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Failed to create check.</blockquote>

messages-check_create_stars_invalid =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Amount must be between <b>{ $min_stars }</b> and <b>{ $max_stars }</b>.</blockquote>

messages-check_create_password_invalid =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Password cannot be empty.</blockquote>

messages-check_settings_recipient_saved =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Recipient updated.</blockquote>

messages-check_settings_recipient_cleared =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Recipient restriction removed.</blockquote>

messages-check_settings_password_saved =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Password updated.</blockquote>

messages-check_settings_password_cleared =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Password removed.</blockquote>

messages-check_close_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Check not found or unavailable.</blockquote>

messages-check_close_done =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Check closed. Funds returned to balance.</blockquote>

messages-check_close_already_redeemed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Check already redeemed.</blockquote>

messages-check_close_already_closed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> This check is already closed.</blockquote>

messages-check_close_processing =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Check is already processing.</blockquote>

messages-check_claim_done_stars =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Delivered: <b>{ $stars }</b> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> · TX: <tg-spoiler><code>{ $tx_hash }</code></tg-spoiler></blockquote>

messages-check_claim_already_redeemed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Check already redeemed.</blockquote>

messages-check_claim_already_closed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> This check was closed by owner.</blockquote>

messages-check_claim_username_required =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Telegram username is required to redeem this check.</blockquote>

messages-check_claim_recipient_mismatch =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> This check is assigned to another user.</blockquote>

messages-check_claim_password_required =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Password is required for this check.</blockquote>

messages-check_claim_password_invalid =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Invalid password.</blockquote>

messages-check_claim_delivery_unavailable =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Delivery service is temporarily unavailable.</blockquote>

messages-check_claim_delivery_failed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Failed to complete redemption.</blockquote>

messages-check_claim_processing =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Check is already processing.</blockquote>

messages-check_claim_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Check not found.</blockquote>

messages-check_notice_close_button = Close

messages-check_creator_claimed =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Your check was claimed</b></blockquote>

    <table>
    <tr><td>Recipient</td><td><b>{ $claimer }</b></td></tr>
    <tr><th>Amount</th><td><mark>{ $stars } Stars</mark> · { $amount } USD</td></tr>
    </table>

messages-check_claim_password_required_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Check Redemption</b></blockquote>

    <b>Amount:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<code>{ $amount } USD</code>)
    Send password.

messages-check_inline_help_title = Stars Check

messages-check_inline_help_description = Enter amount from 50 to 10000

messages-check_inline_help_message =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Checks · Inline</b></blockquote>
    Query: <code>@ttstars_tgbot 50</code>
    Range: <b>50</b> – <b>10000</b> Stars.

messages-check_inline_create_title = Send { $stars } Stars

messages-check_inline_create_description = Share check for { $amount } USD

messages-check_inline_placeholder =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Check · Processing</b></blockquote>

    <b>Creating check:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> · <code>{ $amount } USD</code>…

messages-check_inline_card_message = <a href="{ $image_url }">&#8205;</a><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Check for <b>{ $stars }</b> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<b>{ $amount } USD</b>) for <code>{ $target }</code>.

messages-check_inline_card_message_any = <a href="{ $image_url }">&#8205;</a><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Check for <b>{ $stars }</b> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<b>{ $amount } USD</b>).

messages-check_inline_received_button = ✅ Claimed

messages-check_inline_share_title = Share check for { $stars } Stars

messages-check_inline_share_description = Amount: { $amount } USD

messages-check_inline_not_found_title = Check unavailable

messages-check_inline_not_found_description = Check not found or already inactive

messages-check_inline_not_enough_title = Not enough balance

messages-check_inline_not_enough_description = Have { $current } USD, need { $required } USD

messages-check_inline_not_enough_message =
    <blockquote><b><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Not enough balance</b></blockquote>

    <b>Current balance:</b> <code>{ $current } USD</code>
    <b>Required for check:</b> <code>{ $required } USD</code>

messages-check_inline_draft_missing = Check draft unavailable. Create a new check via inline.

messages-check_inline_unavailable =
    <blockquote><b><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Check unavailable</b></blockquote>

    Sender has insufficient balance for this check.

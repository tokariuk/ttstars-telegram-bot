messages-referral_screen =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Referral System</b></blockquote>

    Track referrals and referral earnings.

    <tg-emoji emoji-id="5382283505872967732">🔗</tg-emoji> <b>Link:</b> <code>{ $link }</code>

    <b>Referral balance:</b> <code>{ $balance } USD</code>
    <b>Total earned:</b> <code>{ $earned } USD</code>

    <tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> <b>Total referrals:</b> <b>{ $total }</b>
    ├ Level 1 ({ $percent1 }%): <b>{ $level1 }</b>
    ├ Level 2 ({ $percent2 }%): <b>{ $level2 }</b>
    └ Level 3 ({ $percent3 }%): <b>{ $level3 }</b>

messages-referral_list_screen =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Referrals List ({ $total })</b></blockquote>

    Choose a referral.

messages-referral_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Referrals List</b></blockquote>

    No referrals yet.

messages-referral_member_button = L{ $level } · #{ $user_id } · { $name }

messages-referral_list_page_indicator = { $current }/{ $total }

messages-referral_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Referral #{ $user_id }</b></blockquote>

    <b>Name:</b> <b>{ $name }</b>
    <b>Level:</b> <code>{ $level }</code> ({ $percent }%)
    <b>Joined:</b> { $joined }

messages-referral_detail_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Referral not found or unavailable.</blockquote>

messages-referral_withdraw_screen =
    <blockquote><b><tg-emoji emoji-id="5381926933393085632">👛</tg-emoji> Withdraw Referral Balance</b></blockquote>

    Send the amount in USD you want to withdraw.

    <b>Available:</b> <code>{ $balance } USD</code>

messages-referral_withdraw_invalid_amount =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Amount must be between <b>{ $min_amount }</b> and <b>{ $max_amount } USD</b>.</blockquote>

messages-referral_withdraw_empty =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Referral balance is empty.</blockquote>

messages-referral_withdraw_done =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Credited to main balance: <b>{ $amount } USD</b>.</blockquote>

messages-referral_unavailable =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Referral data is temporarily unavailable.</blockquote>

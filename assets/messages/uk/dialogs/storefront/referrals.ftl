messages-referral_screen =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Реферальна система</b></blockquote>

    Керуй запрошеннями та реферальним балансом.

    <tg-emoji emoji-id="5382283505872967732">🔗</tg-emoji> <b>Посилання:</b> <code>{ $link }</code>

    <b>Реферальний баланс:</b> <code>{ $balance } USD</code>
    <b>Зароблено всього:</b> <code>{ $earned } USD</code>

    <tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> <b>Всього рефералів:</b> <b>{ $total }</b>
    ├ Рівень 1 ({ $percent1 }%): <b>{ $level1 }</b>
    ├ Рівень 2 ({ $percent2 }%): <b>{ $level2 }</b>
    └ Рівень 3 ({ $percent3 }%): <b>{ $level3 }</b>

messages-referral_list_screen =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Список рефералів ({ $total })</b></blockquote>

    Обери реферала.

messages-referral_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Список рефералів</b></blockquote>

    Рефералів ще немає.

messages-referral_member_button = L{ $level } · #{ $user_id } · { $name }

messages-referral_list_page_indicator = { $current }/{ $total }

messages-referral_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Реферал #{ $user_id }</b></blockquote>

    <b>Імʼя:</b> <b>{ $name }</b>
    <b>Рівень:</b> <code>{ $level }</code> ({ $percent }%)
    <b>Дата приєднання:</b> { $joined }

messages-referral_detail_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Реферала не знайдено або він недоступний.</blockquote>

messages-referral_withdraw_screen =
    <blockquote><b><tg-emoji emoji-id="5381926933393085632">👛</tg-emoji> Виведення реферального балансу</b></blockquote>

    Надішли суму в USD, яку потрібно вивести.

    <b>Доступно:</b> <code>{ $balance } USD</code>

messages-referral_withdraw_invalid_amount =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Сума має бути в діапазоні <b>{ $min_amount }</b> – <b>{ $max_amount } USD</b>.</blockquote>

messages-referral_withdraw_empty =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> На реферальному балансі немає коштів.</blockquote>

messages-referral_withdraw_done =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Переведено на основний баланс: <b>{ $amount } USD</b>.</blockquote>

messages-referral_unavailable =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Реферальні дані тимчасово недоступні.</blockquote>

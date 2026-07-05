messages-referral_screen =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Реферальная система</b></blockquote>

    Управляй приглашениями и реферальным балансом.

    <tg-emoji emoji-id="5382283505872967732">🔗</tg-emoji> <b>Ссылка:</b> <code>{ $link }</code>

    <b>Реферальный баланс:</b> <code>{ $balance } USD</code>
    <b>Заработано всего:</b> <code>{ $earned } USD</code>

    <tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> <b>Всего рефералов:</b> <b>{ $total }</b>
    ├ Уровень 1 ({ $percent1 }%): <b>{ $level1 }</b>
    ├ Уровень 2 ({ $percent2 }%): <b>{ $level2 }</b>
    └ Уровень 3 ({ $percent3 }%): <b>{ $level3 }</b>

messages-referral_list_screen =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Список рефералов ({ $total })</b></blockquote>

    Выбери реферала.

messages-referral_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Список рефералов</b></blockquote>

    Рефералов ещё нет.

messages-referral_member_button = L{ $level } · #{ $user_id } · { $name }

messages-referral_list_page_indicator = { $current }/{ $total }

messages-referral_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Реферал #{ $user_id }</b></blockquote>

    <b>Имя:</b> <b>{ $name }</b>
    <b>Уровень:</b> <code>{ $level }</code> ({ $percent }%)
    <b>Дата присоединения:</b> { $joined }

messages-referral_detail_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Реферал не найден или недоступен.</blockquote>

messages-referral_withdraw_screen =
    <blockquote><b><tg-emoji emoji-id="5381926933393085632">👛</tg-emoji> Вывод реферального баланса</b></blockquote>

    Отправь сумму в USD, которую нужно вывести.

    <b>Доступно:</b> <code>{ $balance } USD</code>

messages-referral_withdraw_invalid_amount =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Сумма должна быть в диапазоне <b>{ $min_amount }</b> – <b>{ $max_amount } USD</b>.</blockquote>

messages-referral_withdraw_empty =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> На реферальном балансе нет средств.</blockquote>

messages-referral_withdraw_done =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Переведено на основной баланс: <b>{ $amount } USD</b>.</blockquote>

messages-referral_unavailable =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Реферальные данные временно недоступны.</blockquote>

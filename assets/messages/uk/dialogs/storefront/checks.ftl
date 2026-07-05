messages-check_item_button = #{ $check_id } · { $stars } Stars · { $amount } USD

messages-check_history_item_button = #{ $check_id } · { $status } · { $stars } Stars · { $amount } USD

messages-check_claim_username_any = Будь-хто

messages-check_claim_password_set = Встановлено

messages-check_claim_password_empty = Не встановлено

messages-checks_list_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Чеки ({ $active_count })</b></blockquote>

messages-checks_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Чеки</b></blockquote>

    Активних чеків немає.

messages-checks_page_indicator = { $current }/{ $total }

messages-checks_history_list_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📄</tg-emoji> Історія чеків ({ $total_count })</b></blockquote>

messages-checks_history_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📄</tg-emoji> Історія чеків</b></blockquote>

    Історія чеків порожня.

messages-checks_history_page_indicator = { $current }/{ $total }

messages-checks_create_stars_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Створення чека · Крок 1/4</b></blockquote>

    Надішли кількість Stars.

    <b>Мінімум:</b> <code>{ $min_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    <b>Максимум:</b> <code>{ $max_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

messages-checks_create_recipient_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Створення чека · Крок 2/4</b></blockquote>

    Надішли <code>@username</code>, хто зможе активувати чек, або пропусти крок.

messages-checks_create_password_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Створення чека · Крок 3/4</b></blockquote>

    Надішли пароль або пропусти крок.

messages-checks_create_confirm_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Створення чека · Крок 4/4</b></blockquote>

    <b>Сума:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<code>{ $amount } USD</code>)
    <b>Отримувач:</b> <code>{ $claim_username }</code>
    <b>Пароль:</b> <code>{ $has_password }</code>

messages-check_detail_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Чек не знайдено або він уже неактивний.</blockquote>

messages-check_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Чек #{ $check_id }</b></blockquote>

    <b>Сума:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<code>{ $amount } USD</code>)
    <b>Отримувач:</b> <code>{ $claim_username }</code>
    <b>Пароль:</b> <code>{ $has_password }</code>
    <b>Створено:</b> { $created }

    <b>Посилання:</b> <code>{ $link }</code>

messages-check_history_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📄</tg-emoji> Історія чека #{ $check_id }</b></blockquote>

    <b>Статус:</b> <code>{ $status }</code>
    <b>Сума:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<code>{ $amount } USD</code>)
    <b>Отримувач:</b> <code>{ $claim_username }</code>
    <b>Пароль:</b> <code>{ $has_password }</code>

    <b>Посилання:</b> <code>{ $link }</code>

    <blockquote expandable><b>Технічні деталі</b>
    <b>ID активатора:</b> <code>{ $recipient_id }</code>
    <b>TX:</b> <tg-spoiler><code>{ $tx_hash }</code></tg-spoiler>
    <b>Помилка:</b> <code>{ $last_error }</code>
    <b>Створено:</b> { $created }
    <b>Активовано:</b> { $redeemed }
    <b>Закрито:</b> { $closed }</blockquote>

messages-check_status_active = Активний

messages-check_status_processing = Обробляється

messages-check_status_redeemed = Активований

messages-check_status_closed = Закритий

messages-check_settings_screen =
    <blockquote><b><tg-emoji emoji-id="5381935145370559125">🧾</tg-emoji> Налаштування чека #{ $check_id }</b></blockquote>

    <b>Отримувач:</b> <code>{ $claim_username }</code>
    <b>Пароль:</b> <code>{ $has_password }</code>

messages-check_settings_edit_recipient_screen =
    <blockquote><b><tg-emoji emoji-id="5381935145370559125">🧾</tg-emoji> Редагування отримувача</b></blockquote>

    Надішли username у форматі <code>@username</code>.

messages-check_settings_edit_password_screen =
    <blockquote><b><tg-emoji emoji-id="5381935145370559125">🧾</tg-emoji> Редагування пароля</b></blockquote>

    Надішли новий пароль.

messages-check_create_done =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Чек створено.</blockquote>

messages-check_create_failed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Не вдалося створити чек.</blockquote>

messages-check_create_stars_invalid =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Кількість має бути в діапазоні <b>{ $min_stars }</b> – <b>{ $max_stars }</b>.</blockquote>

messages-check_create_password_invalid =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Пароль не може бути порожнім.</blockquote>

messages-check_settings_recipient_saved =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Отримувача оновлено.</blockquote>

messages-check_settings_recipient_cleared =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Обмеження за отримувачем знято.</blockquote>

messages-check_settings_password_saved =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Пароль оновлено.</blockquote>

messages-check_settings_password_cleared =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Пароль видалено.</blockquote>

messages-check_close_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Чек не знайдено або вже недоступний.</blockquote>

messages-check_close_done =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Чек закрито. Кошти повернено на баланс.</blockquote>

messages-check_close_already_redeemed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Чек вже активовано.</blockquote>

messages-check_close_already_closed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Цей чек уже закрито.</blockquote>

messages-check_close_processing =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Чек уже обробляється.</blockquote>

messages-check_claim_done_stars =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Відправлено: <b>{ $stars }</b> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> · TX: <tg-spoiler><code>{ $tx_hash }</code></tg-spoiler></blockquote>

messages-check_claim_already_redeemed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Чек вже активовано.</blockquote>

messages-check_claim_already_closed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Цей чек закрито власником.</blockquote>

messages-check_claim_username_required =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Для активації потрібен username у профілі Telegram.</blockquote>

messages-check_claim_recipient_mismatch =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Цей чек призначений для іншого користувача.</blockquote>

messages-check_claim_password_required =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Для активації потрібен пароль.</blockquote>

messages-check_claim_password_invalid =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Невірний пароль.</blockquote>

messages-check_claim_delivery_unavailable =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Сервіс доставки тимчасово недоступний.</blockquote>

messages-check_claim_delivery_failed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Не вдалося завершити активацію.</blockquote>

messages-check_claim_processing =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Чек уже обробляється.</blockquote>

messages-check_claim_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Чек не знайдено.</blockquote>

messages-check_notice_close_button = Закрити

messages-check_creator_claimed =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Твій чек активовано</b></blockquote>

    <table>
    <tr><td>Отримувач</td><td><b>{ $claimer }</b></td></tr>
    <tr><th>Сума</th><td><mark>{ $stars } Stars</mark> · { $amount } USD</td></tr>
    </table>

messages-check_claim_password_required_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Активація чека</b></blockquote>

    <b>Сума:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<code>{ $amount } USD</code>)

    Надішли пароль.

messages-check_inline_help_title = Чек на Stars

messages-check_inline_help_description = Введи кількість від 50 до 10000

messages-check_inline_help_message =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Чеки · Inline</b></blockquote>
    Запит: <code>@ttstars_tgbot 50</code>
    Діапазон: <b>50</b> – <b>10000</b> Stars.

messages-check_inline_create_title = Відправити { $stars } Stars

messages-check_inline_create_description = Поділитися чеком на { $amount } USD

messages-check_inline_placeholder =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Чек · Обробка</b></blockquote>

    <b>Створюю чек:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> · <code>{ $amount } USD</code>…

messages-check_inline_card_message = <a href="{ $image_url }">&#8205;</a><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Чек на <b>{ $stars }</b> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<b>{ $amount } USD</b>) для <code>{ $target }</code>.

messages-check_inline_card_message_any = <a href="{ $image_url }">&#8205;</a><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Чек на <b>{ $stars }</b> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<b>{ $amount } USD</b>).

messages-check_inline_received_button = ✅ Отримано

messages-check_inline_share_title = Поділитися чеком на { $stars } Stars

messages-check_inline_share_description = Сума: { $amount } USD

messages-check_inline_not_found_title = Чек недоступний

messages-check_inline_not_found_description = Чек не знайдено або він уже неактивний

messages-check_inline_not_enough_title = Недостатньо коштів

messages-check_inline_not_enough_description = Є { $current } USD, потрібно { $required } USD

messages-check_inline_not_enough_message =
    <blockquote><b><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Недостатньо коштів</b></blockquote>

    <b>Поточний баланс:</b> <code>{ $current } USD</code>
    <b>Потрібно для чека:</b> <code>{ $required } USD</code>

messages-check_inline_draft_missing = Чернетка чека недоступна. Створи новий чек через inline.

messages-check_inline_unavailable =
    <blockquote><b><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Чек недоступний</b></blockquote>

    У відправника недостатньо балансу для цього чека.

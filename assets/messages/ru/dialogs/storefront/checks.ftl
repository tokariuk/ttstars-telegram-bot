messages-check_item_button = #{ $check_id } · { $stars } Stars · { $amount } USD

messages-check_history_item_button = #{ $check_id } · { $status } · { $stars } Stars · { $amount } USD

messages-check_claim_username_any = Любой

messages-check_claim_password_set = Установлен

messages-check_claim_password_empty = Не установлен

messages-checks_list_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Чеки ({ $active_count })</b></blockquote>

messages-checks_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Чеки</b></blockquote>

    Активных чеков нет.

messages-checks_page_indicator = { $current }/{ $total }

messages-checks_history_list_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📄</tg-emoji> История чеков ({ $total_count })</b></blockquote>

messages-checks_history_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📄</tg-emoji> История чеков</b></blockquote>

    История чеков пуста.

messages-checks_history_page_indicator = { $current }/{ $total }

messages-checks_create_stars_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Создание чека · Шаг 1/4</b></blockquote>

    Отправь количество Stars.

    <b>Минимум:</b> <code>{ $min_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    <b>Максимум:</b> <code>{ $max_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

messages-checks_create_recipient_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Создание чека · Шаг 2/4</b></blockquote>

    Отправь <code>@username</code>, кто сможет активировать чек, или пропусти шаг.

messages-checks_create_password_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Создание чека · Шаг 3/4</b></blockquote>

    Отправь пароль или пропусти шаг.

messages-checks_create_confirm_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Создание чека · Шаг 4/4</b></blockquote>

    <b>Сумма:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<code>{ $amount } USD</code>)
    <b>Получатель:</b> <code>{ $claim_username }</code>
    <b>Пароль:</b> <code>{ $has_password }</code>

messages-check_detail_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Чек не найден или уже неактивен.</blockquote>

messages-check_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Чек #{ $check_id }</b></blockquote>

    <b>Сумма:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<code>{ $amount } USD</code>)
    <b>Получатель:</b> <code>{ $claim_username }</code>
    <b>Пароль:</b> <code>{ $has_password }</code>
    <b>Создан:</b> { $created }

    <b>Ссылка:</b> <code>{ $link }</code>

messages-check_history_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📄</tg-emoji> История чека #{ $check_id }</b></blockquote>

    <b>Статус:</b> <code>{ $status }</code>
    <b>Сумма:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<code>{ $amount } USD</code>)
    <b>Получатель:</b> <code>{ $claim_username }</code>
    <b>Пароль:</b> <code>{ $has_password }</code>

    <b>Ссылка:</b> <code>{ $link }</code>

    <blockquote expandable><b>Технические детали</b>
    <b>ID активатора:</b> <code>{ $recipient_id }</code>
    <b>TX:</b> <tg-spoiler><code>{ $tx_hash }</code></tg-spoiler>
    <b>Ошибка:</b> <code>{ $last_error }</code>
    <b>Создан:</b> { $created }
    <b>Активирован:</b> { $redeemed }
    <b>Закрыт:</b> { $closed }</blockquote>

messages-check_status_active = Активен

messages-check_status_processing = Обрабатывается

messages-check_status_redeemed = Активирован

messages-check_status_closed = Закрыт

messages-check_settings_screen =
    <blockquote><b><tg-emoji emoji-id="5381935145370559125">🧾</tg-emoji> Настройки чека #{ $check_id }</b></blockquote>

    <b>Получатель:</b> <code>{ $claim_username }</code>
    <b>Пароль:</b> <code>{ $has_password }</code>

messages-check_settings_edit_recipient_screen =
    <blockquote><b><tg-emoji emoji-id="5381935145370559125">🧾</tg-emoji> Редактирование получателя</b></blockquote>

    Отправь username в формате <code>@username</code>.

messages-check_settings_edit_password_screen =
    <blockquote><b><tg-emoji emoji-id="5381935145370559125">🧾</tg-emoji> Редактирование пароля</b></blockquote>

    Отправь новый пароль.

messages-check_create_done =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Чек создан.</blockquote>

messages-check_create_failed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Не удалось создать чек.</blockquote>

messages-check_create_stars_invalid =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Количество должно быть в диапазоне <b>{ $min_stars }</b> – <b>{ $max_stars }</b>.</blockquote>

messages-check_create_password_invalid =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Пароль не может быть пустым.</blockquote>

messages-check_settings_recipient_saved =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Получатель обновлён.</blockquote>

messages-check_settings_recipient_cleared =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Ограничение по получателю снято.</blockquote>

messages-check_settings_password_saved =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Пароль обновлён.</blockquote>

messages-check_settings_password_cleared =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Пароль удалён.</blockquote>

messages-check_close_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Чек не найден или уже недоступен.</blockquote>

messages-check_close_done =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Чек закрыт. Средства возвращены на баланс.</blockquote>

messages-check_close_already_redeemed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Чек уже активирован.</blockquote>

messages-check_close_already_closed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Этот чек уже закрыт.</blockquote>

messages-check_close_processing =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Чек уже обрабатывается.</blockquote>

messages-check_claim_done_stars =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Отправлено: <b>{ $stars }</b> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> · TX: <tg-spoiler><code>{ $tx_hash }</code></tg-spoiler></blockquote>

messages-check_claim_already_redeemed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Чек уже активирован.</blockquote>

messages-check_claim_already_closed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Этот чек закрыт владельцем.</blockquote>

messages-check_claim_username_required =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Для активации нужен username в профиле Telegram.</blockquote>

messages-check_claim_recipient_mismatch =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Этот чек предназначен для другого пользователя.</blockquote>

messages-check_claim_password_required =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Для активации нужен пароль.</blockquote>

messages-check_claim_password_invalid =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Неверный пароль.</blockquote>

messages-check_claim_delivery_unavailable =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Сервис доставки временно недоступен.</blockquote>

messages-check_claim_delivery_failed =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Не удалось завершить активацию.</blockquote>

messages-check_claim_processing =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Чек уже обрабатывается.</blockquote>

messages-check_claim_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Чек не найден.</blockquote>

messages-check_notice_close_button = Закрыть

messages-check_creator_claimed =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Твой чек активирован</b></blockquote>

    <table>
    <tr><td>Получатель</td><td><b>{ $claimer }</b></td></tr>
    <tr><th>Сумма</th><td><mark>{ $stars } Stars</mark> · { $amount } USD</td></tr>
    </table>

messages-check_claim_password_required_screen =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Активация чека</b></blockquote>

    <b>Сумма:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<code>{ $amount } USD</code>)

    Отправь пароль.

messages-check_inline_help_title = Чек на Stars

messages-check_inline_help_description = Введи количество от 50 до 10000

messages-check_inline_help_message =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Чеки · Inline</b></blockquote>
    Запрос: <code>@ttstars_tgbot 50</code>
    Диапазон: <b>50</b> – <b>10000</b> Stars.

messages-check_inline_create_title = Отправить { $stars } Stars

messages-check_inline_create_description = Поделиться чеком на { $amount } USD

messages-check_inline_placeholder =
    <blockquote><b><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Чек · Обработка</b></blockquote>

    <b>Создаю чек:</b> <code>{ $stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> · <code>{ $amount } USD</code>…

messages-check_inline_card_message = <a href="{ $image_url }">&#8205;</a><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Чек на <b>{ $stars }</b> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<b>{ $amount } USD</b>) для <code>{ $target }</code>.

messages-check_inline_card_message_any = <a href="{ $image_url }">&#8205;</a><tg-emoji emoji-id="5382212574488075316">🧾</tg-emoji> Чек на <b>{ $stars }</b> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> (<b>{ $amount } USD</b>).

messages-check_inline_received_button = ✅ Получено

messages-check_inline_share_title = Поделиться чеком на { $stars } Stars

messages-check_inline_share_description = Сумма: { $amount } USD

messages-check_inline_not_found_title = Чек недоступен

messages-check_inline_not_found_description = Чек не найден или уже неактивен

messages-check_inline_not_enough_title = Недостаточно средств

messages-check_inline_not_enough_description = Есть { $current } USD, нужно { $required } USD

messages-check_inline_not_enough_message =
    <blockquote><b><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Недостаточно средств</b></blockquote>

    <b>Текущий баланс:</b> <code>{ $current } USD</code>
    <b>Нужно для чека:</b> <code>{ $required } USD</code>

messages-check_inline_draft_missing = Черновик чека недоступен. Создай новый чек через inline.

messages-check_inline_unavailable =
    <blockquote><b><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Чек недоступен</b></blockquote>

    У отправителя недостаточно баланса для этого чека.

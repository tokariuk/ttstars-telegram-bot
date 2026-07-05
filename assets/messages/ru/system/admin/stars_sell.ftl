messages-admin_stars_sell_days =
    { $count ->
        [one] { $count } день
        [few] { $count } дня
        [many] { $count } дней
       *[other] { $count } дня
    }

messages-admin_stars_sell_menu_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продажа звёзд</b></blockquote>

    Создавайте заявки на продажу и просматривайте их историю.

    <b>Сводка:</b>
    • Всего заявок: <code>{ $total_orders }</code>
    • Оплачено звёзд: <code>{ $total_paid_stars }</code>
    • Готово к выплате: <code>{ $ready_for_payout }</code>
    • Выплачено: <code>{ $completed_payout } USD</code>

messages-admin_stars_sell_stars_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продажа звёзд · Шаг 1/3</b></blockquote>

    Введите количество звёзд для продажи.

    • Минимум: <code>{ $min_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Максимум: <code>{ $max_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Текущий выбор: <code>{ $selected_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

    • Курс: <code>{ $rate_usd } USD</code> за 1 <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Холд выплаты: <code>{ $hold_days_text }</code>

messages-admin_stars_sell_wallet_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продажа звёзд · Шаг 2/3</b></blockquote>

    Введите TON-кошелёк (USDT) для выплаты.

    • Количество: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • К выплате: <code>{ $payout_amount } USD</code>
    • Текущий кошелёк: <code>{ $wallet }</code>

messages-admin_stars_sell_payment_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продажа звёзд · Шаг 3/3</b></blockquote>

    Проверьте параметры и отправьте инвойс на оплату звёздами.

    • Количество: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • К выплате: <code>{ $payout_amount } USD</code>
    • Кошелёк: <code>{ $wallet }</code>
    • Холд: <code>{ $hold_days_text }</code>
    • К оплате в Telegram: <code>{ $invoice_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

messages-admin_stars_sell_history_list_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продажа звёзд · История заявок</b></blockquote>

    Выберите заявку, чтобы открыть детали.
    • Страница: <code>{ $page }</code>

messages-admin_stars_sell_history_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продажа звёзд · История заявок</b></blockquote>

    У вас пока нет заявок на продажу.

messages-admin_stars_sell_history_detail_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Заявка не найдена.</blockquote>

messages-admin_stars_sell_history_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продажа звёзд · Заявка #{ $order_id }</b></blockquote>

    • Статус: <code>{ $status }</code>
    • Количество: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • К выплате: <code>{ $payout_amount } USD</code>
    • Кошелёк: <code>{ $wallet }</code>
    • Сумма инвойса: <code>{ $invoice_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

    <b>Таймлайн:</b>
    • Создано: { $created_at }
    • Оплачено: { $paid_at }
    • Доступно к выплате: { $payout_available_at }
    • Завершено: { $completed_at }
    • Отклонено: { $rejected_at }
    • Рефанд: { $refunded_at }

    <b>Технические данные:</b>
    • User ID: <code>{ $user_id }</code>
    • Invoice payload: <code>{ $invoice_payload }</code>
    • Оплачено в Stars: <code>{ $paid_stars }</code>
    • Причина ошибки: <code>{ $failure_reason }</code>
    • Причина резолюции: <code>{ $resolution_reason }</code>
    • Комментарий резолюции: <code>{ $resolution_note }</code>

messages-admin_stars_sell_admin_list_screen =
    <b>Продажа звёзд · Управление заявками</b>

    Выберите заявку для управления.
    • Страница: <code>{ $page }</code>

messages-admin_stars_sell_admin_list_empty_screen =
    <b>Продажа звёзд · Управление заявками</b>

    Заявок для управления пока нет.

messages-admin_stars_sell_admin_detail_not_found =
    ⚠️ Заявка не найдена.

messages-admin_stars_sell_admin_detail_screen =
    <b>Управление заявкой #{ $order_id }</b>

    • User ID: <code>{ $user_id }</code>
    • Статус: <code>{ $status }</code>
    • Количество: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • К выплате: <code>{ $payout_amount } USD</code>
    • Кошелёк: <code>{ $wallet }</code>
    • Сумма инвойса: <code>{ $invoice_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

    <b>Таймлайн:</b>
    • Создано: { $created_at }
    • Оплачено: { $paid_at }
    • Доступно к выплате: { $payout_available_at }
    • Завершено: { $completed_at }
    • Отклонено: { $rejected_at }
    • Рефанд: { $refunded_at }

    <b>Технические данные:</b>
    • Invoice payload: <code>{ $invoice_payload }</code>
    • Оплачено в Stars: <code>{ $paid_stars }</code>
    • Причина ошибки: <code>{ $failure_reason }</code>
    • Причина резолюции: <code>{ $resolution_reason }</code>
    • Комментарий резолюции: <code>{ $resolution_note }</code>

messages-admin_stars_sell_status_pending_payment = ожидает оплату
messages-admin_stars_sell_status_paid_hold = оплачено (холд)
messages-admin_stars_sell_status_paid_hold_ready = оплачено (готово к выводу)
messages-admin_stars_sell_status_completed = завершено
messages-admin_stars_sell_status_canceled = отменено
messages-admin_stars_sell_status_rejected = отклонено
messages-admin_stars_sell_status_refunded = отклонено
messages-admin_stars_sell_status_failed = ошибка

messages-admin_stars_sell_reason_replaced_by_new_request = заменено новой заявкой
messages-admin_stars_sell_reason_user_request = запрос пользователя
messages-admin_stars_sell_reason_invalid_payout_wallet = некорректный кошелёк выплаты
messages-admin_stars_sell_reason_stars_refunded = Stars возвращены
messages-admin_stars_sell_reason_stars_not_withdrawable = Stars недоступны для вывода
messages-admin_stars_sell_reason_fraud_suspected = подозрение на фрод
messages-admin_stars_sell_reason_kyc_or_fragment_restriction = KYC/ограничение Fragment
messages-admin_stars_sell_reason_payout_technical_failure = техническая ошибка выплаты
messages-admin_stars_sell_reason_policy_restriction = ограничение политики
messages-admin_stars_sell_reason_other = другая причина

messages-admin_stars_sell_history_page_indicator = { $current }/{ $total }
messages-admin_stars_sell_history_item_button = #{ $order_id } · { $status } · { $stars_count } звёзд · { $payout_amount } USD

messages-admin_stars_sell_admin_page_indicator = { $current }/{ $total }
messages-admin_stars_sell_admin_item_button = #{ $order_id } · #{ $user_id } · { $status } · { $stars_count } звёзд · { $payout_amount } USD

messages-admin_stars_sell_stars_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Введите целое положительное число (количество звёзд).</blockquote>
messages-admin_stars_sell_stars_out_of_range = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Количество звёзд должно быть в диапазоне <code>{ $min_stars }</code>–<code>{ $max_stars }</code>.</blockquote>
messages-admin_stars_sell_wallet_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некорректный TON-кошелёк. Используйте формат <code>UQ...</code> или <code>EQ...</code>.</blockquote>
messages-admin_stars_sell_stars_missing = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Сначала укажите количество звёзд.</blockquote>
messages-admin_stars_sell_wallet_missing = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Сначала укажите кошелёк для выплаты.</blockquote>
messages-admin_stars_sell_order_create_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не удалось создать заявку на продажу. Попробуйте позже.</blockquote>
messages-admin_stars_sell_invoice_send_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не удалось отправить инвойс. Попробуйте ещё раз.</blockquote>
messages-admin_stars_sell_invoice_sent = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Инвойс на оплату звёздами отправлен. Заявка: <code>{ $order_id }</code>.</blockquote>
messages-admin_stars_sell_invoice_resent = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Для открытой заявки <code>{ $order_id }</code> отправлен новый инвойс.</blockquote>
messages-admin_stars_sell_invoice_replaced = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Предыдущая неоплаченная заявка отменена. Создана новая: <code>{ $order_id }</code>.</blockquote>
messages-admin_stars_sell_invoice_canceled = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Заявка отменена.</blockquote>
messages-admin_stars_sell_invoice_cancel_unavailable = <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Эту заявку уже нельзя отменить.</blockquote>
messages-admin_stars_sell_invoice_cancel_not_found = <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Заявка не найдена.</blockquote>

messages-admin_stars_sell_admin_action_completed = ✅ Заявка <code>{ $order_id }</code> отмечена как завершённая.
messages-admin_stars_sell_admin_action_rejected = ✅ Заявка <code>{ $order_id }</code> отклонена.
messages-admin_stars_sell_admin_action_not_ready = ⚠️ Заявка <code>{ $order_id }</code> ещё на холде. Доступно после: <code>{ $payout_available_at }</code>.
messages-admin_stars_sell_admin_action_conflict = ⚠️ Статус заявки <code>{ $order_id }</code> уже изменён. Обновите данные.
messages-admin_stars_sell_admin_action_failed = ❌ Не удалось выполнить действие для заявки <code>{ $order_id }</code>.

messages-admin_stars_sell_invoice_title = Продажа Telegram Stars
messages-admin_stars_sell_invoice_description = Продажа { $stars_count } ⭐. После подтверждения оплаты выплата { $payout_amount } USD будет доступна через { $hold_days_text }.
messages-admin_stars_sell_invoice_label = Продажа { $stars_count } ⭐

messages-admin_stars_sell_payment_confirmed =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Оплата звёздами подтверждена</b></blockquote>

    • Заявка: <code>{ $order_id }</code>
    • Оплачено: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • К выплате: <code>{ $payout_amount } USD</code>
    • Кошелёк: <code>{ $wallet }</code>
    • Доступно для ручной выплаты после: <code>{ $payout_available_at }</code>
    • Холд: <code>{ $hold_days_text }</code>

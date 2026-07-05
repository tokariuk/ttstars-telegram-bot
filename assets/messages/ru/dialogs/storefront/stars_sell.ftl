messages-stars_sell_days =
    { $count ->
        [one] { $count } день
        [few] { $count } дня
        [many] { $count } дней
       *[other] { $count } дня
    }

messages-stars_sell_menu_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продажа звёзд</b></blockquote>

    Создавайте заявки на продажу и просматривайте их историю.

    <b>Цена за 1 <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji></b>: <code>{ $rate_usd } USD</code>

messages-stars_sell_stars_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продажа звёзд · Шаг 1/3</b></blockquote>

    Введите количество звёзд для продажи.

    • Минимум: <code>{ $min_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Максимум: <code>{ $max_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Холд выплаты: <code>{ $hold_days_text }</code>

messages-stars_sell_wallet_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продажа звёзд · Шаг 2/3</b></blockquote>

    Введите TON-кошелёк (USDT) для выплаты.

messages-stars_sell_payment_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продажа звёзд · Шаг 3/3</b></blockquote>

    Проверьте параметры и отправьте инвойс на оплату звёздами.

    • Количество: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • К выплате: <code>{ $payout_amount } USD</code>
    • Кошелёк: <code>{ $wallet }</code>
    • Холд: <code>{ $hold_days_text }</code>

messages-stars_sell_history_list_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> История заявок</b></blockquote>

    Выберите заявку, чтобы открыть детали.

messages-stars_sell_history_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> История заявок</b></blockquote>

    У вас пока нет заявок на продажу.

messages-stars_sell_history_detail_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Заявка не найдена.</blockquote>

messages-stars_sell_history_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> Заявка #{ $order_id }</b></blockquote>

    • Статус: <code>{ $status }</code>
    • Количество: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • К выплате: <code>{ $payout_amount } USD</code>
    • Кошелёк: <code>{ $wallet }</code>
    • Сумма инвойса: <code>{ $invoice_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

    <blockquote expandable><b>Таймлайн</b>
    • Создано: { $created_at }
    • Оплачено: { $paid_at }
    • Доступно к выплате: { $payout_available_at }
    • Завершено: { $completed_at }
    • Отклонено: { $rejected_at }
    • Рефанд: { $refunded_at }

    <b>Технические данные</b>
    • Invoice payload: <code>{ $invoice_payload }</code>
    • Оплачено в Stars: <code>{ $paid_stars }</code>
    • Причина ошибки: <code>{ $failure_reason }</code>
    • Причина резолюции: <code>{ $resolution_reason }</code>
    • Комментарий резолюции: <code>{ $resolution_note }</code></blockquote>

messages-stars_sell_status_pending_payment = ожидает оплату
messages-stars_sell_status_paid_hold = оплачено (холд)
messages-stars_sell_status_paid_hold_ready = оплачено (готово к выводу)
messages-stars_sell_status_completed = завершено
messages-stars_sell_status_canceled = отменено
messages-stars_sell_status_rejected = отклонено
messages-stars_sell_status_failed = ошибка

messages-stars_sell_history_page_indicator = { $current }/{ $total }
messages-stars_sell_history_item_button = #{ $order_id } · { $status } · { $stars_count } Stars · { $payout_amount } USD

messages-stars_sell_stars_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Введите целое положительное число (количество звёзд).</blockquote>
messages-stars_sell_stars_out_of_range = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Количество звёзд должно быть в диапазоне <code>{ $min_stars }</code>–<code>{ $max_stars }</code>.</blockquote>
messages-stars_sell_wallet_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некорректный TON-кошелёк. Используйте формат <code>UQ...</code> или <code>EQ...</code>.</blockquote>
messages-stars_sell_stars_missing = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Сначала укажите количество звёзд.</blockquote>
messages-stars_sell_wallet_missing = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Сначала укажите кошелёк для выплаты.</blockquote>
messages-stars_sell_order_create_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не удалось создать заявку на продажу. Попробуйте позже.</blockquote>
messages-stars_sell_invoice_send_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не удалось отправить инвойс. Попробуйте ещё раз.</blockquote>
messages-stars_sell_invoice_sent = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Инвойс на оплату звёздами отправлен. Заявка: <code>{ $order_id }</code>.</blockquote>
messages-stars_sell_invoice_resent = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Для открытой заявки <code>{ $order_id }</code> отправлен новый инвойс.</blockquote>
messages-stars_sell_invoice_replaced = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Предыдущая неоплаченная заявка отменена. Создана новая: <code>{ $order_id }</code>.</blockquote>
messages-stars_sell_invoice_canceled = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Заявка отменена.</blockquote>
messages-stars_sell_invoice_cancel_unavailable = <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Эту заявку уже нельзя отменить.</blockquote>
messages-stars_sell_invoice_cancel_not_found = <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Заявка не найдена.</blockquote>

messages-stars_sell_invoice_title = Продажа Telegram Stars
messages-stars_sell_invoice_description = Продажа { $stars_count } Stars. После подтверждения оплаты выплата { $payout_amount } USD будет доступна через { $hold_days_text }.
messages-stars_sell_invoice_label = Продажа { $stars_count } Stars

messages-stars_sell_payment_confirmed =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Оплата звёздами подтверждена</b></blockquote>

    <table>
    <tr><td>Заявка</td><td><code>{ $order_id }</code></td></tr>
    <tr><td>Оплачено</td><td><code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji></td></tr>
    <tr><th>К выплате</th><td><mark>{ $payout_amount } USD</mark></td></tr>
    <tr><td>Кошелёк</td><td><code>{ $wallet }</code></td></tr>
    <tr><td>Доступно после</td><td><code>{ $payout_available_at }</code></td></tr>
    <tr><td>Холд</td><td><code>{ $hold_days_text }</code></td></tr>
    </table>

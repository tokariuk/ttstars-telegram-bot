messages-stars_sell_days =
    { $count ->
        [one] { $count } день
        [few] { $count } дні
        [many] { $count } днів
       *[other] { $count } днів
    }

messages-stars_sell_menu_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продаж Stars</b></blockquote>

    Створюй заявки на продаж і переглядай їхню історію.

    <b>Ціна за 1 <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji></b>: <code>{ $rate_usd } USD</code>

messages-stars_sell_stars_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продаж Stars · Крок 1/3</b></blockquote>

    Введи кількість зірок для продажу.

    • Мінімум: <code>{ $min_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Максимум: <code>{ $max_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Холд виплати: <code>{ $hold_days_text }</code>

messages-stars_sell_wallet_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продаж Stars · Крок 2/3</b></blockquote>

    Введи гаманець TON (USDT), куди отримаєш виплату.

messages-stars_sell_payment_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продаж Stars · Крок 3/3</b></blockquote>

    Перевір параметри та надішли інвойс на оплату зірками.

    • Кількість: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • До виплати: <code>{ $payout_amount } USD</code>
    • Гаманець: <code>{ $wallet }</code>
    • Холд: <code>{ $hold_days_text }</code>

messages-stars_sell_history_list_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> Історія заявок</b></blockquote>

    Обери заявку, щоб переглянути деталі.

messages-stars_sell_history_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> Історія заявок</b></blockquote>

    У тебе ще немає заявок на продаж.

messages-stars_sell_history_detail_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Заявку не знайдено.</blockquote>

messages-stars_sell_history_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> Заявка #{ $order_id }</b></blockquote>

    • Статус: <code>{ $status }</code>
    • Кількість: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • До виплати: <code>{ $payout_amount } USD</code>
    • Гаманець: <code>{ $wallet }</code>
    • Сума інвойсу: <code>{ $invoice_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

    <blockquote expandable><b>Таймлайн</b>
    • Створено: { $created_at }
    • Оплачено: { $paid_at }
    • Доступно до виплати: { $payout_available_at }
    • Завершено: { $completed_at }
    • Відхилено: { $rejected_at }
    • Рефанд: { $refunded_at }

    <b>Технічні дані</b>
    • Invoice payload: <code>{ $invoice_payload }</code>
    • Сплачено в Stars: <code>{ $paid_stars }</code>
    • Причина помилки: <code>{ $failure_reason }</code>
    • Причина резолюції: <code>{ $resolution_reason }</code>
    • Коментар резолюції: <code>{ $resolution_note }</code></blockquote>

messages-stars_sell_status_pending_payment = очікує оплату
messages-stars_sell_status_paid_hold = оплачено (холд)
messages-stars_sell_status_paid_hold_ready = оплачено (готово до виводу)
messages-stars_sell_status_completed = завершено
messages-stars_sell_status_canceled = скасовано
messages-stars_sell_status_rejected = відхилено
messages-stars_sell_status_failed = помилка

messages-stars_sell_history_page_indicator = { $current }/{ $total }
messages-stars_sell_history_item_button = #{ $order_id } · { $status } · { $stars_count } Stars · { $payout_amount } USD

messages-stars_sell_stars_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Введи ціле додатне число (кількість зірок).</blockquote>
messages-stars_sell_stars_out_of_range = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Кількість зірок має бути в межах <code>{ $min_stars }</code>–<code>{ $max_stars }</code>.</blockquote>
messages-stars_sell_wallet_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некоректний TON-гаманець. Використай формат <code>UQ...</code> або <code>EQ...</code>.</blockquote>
messages-stars_sell_stars_missing = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Спочатку вкажи кількість зірок.</blockquote>
messages-stars_sell_wallet_missing = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Спочатку вкажи гаманець для виплати.</blockquote>
messages-stars_sell_order_create_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не вдалося створити заявку на продаж. Спробуй пізніше.</blockquote>
messages-stars_sell_invoice_send_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не вдалося надіслати інвойс. Спробуй ще раз.</blockquote>
messages-stars_sell_invoice_sent = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Інвойс на оплату зірками надіслано. Заявка: <code>{ $order_id }</code>.</blockquote>
messages-stars_sell_invoice_resent = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Для відкритої заявки <code>{ $order_id }</code> надіслано новий інвойс.</blockquote>
messages-stars_sell_invoice_replaced = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Попередню неоплачену заявку скасовано. Створено нову: <code>{ $order_id }</code>.</blockquote>
messages-stars_sell_invoice_canceled = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Заявку скасовано.</blockquote>
messages-stars_sell_invoice_cancel_unavailable = <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Цю заявку вже не можна скасувати.</blockquote>
messages-stars_sell_invoice_cancel_not_found = <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Заявку не знайдено.</blockquote>

messages-stars_sell_invoice_title = Продаж Telegram Stars
messages-stars_sell_invoice_description = Продаж { $stars_count } Stars. Після підтвердження оплати виплата { $payout_amount } USD стане доступною через { $hold_days_text }.
messages-stars_sell_invoice_label = Продаж { $stars_count } Stars

messages-stars_sell_payment_confirmed =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Оплату зірками підтверджено</b></blockquote>

    <table>
    <tr><td>Заявка</td><td><code>{ $order_id }</code></td></tr>
    <tr><td>Сплачено</td><td><code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji></td></tr>
    <tr><th>До виплати</th><td><mark>{ $payout_amount } USD</mark></td></tr>
    <tr><td>Гаманець</td><td><code>{ $wallet }</code></td></tr>
    <tr><td>Доступно після</td><td><code>{ $payout_available_at }</code></td></tr>
    <tr><td>Холд</td><td><code>{ $hold_days_text }</code></td></tr>
    </table>

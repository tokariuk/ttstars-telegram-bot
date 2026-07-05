messages-admin_stars_sell_days =
    { $count ->
        [one] { $count } день
        [few] { $count } дні
        [many] { $count } днів
       *[other] { $count } днів
    }

messages-admin_stars_sell_menu_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продаж зірок</b></blockquote>

    Створюй заявки на продаж і переглядай їхню історію.

    <b>Зведення:</b>
    • Усього заявок: <code>{ $total_orders }</code>
    • Оплачено зірок: <code>{ $total_paid_stars }</code>
    • Готово до виплати: <code>{ $ready_for_payout }</code>
    • Виплачено: <code>{ $completed_payout } USD</code>

messages-admin_stars_sell_stars_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продаж зірок · Крок 1/3</b></blockquote>

    Введи кількість зірок для продажу.

    • Мінімум: <code>{ $min_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Максимум: <code>{ $max_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Поточний вибір: <code>{ $selected_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

    • Курс: <code>{ $rate_usd } USD</code> за 1 <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • Холд виплати: <code>{ $hold_days_text }</code>

messages-admin_stars_sell_wallet_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продаж зірок · Крок 2/3</b></blockquote>

    Введи гаманець TON (USDT), куди отримаєш виплату.

    • Кількість: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • До виплати: <code>{ $payout_amount } USD</code>
    • Поточний гаманець: <code>{ $wallet }</code>

messages-admin_stars_sell_payment_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продаж зірок · Крок 3/3</b></blockquote>

    Перевір параметри та надішли інвойс на оплату зірками.

    • Кількість: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • До виплати: <code>{ $payout_amount } USD</code>
    • Гаманець: <code>{ $wallet }</code>
    • Холд: <code>{ $hold_days_text }</code>
    • До оплати в Telegram: <code>{ $invoice_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

messages-admin_stars_sell_history_list_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продаж зірок · Історія заявок</b></blockquote>

    Обери заявку, щоб переглянути деталі.
    • Сторінка: <code>{ $page }</code>

messages-admin_stars_sell_history_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продаж зірок · Історія заявок</b></blockquote>

    У тебе ще немає заявок на продаж.

messages-admin_stars_sell_history_detail_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Заявку не знайдено.</blockquote>

messages-admin_stars_sell_history_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> Продаж зірок · Заявка #{ $order_id }</b></blockquote>

    • Статус: <code>{ $status }</code>
    • Кількість: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • До виплати: <code>{ $payout_amount } USD</code>
    • Гаманець: <code>{ $wallet }</code>
    • Сума інвойсу: <code>{ $invoice_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

    <b>Таймлайн:</b>
    • Створено: { $created_at }
    • Оплачено: { $paid_at }
    • Доступно до виплати: { $payout_available_at }
    • Завершено: { $completed_at }
    • Відхилено: { $rejected_at }
    • Рефанд: { $refunded_at }

    <b>Технічні дані:</b>
    • User ID: <code>{ $user_id }</code>
    • Invoice payload: <code>{ $invoice_payload }</code>
    • Сплачено в Stars: <code>{ $paid_stars }</code>
    • Причина помилки: <code>{ $failure_reason }</code>
    • Причина резолюції: <code>{ $resolution_reason }</code>
    • Коментар резолюції: <code>{ $resolution_note }</code>

messages-admin_stars_sell_admin_list_screen =
    <b>Продаж зірок · Керування заявками</b>

    Обери заявку для керування.
    • Сторінка: <code>{ $page }</code>

messages-admin_stars_sell_admin_list_empty_screen =
    <b>Продаж зірок · Керування заявками</b>

    Заявок для керування поки немає.

messages-admin_stars_sell_admin_detail_not_found =
    ⚠️ Заявку не знайдено.

messages-admin_stars_sell_admin_detail_screen =
    <b>Керування заявкою #{ $order_id }</b>

    • User ID: <code>{ $user_id }</code>
    • Статус: <code>{ $status }</code>
    • Кількість: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • До виплати: <code>{ $payout_amount } USD</code>
    • Гаманець: <code>{ $wallet }</code>
    • Сума інвойсу: <code>{ $invoice_stars }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>

    <b>Таймлайн:</b>
    • Створено: { $created_at }
    • Оплачено: { $paid_at }
    • Доступно до виплати: { $payout_available_at }
    • Завершено: { $completed_at }
    • Відхилено: { $rejected_at }
    • Рефанд: { $refunded_at }

    <b>Технічні дані:</b>
    • Invoice payload: <code>{ $invoice_payload }</code>
    • Сплачено в Stars: <code>{ $paid_stars }</code>
    • Причина помилки: <code>{ $failure_reason }</code>
    • Причина резолюції: <code>{ $resolution_reason }</code>
    • Коментар резолюції: <code>{ $resolution_note }</code>

messages-admin_stars_sell_status_pending_payment = очікує оплату
messages-admin_stars_sell_status_paid_hold = оплачено (холд)
messages-admin_stars_sell_status_paid_hold_ready = оплачено (готово до виводу)
messages-admin_stars_sell_status_completed = завершено
messages-admin_stars_sell_status_canceled = скасовано
messages-admin_stars_sell_status_rejected = відхилено
messages-admin_stars_sell_status_refunded = відхилено
messages-admin_stars_sell_status_failed = помилка

messages-admin_stars_sell_reason_replaced_by_new_request = замінено новою заявкою
messages-admin_stars_sell_reason_user_request = запит користувача
messages-admin_stars_sell_reason_invalid_payout_wallet = некоректний гаманець виплати
messages-admin_stars_sell_reason_stars_refunded = Stars повернуто
messages-admin_stars_sell_reason_stars_not_withdrawable = Stars недоступні для виводу
messages-admin_stars_sell_reason_fraud_suspected = підозра на фрод
messages-admin_stars_sell_reason_kyc_or_fragment_restriction = KYC/обмеження Fragment
messages-admin_stars_sell_reason_payout_technical_failure = технічна помилка виплати
messages-admin_stars_sell_reason_policy_restriction = обмеження політики
messages-admin_stars_sell_reason_other = інша причина

messages-admin_stars_sell_history_page_indicator = { $current }/{ $total }
messages-admin_stars_sell_history_item_button = #{ $order_id } · { $status } · { $stars_count } зірок · { $payout_amount } USD

messages-admin_stars_sell_admin_page_indicator = { $current }/{ $total }
messages-admin_stars_sell_admin_item_button = #{ $order_id } · #{ $user_id } · { $status } · { $stars_count } зірок · { $payout_amount } USD

messages-admin_stars_sell_stars_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Введи ціле додатне число (кількість зірок).</blockquote>
messages-admin_stars_sell_stars_out_of_range = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Кількість зірок має бути в межах <code>{ $min_stars }</code>–<code>{ $max_stars }</code>.</blockquote>
messages-admin_stars_sell_wallet_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некоректний TON-гаманець. Використай формат <code>UQ...</code> або <code>EQ...</code>.</blockquote>
messages-admin_stars_sell_stars_missing = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Спочатку вкажи кількість зірок.</blockquote>
messages-admin_stars_sell_wallet_missing = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Спочатку вкажи гаманець для виплати.</blockquote>
messages-admin_stars_sell_order_create_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не вдалося створити заявку на продаж. Спробуй пізніше.</blockquote>
messages-admin_stars_sell_invoice_send_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не вдалося надіслати інвойс. Спробуй ще раз.</blockquote>
messages-admin_stars_sell_invoice_sent = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Інвойс на оплату зірками надіслано. Заявка: <code>{ $order_id }</code>.</blockquote>
messages-admin_stars_sell_invoice_resent = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Для відкритої заявки <code>{ $order_id }</code> надіслано новий інвойс.</blockquote>
messages-admin_stars_sell_invoice_replaced = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Попередню неоплачену заявку скасовано. Створено нову: <code>{ $order_id }</code>.</blockquote>
messages-admin_stars_sell_invoice_canceled = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Заявку скасовано.</blockquote>
messages-admin_stars_sell_invoice_cancel_unavailable = <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Цю заявку вже не можна скасувати.</blockquote>
messages-admin_stars_sell_invoice_cancel_not_found = <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Заявку не знайдено.</blockquote>

messages-admin_stars_sell_admin_action_completed = ✅ Заявку <code>{ $order_id }</code> позначено як завершену.
messages-admin_stars_sell_admin_action_rejected = ✅ Заявку <code>{ $order_id }</code> відхилено.
messages-admin_stars_sell_admin_action_not_ready = ⚠️ Заявка <code>{ $order_id }</code> ще на холді. Доступно після: <code>{ $payout_available_at }</code>.
messages-admin_stars_sell_admin_action_conflict = ⚠️ Статус заявки <code>{ $order_id }</code> вже змінено. Онови дані.
messages-admin_stars_sell_admin_action_failed = ❌ Не вдалося виконати дію для заявки <code>{ $order_id }</code>.

messages-admin_stars_sell_invoice_title = Продаж Telegram Stars
messages-admin_stars_sell_invoice_description = Продаж { $stars_count } ⭐. Після підтвердження оплати виплата { $payout_amount } USD стане доступною через { $hold_days_text }.
messages-admin_stars_sell_invoice_label = Продаж { $stars_count } ⭐

messages-admin_stars_sell_payment_confirmed =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Оплату зірками підтверджено</b></blockquote>

    • Заявка: <code>{ $order_id }</code>
    • Сплачено: <code>{ $stars_count }</code> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji>
    • До виплати: <code>{ $payout_amount } USD</code>
    • Гаманець: <code>{ $wallet }</code>
    • Доступно до ручного виводу після: <code>{ $payout_available_at }</code>
    • Холд: <code>{ $hold_days_text }</code>

messages-admin_stats_screen =
    <blockquote><b>📊 Статистика</b></blockquote>

    <b>Користувачі</b>
    • Всього: <b>{ $users_total }</b>
    • Активні: <b>{ $users_active }</b>
    • З балансом: <b>{ $users_with_balance }</b>
    • Сумарний баланс: <b>{ $users_balance_total } USD</b>

    <b>Замовлення</b>
    • Всього: <b>{ $orders_total }</b>
    • Нові 24h: <b>{ $orders_new_24h }</b>
    • Нові 7d: <b>{ $orders_new_7d }</b>
    • Оплачено 24h: <b>{ $orders_paid_24h }</b> (<b>{ $orders_paid_amount_24h } USD</b>)
    • Оплачено 7d: <b>{ $orders_paid_7d }</b> (<b>{ $orders_paid_amount_7d } USD</b>)
    • Успішно завершено (сума): <b>{ $orders_completed_amount } USD</b>

    <b>Статуси</b>
    • creating_payment: <b>{ $status_creating }</b>
    • pending_payment: <b>{ $status_pending }</b>
    • payment_confirmed: <b>{ $status_paid }</b>
    • fulfilling: <b>{ $status_fulfilling }</b>
    • completed: <b>{ $status_completed }</b>
    • failed: <b>{ $status_failed }</b>
    • canceled: <b>{ $status_canceled }</b>

    <b>Виконані продукти</b>
    • Stars: <b>{ $completed_stars_count }</b> зам. · <b>{ $completed_stars_units }</b> ⭐ · <b>{ $completed_stars_amount } USD</b>
    • Premium: <b>{ $completed_premium_count }</b> зам. · <b>{ $completed_premium_amount } USD</b>
    • Top-up: <b>{ $completed_topup_count }</b> зам. · <b>{ $completed_topup_amount } USD</b>

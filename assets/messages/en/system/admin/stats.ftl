messages-admin_stats_screen =
    <blockquote><b>📊 Statistics</b></blockquote>

    <b>Users</b>
    • Total: <b>{ $users_total }</b>
    • Active: <b>{ $users_active }</b>
    • With balance: <b>{ $users_with_balance }</b>
    • Total balances: <b>{ $users_balance_total } USD</b>

    <b>Orders</b>
    • Total: <b>{ $orders_total }</b>
    • New 24h: <b>{ $orders_new_24h }</b>
    • New 7d: <b>{ $orders_new_7d }</b>
    • Paid 24h: <b>{ $orders_paid_24h }</b> (<b>{ $orders_paid_amount_24h } USD</b>)
    • Paid 7d: <b>{ $orders_paid_7d }</b> (<b>{ $orders_paid_amount_7d } USD</b>)
    • Completed amount: <b>{ $orders_completed_amount } USD</b>

    <b>Statuses</b>
    • creating_payment: <b>{ $status_creating }</b>
    • pending_payment: <b>{ $status_pending }</b>
    • payment_confirmed: <b>{ $status_paid }</b>
    • fulfilling: <b>{ $status_fulfilling }</b>
    • completed: <b>{ $status_completed }</b>
    • failed: <b>{ $status_failed }</b>
    • canceled: <b>{ $status_canceled }</b>

    <b>Completed products</b>
    • Stars: <b>{ $completed_stars_count }</b> orders · <b>{ $completed_stars_units }</b> ⭐ · <b>{ $completed_stars_amount } USD</b>
    • Premium: <b>{ $completed_premium_count }</b> orders · <b>{ $completed_premium_amount } USD</b>
    • Top-up: <b>{ $completed_topup_count }</b> orders · <b>{ $completed_topup_amount } USD</b>

messages-admin_stats_screen =
    <blockquote><b><tg-emoji emoji-id="5381817355892465423">📊</tg-emoji> Статистика</b></blockquote>

    <b>Пользователи</b>
    • Всего: <b>{ $users_total }</b>
    • Активные: <b>{ $users_active }</b>
    • С балансом: <b>{ $users_with_balance }</b>
    • Суммарный баланс: <b>{ $users_balance_total } USD</b>

    <b>Заказы</b>
    • Всего: <b>{ $orders_total }</b>
    • Новые за 24 ч: <b>{ $orders_new_24h }</b>
    • Новые за 7 дней: <b>{ $orders_new_7d }</b>
    • Выполнено за 24 ч: <b>{ $orders_paid_24h }</b> (<b>{ $orders_paid_amount_24h } USD</b>)
    • Выполнено за 7 дней: <b>{ $orders_paid_7d }</b> (<b>{ $orders_paid_amount_7d } USD</b>)
    • Успешно завершено (сумма): <b>{ $orders_completed_amount } USD</b>

    <b>Статусы</b>
    • Создание оплаты: <b>{ $status_creating }</b>
    • Ожидают оплату: <b>{ $status_pending }</b>
    • Оплата подтверждена: <b>{ $status_paid }</b>
    • Выполняются: <b>{ $status_fulfilling }</b>
    • Завершены: <b>{ $status_completed }</b>
    • Ошибка: <b>{ $status_failed }</b>
    • Отменены: <b>{ $status_canceled }</b>

    <b>Выполненные продукты</b>
    • Stars: <b>{ $completed_stars_count }</b> заказов · <b>{ $completed_stars_units }</b> <tg-emoji emoji-id="5381819344462327797">⭐</tg-emoji> · <b>{ $completed_stars_amount } USD</b>
    • Premium: <b>{ $completed_premium_count }</b> заказов · <b>{ $completed_premium_amount } USD</b>
    • Пополнения: <b>{ $completed_topup_count }</b> заказов · <b>{ $completed_topup_amount } USD</b>

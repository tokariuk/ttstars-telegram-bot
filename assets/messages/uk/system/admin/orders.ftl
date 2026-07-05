messages-admin_orders_menu =
    <blockquote><b>📦 Керування ордерами</b></blockquote>

    Тут можна вручну перезапустити доставку ордера:
    • <b>Retry fulfill</b> — безпечна повторна перевірка/доставка
    • <b>Force fulfill</b> — примусова доставка (використовуй обережно)

messages-admin_orders_retry_prompt =
    Надішли ID ордера для <b>Retry fulfill</b>.
    Приклад: <code>12345</code>

messages-admin_orders_force_prompt =
    Надішли ID ордера для <b>Force fulfill</b>.
    Приклад: <code>12345</code>

messages-admin_orders_input_invalid = <blockquote>❌ Вкажи коректний числовий ID ордера. Приклад: <code>12345</code>.</blockquote>
messages-admin_orders_not_found = <blockquote>❌ Ордер <code>{ $order_id }</code> не знайдено.</blockquote>
messages-admin_orders_force_debit_failed = <blockquote>❌ Не вдалося зробити Force fulfill для ордера <code>{ $order_id }</code>: кошти <b>{ $amount } USD</b>, які були повернені на баланс, вже витрачені.</blockquote>
messages-admin_orders_action_done =
    <blockquote>✅ { $action }</blockquote>

    • Ордер: <code>{ $order_id }</code>
    • Результат: <b>{ $outcome }</b>
    • Статус: <code>{ $status }</code>
    • Статус провайдера: <code>{ $provider_status }</code>
    • TX: <code>{ $tx_hash }</code>
    • Помилка: <code>{ $error }</code>

messages-admin_orders_action_retry = Retry fulfill виконано
messages-admin_orders_action_force = Force fulfill виконано
messages-admin_orders_outcome_pending = очікує оплату
messages-admin_orders_outcome_processing = обробляється
messages-admin_orders_outcome_completed = завершено
messages-admin_orders_outcome_failed = невдача
messages-admin_orders_outcome_canceled = скасовано
messages-admin_orders_outcome_not_found = не знайдено

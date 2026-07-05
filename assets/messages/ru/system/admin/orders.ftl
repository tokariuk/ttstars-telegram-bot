messages-admin_orders_menu =
    <blockquote><b>📦 Управление ордерами</b></blockquote>

    Ручные действия по доставке ордера:
    • <b>Retry fulfill</b> — безопасный повтор с обычными проверками
    • <b>Force fulfill</b> — принудительная доставка (используй осторожно)

messages-admin_orders_retry_prompt =
    Отправь ID ордера для <b>Retry fulfill</b>.
    Пример: <code>12345</code>

messages-admin_orders_force_prompt =
    Отправь ID ордера для <b>Force fulfill</b>.
    Пример: <code>12345</code>

messages-admin_orders_input_invalid = <blockquote>❌ Укажи корректный числовой ID ордера. Пример: <code>12345</code>.</blockquote>
messages-admin_orders_not_found = <blockquote>❌ Ордер <code>{ $order_id }</code> не найден.</blockquote>
messages-admin_orders_force_debit_failed = <blockquote>❌ Не удалось выполнить Force fulfill для ордера <code>{ $order_id }</code>: возвращенные <b>{ $amount } USD</b> уже потрачены с баланса.</blockquote>
messages-admin_orders_action_done =
    <blockquote>✅ { $action }</blockquote>

    • Ордер: <code>{ $order_id }</code>
    • Результат: <b>{ $outcome }</b>
    • Статус: <code>{ $status }</code>
    • Статус провайдера: <code>{ $provider_status }</code>
    • TX: <code>{ $tx_hash }</code>
    • Ошибка: <code>{ $error }</code>

messages-admin_orders_action_retry = Retry fulfill выполнен
messages-admin_orders_action_force = Force fulfill выполнен
messages-admin_orders_outcome_pending = ожидает оплату
messages-admin_orders_outcome_processing = обрабатывается
messages-admin_orders_outcome_completed = завершён
messages-admin_orders_outcome_failed = ошибка
messages-admin_orders_outcome_canceled = отменён
messages-admin_orders_outcome_not_found = не найден

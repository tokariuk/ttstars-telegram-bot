messages-admin_orders_menu =
    <blockquote><b>📦 Управление ордерами</b></blockquote>

    Ручные действия по доставке заказа:
    • <b>Повторить доставку</b> — снова запускает обычные проверки
    • <b>Принудить доставку</b> — обходит часть защит; используй только после проверки оплаты

messages-admin_orders_retry_prompt =
    Отправь ID заказа для повторной доставки.
    Пример: <code>12345</code>

messages-admin_orders_force_prompt =
    Отправь ID заказа для принудительной доставки.
    <b>Внимание:</b> действие может выдать продукт без повторной проверки провайдера.
    Пример: <code>12345</code>

messages-admin_orders_input_invalid = <blockquote>❌ Укажи корректный числовой ID ордера. Пример: <code>12345</code>.</blockquote>
messages-admin_orders_not_found = <blockquote>❌ Ордер <code>{ $order_id }</code> не найден.</blockquote>
messages-admin_orders_force_debit_failed = <blockquote>❌ Принудительная доставка заказа <code>{ $order_id }</code> остановлена: возвращённые <b>{ $amount } USD</b> уже потрачены с баланса. Продукт не выдан.</blockquote>
messages-admin_orders_action_done =
    <blockquote>✅ { $action }</blockquote>

    • Ордер: <code>{ $order_id }</code>
    • Результат: <b>{ $outcome }</b>
    • Статус: <code>{ $status }</code>
    • Статус провайдера: <code>{ $provider_status }</code>
    • TX: <code>{ $tx_hash }</code>
    • Ошибка: <code>{ $error }</code>

messages-admin_orders_action_retry = Повторная доставка выполнена
messages-admin_orders_action_force = Принудительная доставка выполнена
messages-admin_orders_outcome_pending = ожидает оплату
messages-admin_orders_outcome_processing = обрабатывается
messages-admin_orders_outcome_completed = завершён
messages-admin_orders_outcome_failed = ошибка
messages-admin_orders_outcome_canceled = отменён
messages-admin_orders_outcome_not_found = не найден

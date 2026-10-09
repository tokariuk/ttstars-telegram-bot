messages-admin_orders_menu =
    <blockquote><b><tg-emoji emoji-id="5379646374478392537">📦</tg-emoji> Управление заказами</b></blockquote>

    Ручные действия по доставке заказа:
    • <b>Повторить доставку</b> — снова запускает обычные проверки
    • <b>Принудить доставку</b> — обходит часть защит; используй только после проверки оплаты

messages-admin_orders_retry_prompt =
    <blockquote><b><tg-emoji emoji-id="5381856410030087819">🔄</tg-emoji> Повторная доставка</b></blockquote>

    Отправь ID заказа для повторной доставки.
    Пример: <code>12345</code>

messages-admin_orders_force_prompt =
    <blockquote><b><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Принудительная доставка</b></blockquote>

    Отправь ID заказа для принудительной доставки.
    <b>Внимание:</b> действие может выдать продукт без повторной проверки провайдера.
    Пример: <code>12345</code>

messages-admin_orders_input_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Укажи числовой ID заказа. Пример: <code>12345</code>.</blockquote>
messages-admin_orders_not_found = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Заказ <code>{ $order_id }</code> не найден.</blockquote>
messages-admin_orders_force_debit_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Принудительная доставка заказа <code>{ $order_id }</code> остановлена: возвращённые <b>{ $amount } USD</b> уже потрачены с баланса. Продукт не выдан.</blockquote>
messages-admin_orders_action_done =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> { $action }</b></blockquote>

    • Заказ: <code>{ $order_id }</code>
    • Результат: <b>{ $outcome }</b>
    • Статус: <code>{ $status }</code>
    <blockquote expandable><b>Технические данные</b>
    • Статус провайдера: <code>{ $provider_status }</code>
    • TX: <code>{ $tx_hash }</code>
    • Ошибка: <code>{ $error }</code></blockquote>

messages-admin_orders_action_retry = Повторная доставка выполнена
messages-admin_orders_action_force = Принудительная доставка выполнена
messages-admin_orders_outcome_pending = ожидает оплату
messages-admin_orders_outcome_processing = обрабатывается
messages-admin_orders_outcome_completed = завершён
messages-admin_orders_outcome_failed = ошибка
messages-admin_orders_outcome_canceled = отменён
messages-admin_orders_outcome_not_found = не найден

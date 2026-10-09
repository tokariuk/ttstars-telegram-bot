messages-admin_orders_menu =
    <blockquote><b><tg-emoji emoji-id="5379646374478392537">📦</tg-emoji> Керування замовленнями</b></blockquote>

    Ручні дії для доставки замовлення:
    • <b>Повторити доставку</b> — знову запускає звичайні перевірки
    • <b>Примусити доставку</b> — обходить частину захистів; використовуй лише після перевірки оплати

messages-admin_orders_retry_prompt =
    <blockquote><b><tg-emoji emoji-id="5381856410030087819">🔄</tg-emoji> Повторна доставка</b></blockquote>

    Надішли ID замовлення для повторної доставки.
    Приклад: <code>12345</code>

messages-admin_orders_force_prompt =
    <blockquote><b><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Примусова доставка</b></blockquote>

    Надішли ID замовлення для примусової доставки.
    <b>Увага:</b> дія може видати продукт без повторної перевірки провайдера.
    Приклад: <code>12345</code>

messages-admin_orders_input_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Вкажи числовий ID замовлення. Приклад: <code>12345</code>.</blockquote>
messages-admin_orders_not_found = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Замовлення <code>{ $order_id }</code> не знайдено.</blockquote>
messages-admin_orders_force_debit_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Примусову доставку замовлення <code>{ $order_id }</code> зупинено: повернені <b>{ $amount } USD</b> уже витрачено з балансу. Продукт не видано.</blockquote>
messages-admin_orders_action_done =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> { $action }</b></blockquote>

    • Замовлення: <code>{ $order_id }</code>
    • Результат: <b>{ $outcome }</b>
    • Статус: <code>{ $status }</code>
    <blockquote expandable><b>Технічні дані</b>
    • Статус провайдера: <code>{ $provider_status }</code>
    • TX: <code>{ $tx_hash }</code>
    • Помилка: <code>{ $error }</code></blockquote>

messages-admin_orders_action_retry = Повторну доставку виконано
messages-admin_orders_action_force = Примусову доставку виконано
messages-admin_orders_outcome_pending = очікує оплату
messages-admin_orders_outcome_processing = обробляється
messages-admin_orders_outcome_completed = завершено
messages-admin_orders_outcome_failed = невдача
messages-admin_orders_outcome_canceled = скасовано
messages-admin_orders_outcome_not_found = не знайдено

messages-admin_orders_menu =
    <blockquote><b>📦 Керування ордерами</b></blockquote>

    Ручні дії для доставки замовлення:
    • <b>Повторити доставку</b> — знову запускає звичайні перевірки
    • <b>Примусити доставку</b> — обходить частину захистів; використовуй лише після перевірки оплати

messages-admin_orders_retry_prompt =
    Надішли ID замовлення для повторної доставки.
    Приклад: <code>12345</code>

messages-admin_orders_force_prompt =
    Надішли ID замовлення для примусової доставки.
    <b>Увага:</b> дія може видати продукт без повторної перевірки провайдера.
    Приклад: <code>12345</code>

messages-admin_orders_input_invalid = <blockquote>❌ Вкажи коректний числовий ID ордера. Приклад: <code>12345</code>.</blockquote>
messages-admin_orders_not_found = <blockquote>❌ Ордер <code>{ $order_id }</code> не знайдено.</blockquote>
messages-admin_orders_force_debit_failed = <blockquote>❌ Примусову доставку замовлення <code>{ $order_id }</code> зупинено: повернені <b>{ $amount } USD</b> вже витрачено з балансу. Продукт не видано.</blockquote>
messages-admin_orders_action_done =
    <blockquote>✅ { $action }</blockquote>

    • Ордер: <code>{ $order_id }</code>
    • Результат: <b>{ $outcome }</b>
    • Статус: <code>{ $status }</code>
    • Статус провайдера: <code>{ $provider_status }</code>
    • TX: <code>{ $tx_hash }</code>
    • Помилка: <code>{ $error }</code>

messages-admin_orders_action_retry = Повторну доставку виконано
messages-admin_orders_action_force = Примусову доставку виконано
messages-admin_orders_outcome_pending = очікує оплату
messages-admin_orders_outcome_processing = обробляється
messages-admin_orders_outcome_completed = завершено
messages-admin_orders_outcome_failed = невдача
messages-admin_orders_outcome_canceled = скасовано
messages-admin_orders_outcome_not_found = не знайдено

messages-admin_orders_menu =
    <blockquote><b>📦 Order Management</b></blockquote>

    Manual order fulfillment actions:
    • <b>Retry fulfill</b> — safe retry with regular checks
    • <b>Force fulfill</b> — forced delivery (use carefully)

messages-admin_orders_retry_prompt =
    Send order ID for <b>Retry fulfill</b>.
    Example: <code>12345</code>

messages-admin_orders_force_prompt =
    Send order ID for <b>Force fulfill</b>.
    Example: <code>12345</code>

messages-admin_orders_input_invalid = <blockquote>❌ Send a valid numeric order ID. Example: <code>12345</code>.</blockquote>
messages-admin_orders_not_found = <blockquote>❌ Order <code>{ $order_id }</code> not found.</blockquote>
messages-admin_orders_force_debit_failed = <blockquote>❌ Force fulfill failed for order <code>{ $order_id }</code>: refunded <b>{ $amount } USD</b> was already spent from balance.</blockquote>
messages-admin_orders_action_done =
    <blockquote>✅ { $action }</blockquote>

    • Order: <code>{ $order_id }</code>
    • Outcome: <b>{ $outcome }</b>
    • Status: <code>{ $status }</code>
    • Provider status: <code>{ $provider_status }</code>
    • TX: <code>{ $tx_hash }</code>
    • Error: <code>{ $error }</code>

messages-admin_orders_action_retry = Retry fulfill executed
messages-admin_orders_action_force = Force fulfill executed
messages-admin_orders_outcome_pending = pending payment
messages-admin_orders_outcome_processing = processing
messages-admin_orders_outcome_completed = completed
messages-admin_orders_outcome_failed = failed
messages-admin_orders_outcome_canceled = canceled
messages-admin_orders_outcome_not_found = not found

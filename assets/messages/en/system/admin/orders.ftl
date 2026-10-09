messages-admin_orders_menu =
    <blockquote><b><tg-emoji emoji-id="5379646374478392537">📦</tg-emoji> Order management</b></blockquote>

    Manual delivery actions:
    • <b>Retry delivery</b> — runs the normal checks again
    • <b>Force delivery</b> — bypasses some safeguards; use only after verifying payment

messages-admin_orders_retry_prompt =
    <blockquote><b><tg-emoji emoji-id="5381856410030087819">🔄</tg-emoji> Retry delivery</b></blockquote>

    Send the order ID to retry delivery.
    Example: <code>12345</code>

messages-admin_orders_force_prompt =
    <blockquote><b><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Force delivery</b></blockquote>

    Send the order ID to force delivery.
    <b>Warning:</b> this can deliver the product without another provider check.
    Example: <code>12345</code>

messages-admin_orders_input_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Send a numeric order ID. Example: <code>12345</code>.</blockquote>
messages-admin_orders_not_found = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Order <code>{ $order_id }</code> was not found.</blockquote>
messages-admin_orders_force_debit_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Force delivery stopped for order <code>{ $order_id }</code>: the refunded <b>{ $amount } USD</b> was already spent. The product was not delivered.</blockquote>
messages-admin_orders_action_done =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> { $action }</b></blockquote>

    • Order: <code>{ $order_id }</code>
    • Outcome: <b>{ $outcome }</b>
    • Status: <code>{ $status }</code>
    <blockquote expandable><b>Technical details</b>
    • Provider status: <code>{ $provider_status }</code>
    • TX: <code>{ $tx_hash }</code>
    • Error: <code>{ $error }</code></blockquote>

messages-admin_orders_action_retry = Delivery retry completed
messages-admin_orders_action_force = Forced delivery completed
messages-admin_orders_outcome_pending = pending payment
messages-admin_orders_outcome_processing = processing
messages-admin_orders_outcome_completed = completed
messages-admin_orders_outcome_failed = failed
messages-admin_orders_outcome_canceled = canceled
messages-admin_orders_outcome_not_found = not found

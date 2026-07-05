messages-admin_promo_menu =
    <blockquote><b>🔑 Promo Management</b></blockquote>

    Active codes: <b>{ $active_codes }</b> of <b>{ $total_codes }</b>
    Tap a promo code below to manage it individually.

messages-admin_promo_list_empty = No promo codes yet.
messages-admin_promo_item = • <code>{ $code }</code> — <b>{ $amount } USD</b> · { $activations }/{ $max_activations }
messages-admin_promo_item_button = { $code } · { $amount } USD · { $activations }/{ $max_activations }
messages-admin_promo_page_indicator = { $current }/{ $total }
messages-admin_promo_bulk_mode_hint = Bulk delete mode is active. Selected: <b>{ $selected }</b>
messages-admin_promo_details =
    <blockquote><b>🔑 Promo Code <code>{ $code }</code></b></blockquote>

    • Amount: <b>{ $amount } USD</b>
    • Activations: <b>{ $activations }/{ $max_activations }</b>
    • Status: <b>{ $status }</b>
    • Created: { $created_at }

messages-admin_promo_status_active = active
messages-admin_promo_status_exhausted = exhausted
messages-admin_limit_unlimited = ∞

messages-admin_promo_create_prompt =
    Format:
    <code>CODE 5</code>
    or
    <code>CODE 5 100</code>

    Third value is activation limit, <code>0</code> = unlimited.

messages-admin_promo_create_invalid = <blockquote>❌ Invalid format. Example: <code>WELCOME5 5 100</code>.</blockquote>
messages-admin_promo_create_failed = <blockquote>❌ Failed to create promo code: { $error }</blockquote>
messages-admin_promo_created = <blockquote>✅ Created <code>{ $code }</code> for <b>{ $amount } USD</b>, limit: <b>{ $max_activations }</b>.</blockquote>

messages-admin_promo_quick_prompt =
    Format:
    <code>5</code>
    or
    <code>5 BONUS</code>

    Where:
    • 5 — amount in USD
    • BONUS — prefix (optional)

messages-admin_promo_quick_invalid = <blockquote>❌ Invalid format. Example: <code>5 BONUS</code>.</blockquote>
messages-admin_promo_quick_failed = <blockquote>❌ Failed to create promo code: { $error }</blockquote>
messages-admin_promo_quick_done =
    <blockquote>✅ One-time promo code <code>{ $code }</code> for <b>{ $amount } USD</b> created.</blockquote>

messages-admin_promo_bulk_prompt =
    Format:
    <code>5 20 BONUS</code>

    Where:
    • 5 — amount in USD
    • 20 — number of unique one-time codes
    • BONUS — prefix (optional)

messages-admin_promo_bulk_invalid = <blockquote>❌ Invalid format. Example: <code>5 20 BONUS</code>.</blockquote>
messages-admin_promo_bulk_failed = <blockquote>❌ Failed to create promo codes: { $error }</blockquote>
messages-admin_promo_bulk_done =
    <blockquote>✅ Created { $count } one-time codes for <b>{ $amount } USD</b> each.</blockquote>

    <code>{ $codes }</code>
messages-admin_promo_bulk_item_selected = Code { $code } added to selection.
messages-admin_promo_bulk_item_unselected = Code { $code } removed from selection.
messages-admin_promo_bulk_delete_empty = No promo codes selected for deletion.
messages-admin_promo_bulk_delete_done = <blockquote>✅ Deleted selected promo codes: <b>{ $count }</b>.</blockquote>

messages-admin_promo_set_limit_prompt =
    Set new activation limit for <code>{ $code }</code>:
    • just a number: <code>1</code>, <code>10</code>, <code>0</code> (unlimited)
    • or full format: <code>CODE 10</code>

messages-admin_promo_set_limit_invalid = <blockquote>❌ Invalid format. Example: <code>10</code> or <code>WELCOME5 10</code>.</blockquote>
messages-admin_promo_set_limit_failed = <blockquote>❌ Failed to update limit: { $error }</blockquote>
messages-admin_promo_set_limit_done = <blockquote>✅ Updated limit for <code>{ $code }</code>: <b>{ $max_activations }</b>.</blockquote>

messages-admin_promo_delete_prompt = Send promo code to delete, for example: <code>WELCOME5</code>
messages-admin_promo_delete_invalid = <blockquote>❌ Send a promo code in one line.</blockquote>
messages-admin_promo_deleted = <blockquote>✅ Promo code <code>{ $code }</code> deleted.</blockquote>
messages-admin_promo_not_found = <blockquote>❌ Promo code not found.</blockquote>
messages-admin_promo_cleanup_done = <blockquote>✅ Removed exhausted promo codes: <b>{ $count }</b>.</blockquote>

messages-admin_promo_menu =
    <blockquote><b><tg-emoji emoji-id="5380101288824450052">🔑</tg-emoji> Promo codes</b></blockquote>

    Active codes: <b>{ $active_codes }</b> of <b>{ $total_codes }</b>
    Tap a promo code below to manage it individually.

messages-admin_promo_list_empty = No promo codes yet. Create the first code with a button below.
messages-admin_promo_item = • <code>{ $code }</code> — <b>{ $amount } USD</b> · { $activations }/{ $max_activations }
messages-admin_promo_item_button = { $code } · { $amount } USD · { $activations }/{ $max_activations }
messages-admin_promo_page_indicator = { $current }/{ $total }
messages-admin_promo_bulk_mode_hint = Bulk delete mode is active. Selected: <b>{ $selected }</b>
messages-admin_promo_details =
    <blockquote><b><tg-emoji emoji-id="5380101288824450052">🔑</tg-emoji> Promo code <code>{ $code }</code></b></blockquote>

    • Amount: <b>{ $amount } USD</b>
    • Activations: <b>{ $activations }/{ $max_activations }</b>
    • Status: <b>{ $status }</b>
    • Created: { $created_at }
    • Activated users:
    { $activated_users }

messages-admin_promo_status_active = active
messages-admin_promo_status_exhausted = exhausted
messages-admin_promo_status_disabled = disabled
messages-admin_promo_toggle_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Promo code <code>{ $code }</code> is now <b>{ $status }</b>.</blockquote>
messages-admin_limit_unlimited = ∞

messages-admin_promo_create_prompt =
    <blockquote><b><tg-emoji emoji-id="5379761711530163623">➕</tg-emoji> New promo code</b></blockquote>

    Format:
    <code>CODE 5</code>
    or
    <code>CODE 5 100</code>

    Third value is activation limit, <code>0</code> = unlimited.

messages-admin_promo_create_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Invalid format. Example: <code>WELCOME5 5 100</code>.</blockquote>
messages-admin_promo_create_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Failed to create promo code: { $error }</blockquote>
messages-admin_promo_created = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Created <code>{ $code }</code> for <b>{ $amount } USD</b>, limit: <b>{ $max_activations }</b>.</blockquote>

messages-admin_promo_quick_prompt =
    <blockquote><b><tg-emoji emoji-id="5380078671526666610">⚡</tg-emoji> Quick one-time code</b></blockquote>

    Format:
    <code>5</code>
    or
    <code>5 BONUS</code>

    Where:
    • 5 — amount in USD
    • BONUS — prefix (optional)

messages-admin_promo_quick_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Invalid format. Example: <code>5 BONUS</code>.</blockquote>
messages-admin_promo_quick_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Failed to create promo code: { $error }</blockquote>
messages-admin_promo_quick_done =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> One-time promo code <code>{ $code }</code> for <b>{ $amount } USD</b> created.</blockquote>

messages-admin_promo_bulk_prompt =
    <blockquote><b><tg-emoji emoji-id="5379646374478392537">📦</tg-emoji> Promo code batch</b></blockquote>

    Format:
    <code>5 20 BONUS</code>

    Where:
    • 5 — amount in USD
    • 20 — number of unique one-time codes
    • BONUS — prefix (optional)

messages-admin_promo_bulk_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Invalid format. Example: <code>5 20 BONUS</code>.</blockquote>
messages-admin_promo_bulk_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Failed to create promo codes: { $error }</blockquote>
messages-admin_promo_bulk_done =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Created { $count } one-time codes for <b>{ $amount } USD</b> each.</blockquote>

    <code>{ $codes }</code>
messages-admin_promo_bulk_item_selected = Code { $code } added to selection.
messages-admin_promo_bulk_item_unselected = Code { $code } removed from selection.
messages-admin_promo_bulk_delete_empty = No promo codes selected for deletion.
messages-admin_promo_bulk_delete_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Deleted selected promo codes: <b>{ $count }</b>.</blockquote>

messages-admin_promo_set_limit_prompt =
    <blockquote><b><tg-emoji emoji-id="5382118858301676590">⚙️</tg-emoji> Activation limit</b></blockquote>

    Set new activation limit for <code>{ $code }</code>:
    • just a number: <code>1</code>, <code>10</code>, <code>0</code> (unlimited)
    • or full format: <code>CODE 10</code>

messages-admin_promo_set_limit_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Invalid format. Example: <code>10</code> or <code>WELCOME5 10</code>.</blockquote>
messages-admin_promo_set_limit_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Failed to update limit: { $error }</blockquote>
messages-admin_promo_set_limit_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Updated limit for <code>{ $code }</code>: <b>{ $max_activations }</b>.</blockquote>

messages-admin_promo_delete_prompt = Send promo code to delete, for example: <code>WELCOME5</code>
messages-admin_promo_delete_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Send a promo code in one line.</blockquote>
messages-admin_promo_deleted = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Promo code <code>{ $code }</code> deleted.</blockquote>
messages-admin_promo_not_found = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Promo code was not found.</blockquote>
messages-admin_promo_cleanup_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Removed exhausted promo codes: <b>{ $count }</b>.</blockquote>

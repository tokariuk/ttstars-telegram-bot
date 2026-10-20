messages-admin_broadcast_content_prompt =
    <blockquote><b><tg-emoji emoji-id="5381969161511543757">🔔</tg-emoji> Broadcast · Step 1/4</b></blockquote>

    Send broadcast content:
    • text with HTML formatting and premium emojis
    • or photo with caption

messages-admin_broadcast_content_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Send a text message or a photo with caption.</blockquote>

messages-admin_broadcast_options_prompt =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Broadcast · Step 2/4</b></blockquote>

    Configure recipients and close button.

    Available locales: <code>{ $locales }</code>
    Selected locales: <b>{ $selected_locales }</b>
    Close button: <b>{ $close_button }</b>
    Link preview: <b>{ $link_preview }</b>

    Format:
    <code>all</code>
    <code>en,uk close</code>
    <code>ru no_close</code>

    Or tap “Skip” to use defaults (all + without close button).

messages-admin_broadcast_options_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Invalid broadcast options: { $error }</blockquote>
messages-admin_broadcast_option_enabled = enabled
messages-admin_broadcast_option_disabled = disabled
messages-admin_broadcast_link_preview_disable = Remove link preview
messages-admin_broadcast_link_preview_enable = Show link preview

messages-admin_broadcast_buttons_prompt =
    <blockquote><b><tg-emoji emoji-id="5382283505872967732">🔗</tg-emoji> Broadcast · Step 3/4</b></blockquote>

    Send link buttons (one per line):
    <code>Text | https://example.com</code>

    Or tap “Skip”.

messages-admin_broadcast_buttons_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Invalid buttons: { $error }</blockquote>

messages-admin_broadcast_preview_ready =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Broadcast · Step 4/4</b></blockquote>

    Recipients: <b>{ $recipients }</b>
    Locales: <b>{ $locales }</b>
    Close button: <b>{ $close_button }</b>
    Link preview: <b>{ $link_preview }</b>
    Buttons: <b>{ $buttons }</b>

messages-admin_broadcast_preview_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Failed to build preview. Check message formatting.</blockquote>
messages-admin_broadcast_preview_failed_detail =
    <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Broadcast not started</blockquote>

    Telegram rejected the test message: <code>{ $reason }</code>
    Fix the content or buttons and try again.
messages-admin_broadcast_preview_content = Content
messages-admin_broadcast_preview_buttons = Buttons
messages-admin_broadcast_preview_photo = Photo
messages-admin_broadcast_started = <blockquote><tg-emoji emoji-id="5382080345329934499">⏳</tg-emoji> Broadcast started. The result will appear when delivery finishes.</blockquote>
messages-admin_broadcast_done =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Broadcast completed</b></blockquote>

    Total: <b>{ $total }</b>
    Delivered: <b>{ $sent }</b>
    Blocked bot: <b>{ $blocked }</b>
    Errors: <b>{ $failed }</b>

messages-admin_broadcast_close_button = Close

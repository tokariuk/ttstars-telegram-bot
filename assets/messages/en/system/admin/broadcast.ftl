messages-admin_broadcast_content_prompt =
    <blockquote><b>📣 Broadcast</b></blockquote>

    Send broadcast content:
    • text with HTML formatting and premium emojis
    • or photo with caption

messages-admin_broadcast_content_invalid = <blockquote>❌ Send a text message or a photo with caption.</blockquote>

messages-admin_broadcast_options_prompt =
    Configure recipients and close button.

    Available locales: <code>{ $locales }</code>
    Selected locales: <b>{ $selected_locales }</b>
    Close button: <b>{ $close_button }</b>

    Format:
    <code>all</code>
    <code>en,uk close</code>
    <code>ru no_close</code>

    Or tap “Skip” to use defaults (all + without close button).

messages-admin_broadcast_options_invalid = <blockquote>❌ Invalid broadcast options: { $error }</blockquote>
messages-admin_broadcast_option_enabled = enabled
messages-admin_broadcast_option_disabled = disabled

messages-admin_broadcast_buttons_prompt =
    Send link buttons (one per line):
    <code>Text | https://example.com</code>

    Or tap “Skip”.

messages-admin_broadcast_buttons_invalid = <blockquote>❌ Invalid buttons: { $error }</blockquote>

messages-admin_broadcast_preview_ready =
    <blockquote>✅ Broadcast preview is ready.</blockquote>

    Recipients: <b>{ $recipients }</b>
    Locales: <b>{ $locales }</b>
    Close button: <b>{ $close_button }</b>
    Buttons: <b>{ $buttons }</b>

messages-admin_broadcast_preview_failed = <blockquote>❌ Failed to build preview. Check message formatting.</blockquote>
messages-admin_broadcast_started = <blockquote>⏳ Broadcast started, please wait...</blockquote>
messages-admin_broadcast_done =
    <blockquote>✅ Broadcast completed</blockquote>

    Total: <b>{ $total }</b>
    Delivered: <b>{ $sent }</b>
    Blocked bot: <b>{ $blocked }</b>
    Errors: <b>{ $failed }</b>

messages-admin_broadcast_close_button = Close

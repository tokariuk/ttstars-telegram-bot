messages-admin_broadcast_content_prompt =
    <blockquote><b>📣 Рассылка</b></blockquote>

    Отправь контент рассылки:
    • текст с HTML-форматированием и премиум-эмодзи
    • или фото с подписью

messages-admin_broadcast_content_invalid = <blockquote>❌ Отправь текст или фото с подписью.</blockquote>

messages-admin_broadcast_options_prompt =
    Настрой получателей и кнопку закрытия.

    Доступные локали: <code>{ $locales }</code>
    Выбранные локали: <b>{ $selected_locales }</b>
    Кнопка «Закрыть»: <b>{ $close_button }</b>

    Формат:
    <code>all</code>
    <code>ru,uk close</code>
    <code>en no_close</code>

    Или нажми «Пропустить» для значений по умолчанию (all + без кнопки).

messages-admin_broadcast_options_invalid = <blockquote>❌ Некорректные параметры рассылки: { $error }</blockquote>
messages-admin_broadcast_option_enabled = включено
messages-admin_broadcast_option_disabled = выключено

messages-admin_broadcast_buttons_prompt =
    Отправь кнопки со ссылками (по одной в строке):
    <code>Текст | https://example.com</code>

    Или нажми «Пропустить».

messages-admin_broadcast_buttons_invalid = <blockquote>❌ Некорректные кнопки: { $error }</blockquote>

messages-admin_broadcast_preview_ready =
    <blockquote>✅ Превью рассылки сформировано.</blockquote>

    Получатели: <b>{ $recipients }</b>
    Локали: <b>{ $locales }</b>
    Кнопка «Закрыть»: <b>{ $close_button }</b>
    Кнопок: <b>{ $buttons }</b>

messages-admin_broadcast_preview_failed = <blockquote>❌ Не удалось собрать превью. Проверь форматирование.</blockquote>
messages-admin_broadcast_started = <blockquote>⏳ Рассылка запущена, подожди...</blockquote>
messages-admin_broadcast_done =
    <blockquote>✅ Рассылка завершена</blockquote>

    Всего: <b>{ $total }</b>
    Доставлено: <b>{ $sent }</b>
    Заблокировали бота: <b>{ $blocked }</b>
    Ошибок: <b>{ $failed }</b>

messages-admin_broadcast_close_button = Закрыть

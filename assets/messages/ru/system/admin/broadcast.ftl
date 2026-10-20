messages-admin_broadcast_content_prompt =
    <blockquote><b><tg-emoji emoji-id="5381969161511543757">🔔</tg-emoji> Рассылка · Шаг 1/4</b></blockquote>

    Отправь контент рассылки:
    • текст с HTML-форматированием и премиум-эмодзи
    • или фото с подписью

messages-admin_broadcast_content_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Отправь текст или фото с подписью.</blockquote>

messages-admin_broadcast_options_prompt =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Рассылка · Шаг 2/4</b></blockquote>

    Настрой получателей и кнопку закрытия.

    Доступные локали: <code>{ $locales }</code>
    Выбранные локали: <b>{ $selected_locales }</b>
    Кнопка «Закрыть»: <b>{ $close_button }</b>
    Предпросмотр ссылки: <b>{ $link_preview }</b>

    Формат:
    <code>all</code>
    <code>ru,uk close</code>
    <code>en no_close</code>

    Или нажми «Пропустить» для значений по умолчанию (all + без кнопки).

messages-admin_broadcast_options_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некорректные параметры рассылки: { $error }</blockquote>
messages-admin_broadcast_option_enabled = включено
messages-admin_broadcast_option_disabled = выключено
messages-admin_broadcast_link_preview_disable = Убрать предпросмотр ссылки
messages-admin_broadcast_link_preview_enable = Показывать предпросмотр ссылки

messages-admin_broadcast_buttons_prompt =
    <blockquote><b><tg-emoji emoji-id="5382283505872967732">🔗</tg-emoji> Рассылка · Шаг 3/4</b></blockquote>

    Отправь кнопки со ссылками (по одной в строке):
    <code>Текст | https://example.com</code>

    Или нажми «Пропустить».

messages-admin_broadcast_buttons_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некорректные кнопки: { $error }</blockquote>

messages-admin_broadcast_preview_ready =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Рассылка · Шаг 4/4</b></blockquote>

    Получатели: <b>{ $recipients }</b>
    Локали: <b>{ $locales }</b>
    Кнопка «Закрыть»: <b>{ $close_button }</b>
    Предпросмотр ссылки: <b>{ $link_preview }</b>
    Кнопок: <b>{ $buttons }</b>

messages-admin_broadcast_preview_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не удалось собрать превью. Проверь форматирование.</blockquote>
messages-admin_broadcast_preview_failed_detail =
    <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Рассылка не запущена</blockquote>

    Telegram отклонил тестовое сообщение: <code>{ $reason }</code>
    Исправь содержимое или кнопки и попробуй снова.
messages-admin_broadcast_preview_content = Содержимое
messages-admin_broadcast_preview_buttons = Кнопки
messages-admin_broadcast_preview_photo = Фото
messages-admin_broadcast_started = <blockquote><tg-emoji emoji-id="5382080345329934499">⏳</tg-emoji> Рассылка запущена. Результат появится после завершения.</blockquote>
messages-admin_broadcast_done =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Рассылка завершена</b></blockquote>

    Всего: <b>{ $total }</b>
    Доставлено: <b>{ $sent }</b>
    Заблокировали бота: <b>{ $blocked }</b>
    Ошибок: <b>{ $failed }</b>

messages-admin_broadcast_close_button = Закрыть

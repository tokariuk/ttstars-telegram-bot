messages-admin_broadcast_content_prompt =
    <blockquote><b><tg-emoji emoji-id="5381969161511543757">🔔</tg-emoji> Розсилка · Крок 1/4</b></blockquote>

    Надішли контент розсилки:
    • текст із HTML-форматуванням та преміум-емодзі
    • або фото з підписом

messages-admin_broadcast_content_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Надішли текст або фото з підписом.</blockquote>

messages-admin_broadcast_options_prompt =
    <blockquote><b><tg-emoji emoji-id="5382107098681220386">👥</tg-emoji> Розсилка · Крок 2/4</b></blockquote>

    Налаштуй одержувачів і кнопку закриття.

    Доступні локалі: <code>{ $locales }</code>
    Обрані локалі: <b>{ $selected_locales }</b>
    Кнопка «Закрити»: <b>{ $close_button }</b>

    Формат:
    <code>all</code>
    <code>uk,ru close</code>
    <code>en no_close</code>

    Або натисни «Пропустити» для значень за замовчуванням (all + без кнопки).

messages-admin_broadcast_options_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некоректні параметри розсилки: { $error }</blockquote>
messages-admin_broadcast_option_enabled = увімкнено
messages-admin_broadcast_option_disabled = вимкнено

messages-admin_broadcast_buttons_prompt =
    <blockquote><b><tg-emoji emoji-id="5382283505872967732">🔗</tg-emoji> Розсилка · Крок 3/4</b></blockquote>

    Надішли кнопки з посиланнями (по одній у рядок):
    <code>Текст | https://example.com</code>

    Або натисни «Пропустити».

messages-admin_broadcast_buttons_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некоректні кнопки: { $error }</blockquote>

messages-admin_broadcast_preview_ready =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Розсилка · Крок 4/4</b></blockquote>

    Одержувачі: <b>{ $recipients }</b>
    Локалі: <b>{ $locales }</b>
    Кнопка «Закрити»: <b>{ $close_button }</b>
    Кнопок: <b>{ $buttons }</b>

messages-admin_broadcast_preview_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не вдалося створити превʼю. Перевір форматування.</blockquote>
messages-admin_broadcast_preview_content = Вміст
messages-admin_broadcast_preview_buttons = Кнопки
messages-admin_broadcast_preview_photo = Фото
messages-admin_broadcast_started = <blockquote><tg-emoji emoji-id="5382080345329934499">⏳</tg-emoji> Розсилку запущено. Результат зʼявиться після завершення.</blockquote>
messages-admin_broadcast_done =
    <blockquote><b><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Розсилку завершено</b></blockquote>

    Всього: <b>{ $total }</b>
    Доставлено: <b>{ $sent }</b>
    Заблокували бота: <b>{ $blocked }</b>
    Помилок: <b>{ $failed }</b>

messages-admin_broadcast_close_button = Закрити

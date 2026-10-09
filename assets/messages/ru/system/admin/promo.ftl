messages-admin_promo_menu =
    <blockquote><b><tg-emoji emoji-id="5380101288824450052">🔑</tg-emoji> Промокоды</b></blockquote>

    Активных кодов: <b>{ $active_codes }</b> из <b>{ $total_codes }</b>
    Нажми на промокод ниже для поштучного управления.

messages-admin_promo_list_empty = Промокодов пока нет. Создай первый код кнопкой ниже.
messages-admin_promo_item = • <code>{ $code }</code> — <b>{ $amount } USD</b> · { $activations }/{ $max_activations }
messages-admin_promo_item_button = { $code } · { $amount } USD · { $activations }/{ $max_activations }
messages-admin_promo_page_indicator = { $current }/{ $total }
messages-admin_promo_bulk_mode_hint = Режим массового удаления активен. Выбрано: <b>{ $selected }</b>
messages-admin_promo_details =
    <blockquote><b><tg-emoji emoji-id="5380101288824450052">🔑</tg-emoji> Промокод <code>{ $code }</code></b></blockquote>

    • Номинал: <b>{ $amount } USD</b>
    • Активации: <b>{ $activations }/{ $max_activations }</b>
    • Статус: <b>{ $status }</b>
    • Создан: { $created_at }
    • Активировали:
    { $activated_users }

messages-admin_promo_status_active = активен
messages-admin_promo_status_exhausted = исчерпан
messages-admin_promo_status_disabled = выключен
messages-admin_promo_toggle_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Промокод <code>{ $code }</code> теперь <b>{ $status }</b>.</blockquote>
messages-admin_limit_unlimited = ∞

messages-admin_promo_create_prompt =
    <blockquote><b><tg-emoji emoji-id="5379761711530163623">➕</tg-emoji> Новый промокод</b></blockquote>

    Формат:
    <code>CODE 5</code>
    или
    <code>CODE 5 100</code>

    Третье число — лимит активаций, <code>0</code> = без лимита.

messages-admin_promo_create_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некорректный формат. Пример: <code>WELCOME5 5 100</code>.</blockquote>
messages-admin_promo_create_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не удалось создать промокод: { $error }</blockquote>
messages-admin_promo_created = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Создан <code>{ $code }</code> на <b>{ $amount } USD</b>, лимит: <b>{ $max_activations }</b>.</blockquote>

messages-admin_promo_quick_prompt =
    <blockquote><b><tg-emoji emoji-id="5380078671526666610">⚡</tg-emoji> Быстрый одноразовый код</b></blockquote>

    Формат:
    <code>5</code>
    или
    <code>5 BONUS</code>

    Где:
    • 5 — сумма в USD
    • BONUS — префикс (опционально)

messages-admin_promo_quick_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некорректный формат. Пример: <code>5 BONUS</code>.</blockquote>
messages-admin_promo_quick_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не удалось создать код: { $error }</blockquote>
messages-admin_promo_quick_done =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Создан одноразовый код <code>{ $code }</code> на <b>{ $amount } USD</b>.</blockquote>

messages-admin_promo_bulk_prompt =
    <blockquote><b><tg-emoji emoji-id="5379646374478392537">📦</tg-emoji> Пачка промокодов</b></blockquote>

    Формат:
    <code>5 20 BONUS</code>

    Где:
    • 5 — сумма в USD
    • 20 — количество уникальных одноразовых кодов
    • BONUS — префикс (опционально)

messages-admin_promo_bulk_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некорректный формат. Пример: <code>5 20 BONUS</code>.</blockquote>
messages-admin_promo_bulk_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не удалось создать коды: { $error }</blockquote>
messages-admin_promo_bulk_done =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Создано { $count } одноразовых кодов по <b>{ $amount } USD</b>.</blockquote>

    <code>{ $codes }</code>
messages-admin_promo_bulk_item_selected = Код { $code } добавлен в выбор.
messages-admin_promo_bulk_item_unselected = Код { $code } убран из выбора.
messages-admin_promo_bulk_delete_empty = Не выбрано ни одного кода для удаления.
messages-admin_promo_bulk_delete_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Удалено выбранных кодов: <b>{ $count }</b>.</blockquote>

messages-admin_promo_set_limit_prompt =
    <blockquote><b><tg-emoji emoji-id="5382118858301676590">⚙️</tg-emoji> Лимит активаций</b></blockquote>

    Укажи новый лимит для <code>{ $code }</code>:
    • число: <code>1</code>, <code>10</code>, <code>0</code> (безлимит)
    • или полный формат: <code>CODE 10</code>

messages-admin_promo_set_limit_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некорректный формат. Пример: <code>10</code> или <code>WELCOME5 10</code>.</blockquote>
messages-admin_promo_set_limit_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не удалось обновить лимит: { $error }</blockquote>
messages-admin_promo_set_limit_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Лимит <code>{ $code }</code> обновлён: <b>{ $max_activations }</b>.</blockquote>

messages-admin_promo_delete_prompt = Отправь код для удаления, например: <code>WELCOME5</code>
messages-admin_promo_delete_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Укажи промокод одной строкой.</blockquote>
messages-admin_promo_deleted = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Промокод <code>{ $code }</code> удалён.</blockquote>
messages-admin_promo_not_found = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Промокод не найден.</blockquote>
messages-admin_promo_cleanup_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Удалено использованных промокодов: <b>{ $count }</b>.</blockquote>

messages-admin_promo_menu =
    <blockquote><b><tg-emoji emoji-id="5380101288824450052">🔑</tg-emoji> Промокоди</b></blockquote>

    Активних кодів: <b>{ $active_codes }</b> із <b>{ $total_codes }</b>
    Натисни на промокод нижче для поштучного керування.

messages-admin_promo_list_empty = Промокодів поки немає. Створи перший код кнопкою нижче.
messages-admin_promo_item = • <code>{ $code }</code> — <b>{ $amount } USD</b> · { $activations }/{ $max_activations }
messages-admin_promo_item_button = { $code } · { $amount } USD · { $activations }/{ $max_activations }
messages-admin_promo_page_indicator = { $current }/{ $total }
messages-admin_promo_bulk_mode_hint = Режим масового видалення активний. Вибрано: <b>{ $selected }</b>
messages-admin_promo_details =
    <blockquote><b><tg-emoji emoji-id="5380101288824450052">🔑</tg-emoji> Промокод <code>{ $code }</code></b></blockquote>

    • Номінал: <b>{ $amount } USD</b>
    • Активації: <b>{ $activations }/{ $max_activations }</b>
    • Статус: <b>{ $status }</b>
    • Створено: { $created_at }
    • Активували:
    { $activated_users }

messages-admin_promo_status_active = активний
messages-admin_promo_status_exhausted = вичерпано
messages-admin_promo_status_disabled = вимкнено
messages-admin_promo_toggle_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Промокод <code>{ $code }</code> тепер <b>{ $status }</b>.</blockquote>
messages-admin_limit_unlimited = ∞

messages-admin_promo_create_prompt =
    <blockquote><b><tg-emoji emoji-id="5379761711530163623">➕</tg-emoji> Новий промокод</b></blockquote>

    Формат:
    <code>CODE 5</code>
    або
    <code>CODE 5 100</code>

    Де 3-тє число — ліміт активацій, <code>0</code> = безліміт.

messages-admin_promo_create_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некоректний формат. Приклад: <code>WELCOME5 5 100</code>.</blockquote>
messages-admin_promo_create_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не вдалося створити промокод: { $error }</blockquote>
messages-admin_promo_created = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Створено <code>{ $code }</code> на <b>{ $amount } USD</b>, ліміт: <b>{ $max_activations }</b>.</blockquote>

messages-admin_promo_quick_prompt =
    <blockquote><b><tg-emoji emoji-id="5380078671526666610">⚡</tg-emoji> Швидкий одноразовий код</b></blockquote>

    Формат:
    <code>5</code>
    або
    <code>5 BONUS</code>

    Де:
    • 5 — сума в USD
    • BONUS — префікс (опційно)

messages-admin_promo_quick_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некоректний формат. Приклад: <code>5 BONUS</code>.</blockquote>
messages-admin_promo_quick_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не вдалося створити код: { $error }</blockquote>
messages-admin_promo_quick_done =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Створено одноразовий код <code>{ $code }</code> на <b>{ $amount } USD</b>.</blockquote>

messages-admin_promo_bulk_prompt =
    <blockquote><b><tg-emoji emoji-id="5379646374478392537">📦</tg-emoji> Пачка промокодів</b></blockquote>

    Формат:
    <code>5 20 BONUS</code>

    Де:
    • 5 — сума в USD
    • 20 — кількість унікальних одноразових кодів
    • BONUS — префікс (опційно)

messages-admin_promo_bulk_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некоректний формат. Приклад: <code>5 20 BONUS</code>.</blockquote>
messages-admin_promo_bulk_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не вдалося створити коди: { $error }</blockquote>
messages-admin_promo_bulk_done =
    <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Створено { $count } одноразових кодів по <b>{ $amount } USD</b>.</blockquote>

    <code>{ $codes }</code>
messages-admin_promo_bulk_item_selected = Код { $code } додано у вибір.
messages-admin_promo_bulk_item_unselected = Код { $code } прибрано з вибору.
messages-admin_promo_bulk_delete_empty = Не обрано жодного коду для видалення.
messages-admin_promo_bulk_delete_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Видалено вибраних кодів: <b>{ $count }</b>.</blockquote>

messages-admin_promo_set_limit_prompt =
    <blockquote><b><tg-emoji emoji-id="5382118858301676590">⚙️</tg-emoji> Ліміт активацій</b></blockquote>

    Вкажи новий ліміт для <code>{ $code }</code>:
    • число: <code>1</code>, <code>10</code>, <code>0</code> (безліміт)
    • або формат: <code>CODE 10</code>

messages-admin_promo_set_limit_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Некоректний формат. Приклад: <code>10</code> або <code>WELCOME5 10</code>.</blockquote>
messages-admin_promo_set_limit_failed = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Не вдалося оновити ліміт: { $error }</blockquote>
messages-admin_promo_set_limit_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Ліміт <code>{ $code }</code> оновлено: <b>{ $max_activations }</b>.</blockquote>

messages-admin_promo_delete_prompt = Надішли код для видалення, наприклад: <code>WELCOME5</code>
messages-admin_promo_delete_invalid = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Вкажи промокод одним рядком.</blockquote>
messages-admin_promo_deleted = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Промокод <code>{ $code }</code> видалено.</blockquote>
messages-admin_promo_not_found = <blockquote><tg-emoji emoji-id="5381932538325404900">❌</tg-emoji> Промокод не знайдено.</blockquote>
messages-admin_promo_cleanup_done = <blockquote><tg-emoji emoji-id="5382230286933205157">✅</tg-emoji> Видалено використаних промокодів: <b>{ $count }</b>.</blockquote>

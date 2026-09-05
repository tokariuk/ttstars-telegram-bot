messages-gifts_recipient_screen =
    <blockquote><b><tg-emoji emoji-id="5379759198974289129">🎁</tg-emoji> Покупка Telegram подарка · Шаг 1/5</b></blockquote>

    Укажи username аккаунта, на который нужно отправить подарок.

    <b>Формат:</b> <code>@username</code>
    <b>Текущий получатель:</b> <code>{ $recipient }</code>

messages-gifts_catalog_screen =
    <blockquote><b><tg-emoji emoji-id="5379759198974289129">🎁</tg-emoji> Покупка Telegram подарка · Шаг 2/5</b></blockquote>

    Выбери подарок из списка ниже.

    <b>Получатель:</b> <code>{ $recipient }</code>
    <b>Выбрано:</b> <code>{ $selected }</code>

messages-gifts_message_screen =
    <blockquote><b><tg-emoji emoji-id="5379759198974289129">🎁</tg-emoji> Покупка Telegram подарка · Шаг 3/5</b></blockquote>

    Введи подпись к подарку или пропусти шаг.

    <b>Получатель:</b> <code>{ $recipient }</code>
    <b>Подарок:</b> <code>{ $gift }</code>
    <b>Сумма:</b> <code>{ $amount } USD</code>
    <b>Текущая подпись:</b> <code>{ $current_message }</code>

messages-gifts_sender_privacy_screen =
    <blockquote><b><tg-emoji emoji-id="5379759198974289129">🎁</tg-emoji> Покупка Telegram подарка · Шаг 4/5</b></blockquote>

    Выбери, показывать ли отправителя подарка.

    <b>Важно:</b> отправитель в этом сценарии — <b>сервисный аккаунт TTStars</b>, а не ты.

    <b>Получатель:</b> <code>{ $recipient }</code>
    <b>Подарок:</b> <code>{ $gift }</code>
    <b>Сумма:</b> <code>{ $amount } USD</code>
    <b>Подпись:</b> <code>{ $message }</code>

messages-gifts_payment_screen =
    <blockquote><b><tg-emoji emoji-id="5379759198974289129">🎁</tg-emoji> Покупка Telegram подарка · Шаг 5/5</b></blockquote>

    Проверь данные перед оплатой.

    <b>Получатель:</b> <code>{ $recipient }</code>
    <b>Подарок:</b> <code>{ $gift }</code>
    <b>Сумма:</b> <code>{ $amount } USD</code>
    <b>Подпись:</b> <code>{ $message }</code>
    <b>Видимость отправителя:</b> <code>{ $sender_visibility }</code>

    <b>Баланс:</b> <code>{ $balance } USD</code>

messages-gift_sender_visible_option = Отправитель (сервис TTStars) будет виден
messages-gift_sender_private_option = Отправитель (сервис TTStars) будет скрыт

messages-gift_name_new_year_tree = Новогодняя елка
messages-gift_name_valentine_heart = Валентинка
messages-gift_name_new_year_bear = Новогодний медведь
messages-gift_name_bear_with_heart = Медведь с сердцем
messages-gift_name_bear_with_bouquet = Медведь с букетом
messages-gift_name_irish_bear = Ирландский медведь
messages-gift_name_clown_bear = Медведь-клоун
messages-gift_name_easter_bear = Пасхальный медведь
messages-gift_name_worker_bear = Медведь-рабочий
messages-gift_name_military_bear = Военный мишка
messages-gift_name_football_bear = Футбольный мишка
messages-gift_name_default_bear = Медведь

messages-gift_recipient_invalid =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Некорректный username получателя. Используй формат <code>@username</code>.</blockquote>

messages-gift_recipient_missing =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Получатель подарка ещё не задан.</blockquote>

messages-gift_invalid =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Подарок не выбран или недоступен.</blockquote>

messages-gift_message_too_long =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Подпись слишком длинная. Максимум: <b>{ $max_chars }</b> символов.</blockquote>

messages-gift_sender_visibility_required =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Выбери видимость отправителя перед оплатой.</blockquote>

messages-gift_userbot_session_required =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Не удалось проверить username получателя. Попробуй позже.</blockquote>

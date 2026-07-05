messages-history_list_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> История операций</b></blockquote>

    Выбери операцию кнопками ниже.

messages-history_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> История операций</b></blockquote>

    Операций ещё нет.

messages-history_operation_button = #{ $order_id } · { $product } · { $amount } USD

messages-history_page_indicator = { $current }/{ $total }

messages-history_product_stars_button = Stars { $stars }

messages-history_product_premium_button = Premium { $months } мес.

messages-history_product_gift_button = Подарок

messages-history_product_topup_button = Пополнение

messages-history_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> Операция #{ $order_id }</b></blockquote>

    <b>Статус:</b> { $status }
    <b>Продукт:</b> { $product }
    <b>Провайдер:</b> { $provider }
    <b>Получатель:</b> { $recipient }
    <b>Сумма:</b> <code>{ $amount } USD</code>

    <blockquote expandable><b>Технические детали</b>
    <b>Создано:</b> { $created }
    <b>Оплачено:</b> { $paid }
    <b>Выполнено:</b> { $fulfilled }

    <b>Provider ref:</b> <code>{ $provider_ref }</code>
    <b>TX:</b> <tg-spoiler><code>{ $tx_hash }</code></tg-spoiler></blockquote>

messages-history_detail_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Операция не найдена или недоступна.</blockquote>

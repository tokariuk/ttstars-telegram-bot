messages-history_list_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> Історія операцій</b></blockquote>

    Обери операцію кнопками нижче.

messages-history_list_empty_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> Історія операцій</b></blockquote>

    Операцій ще немає. Почни з купівлі Stars, Premium або поповнення балансу в головному меню.

messages-history_operation_button = #{ $order_id } · { $product } · { $amount } USD

messages-history_page_indicator = { $current }/{ $total }

messages-history_product_stars_button = Stars { $stars }

messages-history_product_premium_button = Premium { $months } міс.

messages-history_product_gift_button = Подарунок

messages-history_product_topup_button = Поповнення

messages-history_detail_screen =
    <blockquote><b><tg-emoji emoji-id="5382065781095830261">📃</tg-emoji> Операція #{ $order_id }</b></blockquote>

    <b>Статус:</b> { $status }
    <b>Продукт:</b> { $product }
    <b>Провайдер:</b> { $provider }
    <b>Отримувач:</b> { $recipient }
    <b>Сума:</b> <code>{ $amount } USD</code>

    <blockquote expandable><b>Технічні деталі</b>
    <b>Створено:</b> { $created }
    <b>Оплачено:</b> { $paid }
    <b>Виконано:</b> { $fulfilled }

    <b>ID у провайдера:</b> { $provider_ref }
    <b>TX:</b> { $tx_hash }</blockquote>

messages-history_detail_not_found =
    <blockquote><tg-emoji emoji-id="5381889309479574958">⚠️</tg-emoji> Операцію не знайдено або вона недоступна.</blockquote>

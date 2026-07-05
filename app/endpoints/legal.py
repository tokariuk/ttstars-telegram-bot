from __future__ import annotations

# ruff: noqa: E501
from dataclasses import dataclass
from html import escape
from typing import Final, Literal, cast

from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse

from app.utils.localization import normalize_i18n_locale

Locale = Literal["uk", "ru", "en"]


@dataclass(frozen=True)
class LegalSection:
    heading: str
    paragraphs: tuple[str, ...] = ()
    bullets: tuple[str, ...] = ()


@dataclass(frozen=True)
class LegalDoc:
    app_name: str
    title: str
    subtitle: str
    effective_date: str
    updated_date: str
    intro: tuple[str, ...]
    sections: tuple[LegalSection, ...]
    contact_line: str
    switch_link_title: str


def _normalize_lang(raw_lang: str) -> Locale:
    normalized = normalize_i18n_locale(raw_lang, fallback="ru")
    if normalized in {"uk", "ru", "en"}:
        return cast(Locale, normalized)
    return "ru"


def _css() -> str:
    return """
    :root {
      --bg: #0f172a;
      --fg: #e2e8f0;
      --muted: #94a3b8;
      --card: #111827;
      --border: #1f2937;
      --accent: #38bdf8;
      --link: #7dd3fc;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--fg);
      line-height: 1.55;
    }
    .container {
      width: 100%;
      max-width: 920px;
      margin: 0 auto;
      padding: 18px 14px 28px;
    }
    .header {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 14px;
    }
    .brand {
      font-size: 12px;
      letter-spacing: 0;
      text-transform: uppercase;
      color: var(--muted);
      margin: 0 0 6px;
    }
    h1 {
      margin: 0 0 8px;
      font-size: 24px;
      line-height: 1.25;
    }
    .subtitle {
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }
    .meta {
      margin-top: 10px;
      font-size: 12px;
      color: var(--muted);
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }
    .section {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px 16px;
      margin-bottom: 12px;
    }
    h2 {
      margin: 0 0 8px;
      font-size: 18px;
      line-height: 1.35;
    }
    p {
      margin: 0 0 10px;
      color: var(--fg);
      font-size: 14px;
    }
    p:last-child { margin-bottom: 0; }
    ul {
      margin: 0 0 0 18px;
      padding: 0;
    }
    li {
      margin-bottom: 6px;
      color: var(--fg);
      font-size: 14px;
    }
    li:last-child { margin-bottom: 0; }
    .switch {
      margin-top: 6px;
      font-size: 14px;
      color: var(--muted);
    }
    a {
      color: var(--link);
      text-decoration: none;
    }
    a:hover { text-decoration: underline; }
    .footer {
      color: var(--muted);
      font-size: 13px;
      margin-top: 2px;
    }
    """


def _telegram_theme_script() -> str:
    return """
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script>
      (function () {
        const tg = window.Telegram && window.Telegram.WebApp;
        if (!tg) return;
        tg.ready();
        tg.expand();
        const params = tg.themeParams || {};
        const root = document.documentElement;
        if (params.bg_color) root.style.setProperty("--bg", params.bg_color);
        if (params.text_color) root.style.setProperty("--fg", params.text_color);
        if (params.hint_color) root.style.setProperty("--muted", params.hint_color);
        if (params.secondary_bg_color) root.style.setProperty("--card", params.secondary_bg_color);
        if (params.link_color) root.style.setProperty("--link", params.link_color);
      })();
    </script>
    """


def _render_doc(
    *,
    locale: Locale,
    doc: LegalDoc,
    switch_href: str,
) -> HTMLResponse:
    intro_html = "".join(f"<p>{escape(paragraph)}</p>" for paragraph in doc.intro)
    sections_html_parts: list[str] = []
    for section in doc.sections:
        paragraphs_html = "".join(f"<p>{escape(paragraph)}</p>" for paragraph in section.paragraphs)
        bullets_html = ""
        if section.bullets:
            bullets_items = "".join(f"<li>{escape(item)}</li>" for item in section.bullets)
            bullets_html = f"<ul>{bullets_items}</ul>"
        sections_html_parts.append(
            "<section class='section'>"
            f"<h2>{escape(section.heading)}</h2>"
            f"{paragraphs_html}{bullets_html}"
            "</section>"
        )

    switch_link = (
        "<p class='switch'>"
        f"{escape(doc.switch_link_title)} "
        f"<a href='{escape(switch_href, quote=True)}'>{escape(switch_href)}</a>"
        "</p>"
    )

    html = f"""<!doctype html>
<html lang="{escape(locale)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
  <title>{escape(doc.title)} - {escape(doc.app_name)}</title>
  <style>{_css()}</style>
</head>
<body>
  <main class="container">
    <header class="header">
      <p class="brand">{escape(doc.app_name)}</p>
      <h1>{escape(doc.title)}</h1>
      <p class="subtitle">{escape(doc.subtitle)}</p>
      <div class="meta">
        <span>{escape(doc.effective_date)}</span>
        <span>{escape(doc.updated_date)}</span>
      </div>
      {intro_html}
      {switch_link}
    </header>
    {''.join(sections_html_parts)}
    <p class="footer">{escape(doc.contact_line)}</p>
  </main>
  {_telegram_theme_script()}
</body>
</html>
"""
    return HTMLResponse(content=html)


PRIVACY_DOCS: Final[dict[Locale, LegalDoc]] = {
    "ru": LegalDoc(
        app_name="TTStars Bot",
        title="Политика конфиденциальности",
        subtitle="Документ регулирует обработку данных при использовании TTStars.",
        effective_date="Вступает в силу: 25 апреля 2026",
        updated_date="Обновлено: 25 апреля 2026",
        intro=(
            "Используя TTStars Bot и Mini App, вы соглашаетесь с этой Политикой.",
            "Если вы не согласны с условиями, прекратите использование сервиса.",
        ),
        sections=(
            LegalSection(
                heading="1. Какие данные мы получаем",
                bullets=(
                    "Telegram-данные профиля: user_id, username, имя, язык интерфейса.",
                    "Данные заказов: тип продукта, количество Stars/период Premium, статус заказа, сумма.",
                    "Технические данные платежей: идентификаторы платежа у провайдеров, служебные статусы, ссылки на оплату.",
                    "Данные реферальной программы и промокодов при их использовании.",
                    "Сообщения и обращения в поддержку, которые вы отправляете сами.",
                ),
            ),
            LegalSection(
                heading="2. Для чего используется информация",
                bullets=(
                    "Создание, оплата и выполнение заказов.",
                    "Проверка статусов платежей, предотвращение мошенничества и ошибок.",
                    "Начисление баланса, бонусов и реферальных вознаграждений.",
                    "Ответы в поддержке и решение спорных ситуаций.",
                    "Улучшение стабильности и безопасности сервиса.",
                ),
            ),
            LegalSection(
                heading="3. Платежи и третьи стороны",
                paragraphs=(
                    "Платежи обрабатываются соответствующими платежными провайдерами. Мы не храним данные банковских карт.",
                    "Мы передаем провайдерам только данные, необходимые для создания и сопровождения платежа.",
                ),
            ),
            LegalSection(
                heading="4. Срок хранения данных",
                bullets=(
                    "Данные аккаунта и заказов хранятся, пока это необходимо для работы сервиса, отчетности и безопасности.",
                    "Логи и технические события могут храниться ограниченный срок для диагностики и антифрода.",
                    "Часть данных может храниться дольше, если это требуется законом или для урегулирования споров.",
                ),
            ),
            LegalSection(
                heading="5. Защита данных",
                paragraphs=(
                    "Мы применяем организационные и технические меры защиты, включая контроль доступа к административным системам.",
                    "Несмотря на разумные меры безопасности, ни один способ передачи данных в интернете не гарантирует абсолютную защиту.",
                ),
            ),
            LegalSection(
                heading="6. Ваши права",
                paragraphs=(
                    "Вы можете запросить уточнение, обновление или удаление персональных данных, если это не противоречит нашим законным обязательствам.",
                    "По вопросам персональных данных обращайтесь в поддержку бота.",
                ),
            ),
            LegalSection(
                heading="7. Важные уточнения",
                bullets=(
                    "TTStars является независимым сервисом и не аффилирован с Telegram.",
                    "Использование платформы Telegram также регулируется условиями и политиками Telegram.",
                ),
            ),
        ),
        contact_line="Контакт для вопросов по Политике: @TTStars_support",
        switch_link_title="Пользовательское соглашение:",
    ),
    "uk": LegalDoc(
        app_name="TTStars Bot",
        title="Політика конфіденційності",
        subtitle="Документ регулює обробку даних під час використання TTStars.",
        effective_date="Набирає чинності: 25 квітня 2026",
        updated_date="Оновлено: 25 квітня 2026",
        intro=(
            "Використовуючи TTStars Bot і Mini App, ви погоджуєтесь з цією Політикою.",
            "Якщо ви не погоджуєтесь з умовами, припиніть використання сервісу.",
        ),
        sections=(
            LegalSection(
                heading="1. Які дані ми отримуємо",
                bullets=(
                    "Telegram-дані профілю: user_id, username, ім'я, мова інтерфейсу.",
                    "Дані замовлень: тип продукту, кількість Stars/період Premium, статус замовлення, сума.",
                    "Технічні дані платежів: ідентифікатори платежу у провайдерів, службові статуси, посилання на оплату.",
                    "Дані реферальної програми та промокодів під час їх використання.",
                    "Повідомлення й звернення в підтримку, які ви надсилаєте самостійно.",
                ),
            ),
            LegalSection(
                heading="2. Для чого використовується інформація",
                bullets=(
                    "Створення, оплата та виконання замовлень.",
                    "Перевірка статусів платежів, запобігання шахрайству та помилкам.",
                    "Нарахування балансу, бонусів і реферальних винагород.",
                    "Відповіді в підтримці та вирішення спірних ситуацій.",
                    "Покращення стабільності й безпеки сервісу.",
                ),
            ),
            LegalSection(
                heading="3. Платежі та треті сторони",
                paragraphs=(
                    "Платежі обробляються відповідними платіжними провайдерами. Ми не зберігаємо дані банківських карток.",
                    "Ми передаємо провайдерам лише дані, необхідні для створення та супроводу платежу.",
                ),
            ),
            LegalSection(
                heading="4. Строк зберігання даних",
                bullets=(
                    "Дані акаунта й замовлень зберігаються, доки це потрібно для роботи сервісу, звітності та безпеки.",
                    "Логи та технічні події можуть зберігатися обмежений строк для діагностики й антифроду.",
                    "Частина даних може зберігатися довше, якщо цього вимагає закон або вирішення спору.",
                ),
            ),
            LegalSection(
                heading="5. Захист даних",
                paragraphs=(
                    "Ми застосовуємо організаційні та технічні заходи захисту, включно з контролем доступу до адміністративних систем.",
                    "Попри розумні заходи безпеки, жоден спосіб передавання даних в інтернеті не гарантує абсолютний захист.",
                ),
            ),
            LegalSection(
                heading="6. Ваші права",
                paragraphs=(
                    "Ви можете запитати уточнення, оновлення або видалення персональних даних, якщо це не суперечить нашим законним обов'язкам.",
                    "З питань персональних даних звертайтесь у підтримку бота.",
                ),
            ),
            LegalSection(
                heading="7. Важливі уточнення",
                bullets=(
                    "TTStars є незалежним сервісом і не афілійований з Telegram.",
                    "Використання платформи Telegram також регулюється умовами та політиками Telegram.",
                ),
            ),
        ),
        contact_line="Контакт для питань щодо Політики: @TTStars_support",
        switch_link_title="Користувацька угода:",
    ),
    "en": LegalDoc(
        app_name="TTStars Bot",
        title="Privacy Policy",
        subtitle="This document governs data processing when you use TTStars.",
        effective_date="Effective date: April 25, 2026",
        updated_date="Last updated: April 25, 2026",
        intro=(
            "By using TTStars Bot and Mini App, you agree to this Policy.",
            "If you do not agree with these terms, please stop using the service.",
        ),
        sections=(
            LegalSection(
                heading="1. Data we collect",
                bullets=(
                    "Telegram profile data: user_id, username, display name, interface language.",
                    "Order data: product type, Stars amount/Premium period, order status, amount.",
                    "Payment technical data: provider-side payment identifiers, service statuses, checkout links.",
                    "Referral and promo-related data when such features are used.",
                    "Support messages and requests that you submit.",
                ),
            ),
            LegalSection(
                heading="2. Why we use this data",
                bullets=(
                    "To create, process, and fulfill orders.",
                    "To verify payment statuses and prevent fraud or operational errors.",
                    "To apply balance changes, bonuses, and referral rewards.",
                    "To provide support and resolve disputes.",
                    "To improve service reliability and security.",
                ),
            ),
            LegalSection(
                heading="3. Payments and third parties",
                paragraphs=(
                    "Payments are processed by relevant payment providers. We do not store bank card details.",
                    "We share only the minimum data needed to create and maintain a payment.",
                ),
            ),
            LegalSection(
                heading="4. Data retention",
                bullets=(
                    "Account and order data is retained as long as needed for service operation, accounting, and security.",
                    "Logs and technical events may be kept for a limited period for diagnostics and anti-fraud checks.",
                    "Some data may be kept longer where required by law or dispute handling.",
                ),
            ),
            LegalSection(
                heading="5. Security",
                paragraphs=(
                    "We apply organizational and technical safeguards, including restricted administrative access.",
                    "No internet transmission method is absolutely secure, but we maintain reasonable protection standards.",
                ),
            ),
            LegalSection(
                heading="6. Your rights",
                paragraphs=(
                    "You may request correction, update, or deletion of personal data where it does not conflict with our legal obligations.",
                    "For privacy requests, contact bot support.",
                ),
            ),
            LegalSection(
                heading="7. Important notes",
                bullets=(
                    "TTStars is an independent service and is not affiliated with Telegram.",
                    "Your use of Telegram platform is also governed by Telegram terms and policies.",
                ),
            ),
        ),
        contact_line="Privacy contact: @TTStars_support",
        switch_link_title="User Agreement:",
    ),
}


TERMS_DOCS: Final[dict[Locale, LegalDoc]] = {
    "ru": LegalDoc(
        app_name="TTStars Bot",
        title="Пользовательское соглашение",
        subtitle="Правила использования TTStars Bot и связанных Mini App страниц.",
        effective_date="Вступает в силу: 25 апреля 2026",
        updated_date="Обновлено: 25 апреля 2026",
        intro=(
            "Используя сервис, вы подтверждаете, что прочитали и приняли условия этого Соглашения.",
            "Если вы не согласны с условиями, прекратите использование сервиса.",
        ),
        sections=(
            LegalSection(
                heading="1. Предмет сервиса",
                paragraphs=(
                    "TTStars предоставляет инструменты для покупки Telegram Stars, Telegram Premium и пополнения внутреннего баланса.",
                    "Сервис работает через Telegram-бота и подключенные платежные провайдеры.",
                ),
            ),
            LegalSection(
                heading="2. Требования к пользователю",
                bullets=(
                    "Вы обязуетесь предоставлять корректные данные для заказа, включая username получателя.",
                    "Вы несете ответственность за доступ к своему Telegram-аккаунту и его безопасность.",
                    "Вы обязуетесь не использовать сервис для незаконной деятельности.",
                ),
            ),
            LegalSection(
                heading="3. Оплата и выполнение заказа",
                bullets=(
                    "Стоимость и комиссии отображаются перед подтверждением оплаты.",
                    "Заказ считается принятым после фиксации успешной оплаты соответствующим провайдером или внутренним балансом.",
                    "Срок выполнения обычно составляет до нескольких минут, но может быть увеличен из-за внешних ограничений провайдеров и Telegram.",
                ),
            ),
            LegalSection(
                heading="4. Возвраты и спорные ситуации",
                bullets=(
                    "Если оплата не подтверждена, заказ не выполняется.",
                    "Если оплата подтверждена, но выполнение невозможно по техническим причинам, заявка обрабатывается через поддержку.",
                    "Решение о возврате или компенсации принимается по фактическому состоянию платежа и выполнения.",
                ),
            ),
            LegalSection(
                heading="5. Ограничения использования",
                bullets=(
                    "Запрещены попытки обхода защиты, автоматизированного злоупотребления и любых атак на сервис.",
                    "Запрещено использовать сервис для мошенничества, отмывания средств и иных нарушений закона.",
                    "Нарушение правил может привести к блокировке доступа без предварительного уведомления.",
                ),
            ),
            LegalSection(
                heading="6. Ограничение ответственности",
                paragraphs=(
                    "Мы не отвечаем за сбои, задержки или ограничения, вызванные Telegram или сторонними платежными/инфраструктурными сервисами.",
                    "Наша ответственность ограничена объемом фактически оплаченной и неоказанной части услуги, если иное не требуется законом.",
                ),
            ),
            LegalSection(
                heading="7. Изменения условий",
                paragraphs=(
                    "Мы можем обновлять это Соглашение. Актуальная версия публикуется в Mini App.",
                    "Продолжение использования сервиса после обновления означает принятие новой редакции.",
                ),
            ),
        ),
        contact_line="Контакт по вопросам Соглашения: @TTStars_support",
        switch_link_title="Политика конфиденциальности:",
    ),
    "uk": LegalDoc(
        app_name="TTStars Bot",
        title="Користувацька угода",
        subtitle="Правила використання TTStars Bot і пов'язаних Mini App сторінок.",
        effective_date="Набирає чинності: 25 квітня 2026",
        updated_date="Оновлено: 25 квітня 2026",
        intro=(
            "Використовуючи сервіс, ви підтверджуєте, що прочитали та прийняли умови цієї Угоди.",
            "Якщо ви не погоджуєтесь з умовами, припиніть використання сервісу.",
        ),
        sections=(
            LegalSection(
                heading="1. Предмет сервісу",
                paragraphs=(
                    "TTStars надає інструменти для купівлі Telegram Stars, Telegram Premium та поповнення внутрішнього балансу.",
                    "Сервіс працює через Telegram-бота та підключених платіжних провайдерів.",
                ),
            ),
            LegalSection(
                heading="2. Вимоги до користувача",
                bullets=(
                    "Ви зобов'язані надавати коректні дані для замовлення, зокрема username отримувача.",
                    "Ви несете відповідальність за доступ до свого Telegram-акаунта і його безпеку.",
                    "Ви зобов'язані не використовувати сервіс для незаконної діяльності.",
                ),
            ),
            LegalSection(
                heading="3. Оплата та виконання замовлення",
                bullets=(
                    "Вартість і комісії відображаються перед підтвердженням оплати.",
                    "Замовлення вважається прийнятим після фіксації успішної оплати відповідним провайдером або внутрішнім балансом.",
                    "Строк виконання зазвичай становить до кількох хвилин, але може бути збільшений через зовнішні обмеження провайдерів і Telegram.",
                ),
            ),
            LegalSection(
                heading="4. Повернення та спірні ситуації",
                bullets=(
                    "Якщо оплату не підтверджено, замовлення не виконується.",
                    "Якщо оплату підтверджено, але виконання неможливе з технічних причин, заявка обробляється через підтримку.",
                    "Рішення щодо повернення або компенсації приймається за фактичним станом платежу та виконання.",
                ),
            ),
            LegalSection(
                heading="5. Обмеження використання",
                bullets=(
                    "Заборонені спроби обходу захисту, автоматизованого зловживання та будь-які атаки на сервіс.",
                    "Заборонено використовувати сервіс для шахрайства, відмивання коштів та інших порушень закону.",
                    "Порушення правил може призвести до блокування доступу без попереднього повідомлення.",
                ),
            ),
            LegalSection(
                heading="6. Обмеження відповідальності",
                paragraphs=(
                    "Ми не відповідаємо за збої, затримки чи обмеження, спричинені Telegram або сторонніми платіжними/інфраструктурними сервісами.",
                    "Наша відповідальність обмежена обсягом фактично оплаченої та ненаданої частини послуги, якщо інше не вимагає закон.",
                ),
            ),
            LegalSection(
                heading="7. Зміни умов",
                paragraphs=(
                    "Ми можемо оновлювати цю Угоду. Актуальна версія публікується в Mini App.",
                    "Подальше використання сервісу після оновлення означає прийняття нової редакції.",
                ),
            ),
        ),
        contact_line="Контакт щодо питань Угоди: @TTStars_support",
        switch_link_title="Політика конфіденційності:",
    ),
    "en": LegalDoc(
        app_name="TTStars Bot",
        title="User Agreement",
        subtitle="Rules for using TTStars Bot and related Mini App pages.",
        effective_date="Effective date: April 25, 2026",
        updated_date="Last updated: April 25, 2026",
        intro=(
            "By using the service, you confirm that you have read and accepted this Agreement.",
            "If you do not agree with these terms, stop using the service.",
        ),
        sections=(
            LegalSection(
                heading="1. Service scope",
                paragraphs=(
                    "TTStars provides tools to buy Telegram Stars, Telegram Premium, and top up internal balance.",
                    "The service operates via a Telegram bot and connected payment providers.",
                ),
            ),
            LegalSection(
                heading="2. User responsibilities",
                bullets=(
                    "You must provide correct order details, including the recipient username.",
                    "You are responsible for keeping access to your Telegram account secure.",
                    "You must not use the service for unlawful activities.",
                ),
            ),
            LegalSection(
                heading="3. Payment and fulfillment",
                bullets=(
                    "Price and fees are shown before payment confirmation.",
                    "An order is accepted after successful payment is confirmed by the provider or by internal balance debit.",
                    "Fulfillment is usually completed within minutes but may take longer due to external provider or Telegram limitations.",
                ),
            ),
            LegalSection(
                heading="4. Refunds and disputes",
                bullets=(
                    "If payment is not confirmed, the order is not fulfilled.",
                    "If payment is confirmed but fulfillment is technically impossible, the case is handled through support.",
                    "Refund or compensation decisions are based on actual payment and fulfillment state.",
                ),
            ),
            LegalSection(
                heading="5. Prohibited use",
                bullets=(
                    "Attempts to bypass protection, automate abuse, or attack the service are prohibited.",
                    "Fraud, money laundering, or other illegal use is prohibited.",
                    "Rule violations may lead to access restrictions without prior notice.",
                ),
            ),
            LegalSection(
                heading="6. Limitation of liability",
                paragraphs=(
                    "We are not liable for outages, delays, or restrictions caused by Telegram or third-party payment/infrastructure services.",
                    "Our liability is limited to the paid but unprovided part of the service unless otherwise required by law.",
                ),
            ),
            LegalSection(
                heading="7. Changes to terms",
                paragraphs=(
                    "We may update this Agreement. The current version is published in Mini App.",
                    "Continued use after updates means acceptance of the revised terms.",
                ),
            ),
        ),
        contact_line="Agreement contact: @TTStars_support",
        switch_link_title="Privacy Policy:",
    ),
}


router: APIRouter = APIRouter(include_in_schema=False)


@router.get("/miniapp/legal/privacy", response_class=HTMLResponse)
async def miniapp_privacy(
    lang: str = Query(default="ru", min_length=2, max_length=10),
) -> HTMLResponse:
    locale = _normalize_lang(lang)
    switch_href = f"/miniapp/legal/terms?lang={locale}"
    return _render_doc(locale=locale, doc=PRIVACY_DOCS[locale], switch_href=switch_href)


@router.get("/miniapp/legal/terms", response_class=HTMLResponse)
async def miniapp_terms(
    lang: str = Query(default="ru", min_length=2, max_length=10),
) -> HTMLResponse:
    locale = _normalize_lang(lang)
    switch_href = f"/miniapp/legal/privacy?lang={locale}"
    return _render_doc(locale=locale, doc=TERMS_DOCS[locale], switch_href=switch_href)

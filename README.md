# telegram-stars-bot
[![Author](https://img.shields.io/badge/Author-@wakaree-blue)](https://wakaree.dev)
[![Maintainer](https://img.shields.io/badge/Maintainer-@tokariuk-blue)](https://github.com/tokariuk)
[![License](https://img.shields.io/badge/License-MIT-blue)](#license)

Telegram bot for selling Telegram Stars:
- payment methods: `CryptoBot`, `xRocket Pay`, `LZT Market`, `RollyPay (SBP)`, `NicePay (RU/KZ cards)`, `Heleket`
- delivery: automated purchase via Fragment wallet flow (`bohd4nx/FragmentAPI` approach)
- balance: user balance with pay-from-balance flow and auto-refund on delivery failure
- UI: aiogram-dialog flow with `uk`, `ru`, `en` localization

## ⚙️ System dependencies
- Python 3.14+
- Docker
- docker-compose
- make
- uv

## 🐳 Quick Start with Docker compose
- Rename `.env.dist` to `.env` and configure it
- Rename `docker-compose.example.yml` to `docker-compose.yml`
- Run `make app-build` command then `make app-run` to start the bot

Use `make` to see all available commands

## 🔧 Development

### Setup environment
```bash
uv sync
```

### Configure payment and delivery
- Configure public domain for webhooks and checkout links:
  - `SERVER_URL=https://trolololo.icu`
  - `TELEGRAM_USE_WEBHOOK=True`
- Fill `CRYPTO_PAY_*`, `XROCKET_PAY_*`, `LZT_PAY_*`, `ROLLY_PAY_*`, `NICE_PAY_*`, `HELEKET_PAY_*` in `.env`
- For xRocket set:
  - `XROCKET_PAY_BASE_URL=https://pay.xrocket.exchange`
  - `XROCKET_PAY_CURRENCY=USDT` (or any code from `/currencies/available`, e.g. `TONCOIN`, `USDC`, `BTC`)
  - `XROCKET_PAY_WEBHOOK_PATH=/xrocket-pay/webhook` (used as callback URL: `SERVER_URL + XROCKET_PAY_WEBHOOK_PATH`)
- For RollyPay webhooks configure terminal `callback_url` to your bot endpoint:
  - `https://<your-domain>/rolly-pay/webhook`
- Configure fee settings to keep net income positive:
  - `*_FEE_PERCENT` (gateway fee)
  - `*_PAYOUT_FEE_PERCENT` and `*_PAYOUT_FIXED_USD` (withdrawal fee)
- Configure 3-level referral percentages:
  - `PAYMENTS_REFERRAL_LEVEL1_PERCENT`
  - `PAYMENTS_REFERRAL_LEVEL2_PERCENT`
  - `PAYMENTS_REFERRAL_LEVEL3_PERCENT`
- Fill `FRAGMENT_*` in `.env` for stars delivery:
  - authenticated Fragment cookies (`FRAGMENT_COOKIES`)
  - TON wallet credentials (`FRAGMENT_WALLET_API_KEY`, `FRAGMENT_WALLET_MNEMONIC`)
  - wallet version (`FRAGMENT_WALLET_VERSION=V4R2|V5R1`)
  - optional static hash override (`FRAGMENT_HASH`) if auto-hash parsing fails

`FRAGMENT_COOKIES` supports both:
- full cookie header string (`stel_ssid=...; stel_dt=...; stel_token=...; stel_ton_token=...`)
- JSON object string (`{"stel_ssid":"...","stel_dt":"...","stel_token":"...","stel_ton_token":"..."}`)

### Update database tables structure
**Make migration script:**
```bash
make migration message=MESSAGE_WHAT_THE_MIGRATION_DOES
```
**Run migrations:**
```bash
make migrate
```

### Dialog architecture (`aiogram-dialog`)
- Register all dialogs in `app/telegram/dialogs/registry.py`
- Keep shared helpers in `app/telegram/dialogs/common/`
- Keep each flow isolated in `app/telegram/dialogs/flows/<feature>/`:
  - `states.py` (states group)
  - `getters.py` (window data providers)
  - `actions.py` (callbacks and transitions)
  - `windows.py` (window/widget declarations)
  - `dialog.py` (dialog composition)
  - `router.py` (entry points: commands/callbacks)

## 🚀 Used technologies:
- [uv](https://docs.astral.sh/uv/) (an extremely fast Python package and project manager)
- [Aiogram 3.x](https://github.com/aiogram/aiogram) (Telegram bot framework)
- [aiogram-dialog](https://github.com/Tishka17/aiogram_dialog) (dialog manager for Aiogram 3)
- [FastAPI](https://fastapi.tiangolo.com/) (best python web framework for building APIs)
- [PostgreSQL](https://www.postgresql.org/) (persistent relational database)
- [SQLAlchemy](https://docs.sqlalchemy.org/en/20/) (working with database from Python)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/) (lightweight database migration tool)
- [Redis](https://redis.io/docs/) (in-memory database for FSM and caching)
- [Project Fluent](https://projectfluent.org/) (modern localization system)

## 🤝 Contributions

### 🐛 Bug Reports / ✨ Feature Requests

If you want to report a bug or request a new feature, feel free to open a [new issue](https://github.com/tokariuk/aiogram_bot_template/issues/new).

### ⬇️ Pull Requests

If you want to help us improve the bot, you can create a new [Pull Request](https://github.com/tokariuk/aiogram_bot_template/pulls).

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

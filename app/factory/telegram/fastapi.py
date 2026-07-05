from aiogram import Bot, Dispatcher
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.endpoints import healthcheck
from app.endpoints.crypto_pay import create_router as create_crypto_pay_router
from app.endpoints.heleket_pay import create_router as create_heleket_pay_router
from app.endpoints.legal import router as legal_router
from app.endpoints.lzt_pay import create_router as create_lzt_pay_router
from app.endpoints.metrics import router as metrics_router
from app.endpoints.miniapp import register as register_miniapp
from app.endpoints.nice_pay import create_router as create_nice_pay_router
from app.endpoints.platega_pay import create_router as create_platega_pay_router
from app.endpoints.ton_pay import create_router as create_ton_pay_router
from app.endpoints.xrocket_pay import create_router as create_xrocket_pay_router
from app.models.config.env import AppConfig


def setup_fastapi(app: FastAPI, dispatcher: Dispatcher, bot: Bot) -> FastAPI:
    config: AppConfig = dispatcher.workflow_data["config"]
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")
    crypto_pay_webhook_path = config.crypto_pay.webhook_path
    normalized_crypto_path = (
        crypto_pay_webhook_path
        if crypto_pay_webhook_path.startswith("/")
        else f"/{crypto_pay_webhook_path}"
    )
    lzt_pay_webhook_path = config.lzt_pay.webhook_path
    normalized_lzt_path = (
        lzt_pay_webhook_path
        if lzt_pay_webhook_path.startswith("/")
        else f"/{lzt_pay_webhook_path}"
    )
    nice_pay_webhook_path = config.nice_pay.webhook_path
    normalized_nice_path = (
        nice_pay_webhook_path
        if nice_pay_webhook_path.startswith("/")
        else f"/{nice_pay_webhook_path}"
    )
    platega_pay_webhook_path = config.platega_pay.webhook_path
    normalized_platega_path = (
        platega_pay_webhook_path
        if platega_pay_webhook_path.startswith("/")
        else f"/{platega_pay_webhook_path}"
    )
    xrocket_pay_webhook_path = config.xrocket_pay.webhook_path
    normalized_xrocket_path = (
        xrocket_pay_webhook_path
        if xrocket_pay_webhook_path.startswith("/")
        else f"/{xrocket_pay_webhook_path}"
    )
    heleket_pay_webhook_path = config.heleket_pay.webhook_path
    normalized_heleket_path = (
        heleket_pay_webhook_path
        if heleket_pay_webhook_path.startswith("/")
        else f"/{heleket_pay_webhook_path}"
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(config.telegram.miniapp_cors_origins),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(healthcheck.router)
    app.include_router(metrics_router)
    register_miniapp(app)
    app.include_router(legal_router)
    app.include_router(create_crypto_pay_router(normalized_crypto_path))
    app.include_router(create_lzt_pay_router(normalized_lzt_path))
    app.include_router(create_nice_pay_router(normalized_nice_path))
    app.include_router(create_platega_pay_router(normalized_platega_path))
    app.include_router(create_xrocket_pay_router(normalized_xrocket_path))
    app.include_router(
        create_ton_pay_router(
            config.ton_pay.invoice_webhook_path,
        )
    )
    app.include_router(
        create_heleket_pay_router(
            normalized_heleket_path,
            trusted_ips=config.heleket_pay.webhook_trusted_ips,
            trust_forwarded_ip=config.heleket_pay.webhook_trust_forwarded_ip,
        )
    )
    for key, value in dispatcher.workflow_data.items():
        setattr(app.state, key, value)
    app.state.dispatcher = dispatcher
    app.state.bot = bot
    app.state.shutdown_completed = False
    return app

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
from app.utils.routes import normalize_route_path


def setup_fastapi(app: FastAPI, dispatcher: Dispatcher, bot: Bot) -> FastAPI:
    config: AppConfig = dispatcher.workflow_data["config"]
    app.mount("/assets", StaticFiles(directory="assets"), name="assets")
    normalized_crypto_path = normalize_route_path(config.crypto_pay.webhook_path)
    normalized_lzt_path = normalize_route_path(config.lzt_pay.webhook_path)
    normalized_nice_path = normalize_route_path(config.nice_pay.webhook_path)
    normalized_platega_path = normalize_route_path(config.platega_pay.webhook_path)
    normalized_xrocket_path = normalize_route_path(config.xrocket_pay.webhook_path)
    normalized_heleket_path = normalize_route_path(config.heleket_pay.webhook_path)
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

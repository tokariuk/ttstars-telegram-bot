from __future__ import annotations

from fastapi import APIRouter

from .routes import admin, auth, catalog, checks, orders, profile, sell

router = APIRouter(prefix="/v1")
router.include_router(auth.router)
router.include_router(catalog.router)
router.include_router(orders.router)
router.include_router(sell.router)
router.include_router(checks.router)
router.include_router(profile.router)
router.include_router(admin.router)

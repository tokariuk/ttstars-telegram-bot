from __future__ import annotations

import logging
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network, ip_address, ip_network
from typing import Any

from fastapi import APIRouter, HTTPException, Request, status

from app.services.crud.stars_order import StarsOrderService
from app.services.heleket_pay import HeleketPayService, HeleketWebhookEvent
from app.utils import mjson

logger = logging.getLogger(__name__)

IPAddressOrNetwork = IPv4Address | IPv6Address | IPv4Network | IPv6Network


def create_router(
    path: str,
    *,
    trusted_ips: str | None = None,
    trust_forwarded_ip: bool = False,
) -> APIRouter:
    normalized_path = path if path.startswith("/") else f"/{path}"
    router = APIRouter(include_in_schema=False)
    trusted_sources = _parse_trusted_sources(trusted_ips)

    async def heleket_pay_webhook(request: Request) -> dict[str, bool]:
        heleket_pay_service: HeleketPayService = request.app.state.heleket_pay_service
        stars_order_service: StarsOrderService = request.app.state.stars_order_service
        if not heleket_pay_service.configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Heleket Pay is not configured.",
            )

        _validate_source_or_raise(
            request=request,
            trusted_sources=trusted_sources,
            trust_forwarded_ip=trust_forwarded_ip,
        )

        payload = await _decode_payload_or_raise(request=request)

        if not isinstance(payload, dict):
            return {"ok": True}

        _validate_signature_or_raise(
            service=heleket_pay_service,
            payload=payload,
        )

        event = heleket_pay_service.parse_webhook_event(payload)
        if event is None:
            return {"ok": True}
        if not _should_process_event(event):
            return {"ok": True}

        try:
            order = await stars_order_service.process_heleket_webhook_invoice(
                invoice_uuid=event.invoice_uuid,
                order_id=event.order_id,
                webhook_status=event.status,
            )
            logger.info(
                (
                    "Heleket webhook processed: invoice_uuid=%s order_id=%s "
                    "status=%s local_order_id=%s"
                ),
                event.invoice_uuid,
                event.order_id,
                event.status,
                order.id if order is not None else None,
            )
        except Exception:
            logger.exception(
                "Failed to process Heleket webhook: invoice_uuid=%s order_id=%s",
                event.invoice_uuid,
                event.order_id,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process payment.",
            ) from None

        return {"ok": True}

    router.add_api_route(normalized_path, heleket_pay_webhook, methods=["POST"])
    if normalized_path != "/" and not normalized_path.endswith("/"):
        router.add_api_route(f"{normalized_path}/", heleket_pay_webhook, methods=["POST"])

    return router


def _parse_trusted_sources(raw: str | None) -> tuple[IPAddressOrNetwork, ...]:
    if raw is None:
        return ()

    parsed: list[IPAddressOrNetwork] = []
    for token in raw.replace(";", ",").split(","):
        value = token.strip()
        if not value:
            continue
        try:
            source = ip_network(value, strict=False) if "/" in value else ip_address(value)
            parsed.append(source)
        except ValueError:
            logger.warning(
                "Heleket webhook trusted source entry is invalid and ignored: %s",
                value,
            )
    return tuple(parsed)


def _validate_source_or_raise(
    *,
    request: Request,
    trusted_sources: tuple[IPAddressOrNetwork, ...],
    trust_forwarded_ip: bool,
) -> None:
    if not trusted_sources:
        return
    source_ip = _resolve_source_ip(request=request, trust_forwarded_ip=trust_forwarded_ip)
    if _is_source_allowed(source_ip=source_ip, trusted=trusted_sources):
        return
    logger.warning("Heleket webhook rejected: source IP is not trusted (%s)", source_ip)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden.",
    )


def _resolve_source_ip(*, request: Request, trust_forwarded_ip: bool) -> str | None:
    if trust_forwarded_ip:
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            first = x_forwarded_for.split(",", 1)[0].strip()
            if first:
                return first
    if request.client is not None:
        return request.client.host
    return None


def _is_source_allowed(*, source_ip: str | None, trusted: tuple[IPAddressOrNetwork, ...]) -> bool:
    if source_ip is None:
        return False
    try:
        source = ip_address(source_ip)
    except ValueError:
        return False

    for candidate in trusted:
        if isinstance(candidate, (IPv4Address, IPv6Address)):
            if source == candidate:
                return True
            continue
        if source.version != candidate.version:
            continue
        if source in candidate:
            return True
    return False


async def _decode_payload_or_raise(*, request: Request) -> Any:
    try:
        return mjson.decode(await request.body())
    except Exception:
        logger.warning("Heleket webhook rejected: invalid JSON payload")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payload.",
        ) from None


def _validate_signature_or_raise(*, service: HeleketPayService, payload: dict[str, Any]) -> None:
    if service.verify_webhook_signature(payload=payload):
        return
    logger.warning("Heleket webhook rejected: invalid signature")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid signature.",
    )


def _should_process_event(event: HeleketWebhookEvent | None) -> bool:
    if event is None:
        return False
    if event.invoice_type not in {"payment", "unknown"}:
        logger.info(
            "Heleket webhook skipped: unsupported type=%s invoice_uuid=%s order_id=%s",
            event.invoice_type,
            event.invoice_uuid,
            event.order_id,
        )
        return False
    if event.invoice_uuid is None and event.order_id is None:
        return False
    return True

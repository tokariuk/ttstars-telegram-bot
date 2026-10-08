from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

from fastapi import FastAPI
from starlette.types import Message, Receive, Scope, Send

from app.utils import mjson


@dataclass(frozen=True, slots=True)
class ASGIResponse:
    status_code: int
    body: bytes
    headers: dict[str, str]

    def json(self) -> Any:
        return mjson.decode(self.body)


async def asgi_request(
    app: FastAPI,
    *,
    method: str,
    path: str,
    body: bytes = b"",
    query: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    client_host: str = "127.0.0.1",
) -> ASGIResponse:
    raw_headers = [(b"content-type", b"application/json")]
    raw_headers.extend(
        (name.lower().encode("latin-1"), value.encode("latin-1"))
        for name, value in (headers or {}).items()
    )
    scope: Scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": method.upper(),
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": urlencode(query or {}).encode("ascii"),
        "root_path": "",
        "headers": raw_headers,
        "client": (client_host, 12345),
        "server": ("testserver", 80),
    }
    request_sent = False
    messages: list[Message] = []

    async def receive() -> Message:
        nonlocal request_sent
        if request_sent:
            return {"type": "http.disconnect"}
        request_sent = True
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message: Message) -> None:
        messages.append(message)

    await app(scope, cast_receive(receive), cast_send(send))
    start = next(message for message in messages if message["type"] == "http.response.start")
    response_body = b"".join(
        message.get("body", b"") for message in messages if message["type"] == "http.response.body"
    )
    response_headers = {
        name.decode("latin-1"): value.decode("latin-1") for name, value in start["headers"]
    }
    return ASGIResponse(
        status_code=start["status"],
        body=response_body,
        headers=response_headers,
    )


def cast_receive(receive: Receive) -> Receive:
    return receive


def cast_send(send: Send) -> Send:
    return send

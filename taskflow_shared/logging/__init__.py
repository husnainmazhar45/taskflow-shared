"""ASGI request tracing without configuring the application's log handlers."""

import logging
import re
from contextvars import ContextVar
from uuid import uuid4

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

_request_id: ContextVar[str | None] = ContextVar("taskflow_request_id", default=None)
_VALID_REQUEST_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
REQUEST_ID_HEADER = "X-Request-ID"


def get_request_id() -> str | None:
    return _request_id.get()


class RequestIDFilter(logging.Filter):
    """Attach request_id to records; add this filter to application-owned handlers."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id() or "-"
        return True


class RequestIDMiddleware:
    """Propagate a safe ID or generate one; reset context even when the app fails.

    IDs are correlation hints supplied by clients, never authentication credentials.
    Wrap the complete ASGI application to include unhandled-error responses.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        values = [
            value.decode("latin-1")
            for key, value in scope.get("headers", [])
            if key.lower() == b"x-request-id"
        ]
        candidate = values[0] if len(values) == 1 else ""
        request_id = (
            candidate if _VALID_REQUEST_ID.fullmatch(candidate) else uuid4().hex
        )
        token = _request_id.set(request_id)

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", [])
                MutableHeaders(scope=message)[REQUEST_ID_HEADER] = request_id
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            _request_id.reset(token)

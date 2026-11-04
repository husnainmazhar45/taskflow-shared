import asyncio
import logging
from uuid import UUID

import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

from taskflow_shared.logging import RequestIDFilter, RequestIDMiddleware, get_request_id


async def trace_endpoint(request):
    await asyncio.sleep(0)
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "message", (), None)
    RequestIDFilter().filter(record)
    return JSONResponse({"request_id": get_request_id(), "log_id": record.request_id})


@pytest.fixture
def traced_app():
    return RequestIDMiddleware(Starlette(routes=[Route("/", trace_endpoint)]))


@pytest.mark.asyncio
async def test_generated_id_matches_response_and_logging(traced_app, client_factory):
    async with client_factory(traced_app) as client:
        response = await client.get("/")
    request_id = response.headers["x-request-id"]
    UUID(request_id)
    assert response.json() == {"request_id": request_id, "log_id": request_id}
    assert get_request_id() is None


@pytest.mark.asyncio
async def test_client_id_is_preserved(traced_app, client_factory):
    async with client_factory(traced_app) as client:
        response = await client.get("/", headers={"X-Request-ID": "import-123.test"})
    assert response.headers["x-request-id"] == "import-123.test"
    assert response.json()["request_id"] == "import-123.test"


@pytest.mark.parametrize(
    "value", ["", "a" * 129, "contains spaces", "bad\tvalue", "bad/value"]
)
@pytest.mark.asyncio
async def test_invalid_ids_are_replaced(traced_app, client_factory, value):
    async with client_factory(traced_app) as client:
        response = await client.get("/", headers={"X-Request-ID": value})
    UUID(response.headers["x-request-id"])
    assert response.headers["x-request-id"] != value


@pytest.mark.asyncio
async def test_duplicate_ids_are_replaced(traced_app, client_factory):
    async with client_factory(traced_app) as client:
        response = await client.get(
            "/", headers=[("X-Request-ID", "first"), ("X-Request-ID", "second")]
        )
    UUID(response.headers["x-request-id"])


@pytest.mark.asyncio
async def test_concurrent_requests_do_not_leak_context(traced_app, client_factory):
    async with client_factory(traced_app) as client:
        responses = await asyncio.gather(
            *[
                client.get("/", headers={"X-Request-ID": f"request-{index}"})
                for index in range(20)
            ]
        )
    for index, response in enumerate(responses):
        expected = f"request-{index}"
        assert response.json() == {"request_id": expected, "log_id": expected}
    assert get_request_id() is None


@pytest.mark.asyncio
async def test_unhandled_error_receives_id_and_context_is_reset(client_factory):
    async def fail(request):
        raise RuntimeError("failure")

    app = RequestIDMiddleware(Starlette(routes=[Route("/", fail)]))
    async with client_factory(app, raise_app_exceptions=False) as client:
        response = await client.get("/", headers={"X-Request-ID": "failure-123"})
    assert response.status_code == 500
    assert response.headers["x-request-id"] == "failure-123"
    assert get_request_id() is None
    async with client_factory(app) as client:
        with pytest.raises(RuntimeError, match="failure"):
            await client.get("/")
    assert get_request_id() is None


@pytest.mark.asyncio
async def test_streaming_body_keeps_context(client_factory):
    async def endpoint(request):
        async def chunks():
            await asyncio.sleep(0)
            yield get_request_id()

        return StreamingResponse(chunks(), headers={"X-Request-ID": "overwritten"})

    app = RequestIDMiddleware(Starlette(routes=[Route("/", endpoint)]))
    async with client_factory(app) as client:
        response = await client.get("/", headers={"X-Request-ID": "stream-123"})
    assert response.text == response.headers["x-request-id"] == "stream-123"
    assert get_request_id() is None


@pytest.mark.asyncio
async def test_non_http_scopes_are_passed_through():
    scopes = []

    async def app(scope, receive, send):
        scopes.append(scope)
        assert get_request_id() is None

    async def receive():
        return {"type": "lifespan.startup"}

    async def send(message):
        pass

    middleware = RequestIDMiddleware(app)
    for kind in ("lifespan", "websocket"):
        scope = {"type": kind}
        await middleware(scope, receive, send)
        assert scopes[-1] is scope


def test_log_filter_outside_request_uses_placeholder():
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "message", (), None)
    assert RequestIDFilter().filter(record)
    assert record.request_id == "-"


@pytest.mark.asyncio
async def test_minimal_asgi_response_without_headers():
    messages = []

    async def app(scope, receive, send):
        await send({"type": "http.response.start", "status": 200})
        await send({"type": "http.response.body", "body": b"ok"})

    async def receive():
        return {"type": "http.request", "body": b""}

    async def send(message):
        messages.append(message)

    await RequestIDMiddleware(app)({"type": "http", "headers": []}, receive, send)
    assert messages[0]["status"] == 200
    headers = dict(messages[0]["headers"])
    UUID(headers[b"x-request-id"].decode())
    assert get_request_id() is None

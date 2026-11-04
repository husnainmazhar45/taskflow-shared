from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.routing import Route

from taskflow_shared.contracts import IdentifiableSchema, TimestampedSchema
from taskflow_shared.enums import AppEnvironment, SortOrder
from taskflow_shared.errors import AppError, AppHTTPException, ErrorResponse


def test_domain_error_is_transport_independent():
    error = AppError("CONFLICT", "Already exists")
    assert str(error) == "Already exists"
    assert error.error.code == "CONFLICT"
    assert not isinstance(error, HTTPException)


@pytest.mark.asyncio
async def test_http_adapter_preserves_envelope_and_headers(client_factory):
    async def endpoint(request):
        raise AppHTTPException(
            401, "UNAUTHENTICATED", "Login required", {"WWW-Authenticate": "Bearer"}
        )

    async def handler(request, exc):
        return JSONResponse(
            {"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers
        )

    app = Starlette(
        routes=[Route("/", endpoint)], exception_handlers={HTTPException: handler}
    )
    async with client_factory(app) as client:
        response = await client.get("/")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json() == {
        "detail": {"error": {"code": "UNAUTHENTICATED", "message": "Login required"}}
    }


@pytest.mark.parametrize("code,message", [("", "message"), ("CODE", "")])
def test_empty_error_fields_fail_validation(code, message):
    with pytest.raises(ValidationError):
        AppError(code, message)


def test_error_contract_serialization():
    assert ErrorResponse(error={"code": "CODE", "message": "Message"}).model_dump() == {
        "error": {"code": "CODE", "message": "Message"}
    }


def test_contracts_support_attributes_and_json_round_trip():
    class Resource(IdentifiableSchema, TimestampedSchema):
        pass

    now = datetime.now(UTC)
    resource = Resource.model_validate(
        SimpleNamespace(id=uuid4(), created_at=now, updated_at=now)
    )
    assert Resource.model_validate_json(resource.model_dump_json()) == resource


def test_invalid_contract_values_fail_validation():
    with pytest.raises(ValidationError):
        IdentifiableSchema(id="invalid")
    with pytest.raises(ValidationError):
        TimestampedSchema(created_at="invalid", updated_at="invalid")


def test_common_enum_values():
    assert SortOrder.ASC.value == "asc"
    assert SortOrder.DESC.value == "desc"
    assert AppEnvironment("production") is AppEnvironment.PRODUCTION

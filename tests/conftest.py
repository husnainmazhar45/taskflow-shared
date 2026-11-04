import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def client_factory():
    """Each call owns an isolated transport; callers use an async context manager."""

    def make_client(app, **kwargs):
        return AsyncClient(
            transport=ASGITransport(app=app, **kwargs), base_url="http://test"
        )

    return make_client

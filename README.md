# TaskFlow Shared

An installable Python 3.12+ foundation for backend applications, using Pydantic 2.11 or later for typed generic models. Distribution name: `taskflow-shared`; import name: `taskflow_shared`.

## Installation

```bash
git clone https://github.com/husnainmazhar45/taskflow-shared.git
cd taskflow-shared
uv sync --extra test
uv run --extra test pytest
```

For editable development, run `pip install -e .` from this package directory, or declare this checkout as an editable path source in the consuming application's `pyproject.toml`. For deployment, build and install the wheel as described below.

## Public modules

| Module | Exports | Responsibility |
| --- | --- | --- |
| `config` | `BaseAppConfig` | Typed `APP_NAME`, `APP_ENV`/`ENVIRONMENT`, dotenv loading, environment detection |
| `errors` | `AppError`, `AppHTTPException`, `ErrorDetail`, `ErrorResponse` | Domain-independent errors and an optional HTTP adapter |
| `pagination` | `PaginationParams`, `PaginatedResponse[T]`, `clamp_pagination`, size constants | Validation, offset/limit calculation, common list response |
| `enums` | `AppEnvironment`, `SortOrder` | Infrastructure enums |
| `contracts` | `IdentifiableSchema`, `TimestampedSchema` | UUID and timestamp fields with ORM attribute support |
| `logging` | `RequestIDMiddleware`, `RequestIDFilter`, `get_request_id`, `REQUEST_ID_HEADER` | Request correlation and application-owned logging integration |

## Usage

```python
from taskflow_shared.config import BaseAppConfig
from taskflow_shared.pagination import PaginatedResponse, PaginationParams

config = BaseAppConfig()
params = PaginationParams(page=2, page_size=10)
assert params.offset == 10
response = PaginatedResponse[str](items=["example"], page=2, page_size=10, total=11)
```

Settings read `.env` as UTF-8, ignore unrelated entries, and allow subclasses to add application-specific fields. Accepted environments are `development`, `testing`, `staging`, and `production`; invalid values fail validation. Importing the package does not instantiate settings or connect to a database.

`PaginationParams` rejects page values below 1 and page sizes outside 1–100. `clamp_pagination` is an explicit alternative for callers that want normalization. HTTP adapters should preserve their existing validation policy. List responses contain exactly `items`, `page`, `page_size`, and `total`; empty pages beyond the last item are valid.

```python
from taskflow_shared.errors import AppHTTPException

raise AppHTTPException(404, "RESOURCE_NOT_FOUND", "Resource not found")
```

FastAPI's standard exception handler renders this as `{"detail":{"error":{"code":"RESOURCE_NOT_FOUND","message":"Resource not found"}}}`. Starlette applications must provide a JSON exception handler to produce that envelope; their default handler returns plain text. `ErrorResponse` describes the inner `error` envelope. `AppError` has no HTTP status or framework inheritance; the application owns domain-to-HTTP mapping.

## Request tracing and logging

```python
import logging
from fastapi import FastAPI
from taskflow_shared.logging import RequestIDFilter, RequestIDMiddleware

app = FastAPI()
application = RequestIDMiddleware(app)
handler = logging.StreamHandler()
handler.addFilter(RequestIDFilter())
handler.setFormatter(logging.Formatter("%(levelname)s %(request_id)s %(message)s"))
logging.getLogger("example").addHandler(handler)
```

Run the outer `application` ASGI object, for example `uvicorn app.main:application`. Wrapping outside the framework's error middleware includes unhandled 500 responses. Keep the inner FastAPI object for routes, OpenAPI, and test dependency overrides. Lifespan scopes and websockets pass through unchanged.

Exactly one incoming `X-Request-ID` is accepted when it contains 1–128 ASCII letters, digits, dots, underscores, or hyphens and begins with a letter or digit. Missing, invalid, oversized, or duplicate values receive a generated UUID hex ID. The same ID is present in response headers and `get_request_id()` throughout the response, including streaming. Context is reset in `finally`; concurrent requests are isolated. Outside requests, the helper returns `None` and the logging filter uses `-`.

Client IDs are untrusted correlation hints, not uniqueness guarantees or authorization credentials. The package does not configure root logging, log request bodies, or read application secrets.

## Boundaries

Task status/priority enums, transition rules, authorization policies, database models, repository queries, authentication, and import normalization belong in the application. This package must not import the application or require PostgreSQL/MongoDB. Framework coupling is limited to the Starlette HTTP adapter and ASGI middleware.

See [architecture boundaries](docs/architecture-boundaries.md), [testing strategy](docs/testing-strategy.md), and [demo](demos/01-shared-package/demo.md).

## Quality checks and distributions

```bash
uv run --extra test ruff check .
uv run --extra test ruff format --check .
uv run --extra test mypy taskflow_shared
uv run --extra test pytest
uv build
```

Build the wheel and source distribution, then install the wheel into a clean environment and import all six modules from outside the source directory. Build output belongs in `dist/` and is not committed. `py.typed` is shipped for static type checking.

## License

MIT

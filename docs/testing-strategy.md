# Shared package testing strategy

The unit suite runs without databases or the consuming application. Tests isolate environment variables, use temporary dotenv files, and build small ASGI applications through reusable `client_factory` and `traced_app` fixtures.

| Contract | Evidence |
| --- | --- |
| Settings | Defaults, environment and constructor precedence, invalid environments, subclass extension, dotenv and unrelated keys |
| Pagination | Defaults, offset/limit, size bounds, invalid values, explicit clamping, typed item serialization, negative totals, empty pages |
| Errors/contracts | Error independence, HTTP envelope and headers, empty fields, UUID/date validation, attribute parsing, JSON round trip |
| Request IDs | Generation, propagation, invalid/duplicate replacement, 20 concurrent requests, streaming, unhandled failures, context reset, non-HTTP passthrough |
| Logging | Same ID as the response; `-` when no request is active |

Run `uv run --extra test pytest` from this repository. Run lint, formatting, strict type checking, and distribution smoke checks as described in the README. The application separately tests real FastAPI integration, existing API contracts, persistence, and workflow behavior.

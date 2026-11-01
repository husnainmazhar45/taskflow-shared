# Installable Shared Backend Package

## Objective

Prove that all six foundation modules work independently of TaskFlow's application and databases.

## Scenario

Several services need consistent settings, errors, pagination, response fields, and trace IDs without importing each other's business logic.

## Commands / Steps Used

```bash
uv sync --extra test
uv run --extra test pytest
uv run --extra test ruff check .
uv run --extra test ruff format --check .
uv run --extra test mypy taskflow_shared
uv build
```

Install `dist/taskflow_shared-0.1.0-py3-none-any.whl` in a clean environment, change directory outside the repository, and import `config`, `errors`, `pagination`, `enums`, `contracts`, and `logging` from `taskflow_shared`. Confirm `py.typed` is included. See the consuming Session 4 demo for the real app integration.

## Expected Behavior

All tests and static checks pass without Postgres/MongoDB. An incoming valid ID matches response/log context; invalid IDs are replaced. Concurrent requests remain isolated and request context is cleared on success and failure. A wheel import must load from the installed environment rather than the source directory.

## Actual Findings

The independent test suite passes without application imports or database services. Static analysis and package builds pass. Installing the wheel in a clean environment makes all six public modules available and includes the `py.typed` marker.

## Evidence

| Verification | Observed result |
| --- | --- |
| Independent unit suite | 43 tests passed |
| Ruff lint and formatting | Passed |
| Strict type checks | Passed for all 7 package source files |
| Wheel and source archive | Built successfully |
| Clean wheel installation | All six modules and `py.typed` available outside the source checkout |

`tests/test_config.py`, `tests/test_pagination.py`, `tests/test_errors_contracts.py`, and `tests/test_request_id.py` cover valid and invalid cases. Request tracing tests exercise 20 concurrent requests, streaming, unhandled exceptions, non-HTTP scopes, and minimal ASGI response messages.

## What We Learned

Reusable infrastructure needs independent installation and behavioral checks. Typed contracts reduce duplication while leaving business policies in the application. Request context must remain isolated between simultaneous requests and be cleared on both success and failure.

# TaskFlow Shared (`taskflow-shared`)

Reusable foundational utilities, configuration, errors, pagination, and request tracing for TaskFlow backend services.

## Installation

### From GitHub
```bash
pip install git+https://github.com/<your-username>/taskflow-shared.git@v0.1.0
```

### Local Editable Mode (Development)
```bash
pip install -e /path/to/taskflow-shared
```

## Modules Overview
- `taskflow_shared.config`: Base configuration and environment detection (`BaseAppConfig`)
- `taskflow_shared.errors`: Application exceptions and standard error response schemas (`AppError`, `AppHTTPException`)
- `taskflow_shared.pagination`: Standard query parameter clamping and generic `PaginatedResponse[T]`
- `taskflow_shared.logging`: ASGI Request-ID tracing middleware (`RequestIDMiddleware`) and contextvar helpers
- `taskflow_shared.contracts` & `enums`: Common schemas (`TimestampedSchema`, `IdentifiableSchema`) and enums (`AppEnvironment`, `SortOrder`)

## License
MIT

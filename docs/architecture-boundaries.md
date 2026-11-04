# Shared package ownership

The package owns typed base settings, common error contracts, pagination, generic response field mixins, infrastructure enums, and request correlation. It depends on Pydantic, Pydantic Settings, and Starlette; it has no dependency on FastAPI, SQLAlchemy, database drivers, or a consuming application.

The consuming application owns database settings, domain entities and enums, authentication, role checks, HTTP routing, service orchestration, workflow decisions, persistence, migrations, and raw import processing. The HTTP exception adapter standardizes presentation without deciding whether a user may perform an action.

Dependency direction is application → shared package. Never import `app` from `taskflow_shared`. Imports have no settings, database, or root-logging side effects.

The Session 4 integration keeps this repository as an independent checkout in `packages/taskflow_shared/`, installed through an editable path source. Its code is reviewed here rather than copied into the application repository. The application documents its concrete before/after changes and the revision used for any released integration.

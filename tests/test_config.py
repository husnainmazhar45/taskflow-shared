import pytest
from pydantic import ValidationError

from taskflow_shared.config import BaseAppConfig
from taskflow_shared.enums import AppEnvironment


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    for name in ("APP_NAME", "APP_ENV", "ENVIRONMENT"):
        monkeypatch.delenv(name, raising=False)


def test_defaults_do_not_require_database_settings():
    config = BaseAppConfig(_env_file=None)
    assert config.APP_NAME == "TaskFlow API"
    assert config.ENVIRONMENT is AppEnvironment.DEVELOPMENT
    assert not config.is_production


def test_environment_overrides_and_explicit_values(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_NAME", "Worker")
    config = BaseAppConfig(_env_file=None)
    assert config.is_production
    assert config.APP_NAME == "Worker"
    assert BaseAppConfig(APP_NAME="API", _env_file=None).APP_NAME == "API"


@pytest.mark.parametrize("value", ["", "prodution", "unsupported"])
def test_invalid_environment_is_rejected(monkeypatch, value):
    monkeypatch.setenv("APP_ENV", value)
    with pytest.raises(ValidationError):
        BaseAppConfig(_env_file=None)


def test_dotenv_and_subclass_extension(tmp_path):
    dotenv = tmp_path / ".env"
    dotenv.write_text("APP_ENV=staging\nUNRELATED_SETTING=ignored\n")

    class WorkerConfig(BaseAppConfig):
        WORKERS: int = 2

    config = WorkerConfig(_env_file=dotenv)
    assert config.ENVIRONMENT is AppEnvironment.STAGING
    assert config.WORKERS == 2

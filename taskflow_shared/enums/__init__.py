"""Infrastructure values shared by backend applications."""

from enum import StrEnum


class AppEnvironment(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"

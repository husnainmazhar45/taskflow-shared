"""Validated pagination models and explicitly opt-in normalization."""

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100


class PaginationParams(BaseModel):
    model_config = ConfigDict(frozen=True)

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


def clamp_pagination(
    page: int = 1, page_size: int = DEFAULT_PAGE_SIZE
) -> PaginationParams:
    """Normalize trusted integer inputs; HTTP adapters can instead reject bad input."""
    return PaginationParams(
        page=max(1, page), page_size=min(MAX_PAGE_SIZE, max(1, page_size))
    )


class PaginatedResponse[T](BaseModel):
    items: list[T]
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1, le=MAX_PAGE_SIZE)
    total: int = Field(..., ge=0)

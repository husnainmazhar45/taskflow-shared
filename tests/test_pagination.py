import pytest
from pydantic import BaseModel, ValidationError

from taskflow_shared.pagination import (
    PaginatedResponse,
    PaginationParams,
    clamp_pagination,
)


@pytest.mark.parametrize("page,size,offset", [(1, 10, 0), (3, 20, 40), (2, 100, 100)])
def test_offsets_and_limits(page, size, offset):
    params = PaginationParams(page=page, page_size=size)
    assert params.offset == offset
    assert params.limit == size


def test_defaults():
    assert PaginationParams().model_dump() == {"page": 1, "page_size": 10}


@pytest.mark.parametrize(
    "values", [dict(page=0), dict(page=-1), dict(page_size=0), dict(page_size=101)]
)
def test_invalid_pagination_is_rejected(values):
    with pytest.raises(ValidationError):
        PaginationParams(**values)


@pytest.mark.parametrize(
    "page,size,expected", [(0, 0, (1, 1)), (-5, 1000, (1, 100)), (3, 20, (3, 20))]
)
def test_explicit_clamping(page, size, expected):
    params = clamp_pagination(page, size)
    assert (params.page, params.page_size) == expected


def test_generic_response_serializes_items_without_extra_fields():
    class Item(BaseModel):
        name: str

    result = PaginatedResponse[Item](
        items=[{"name": "example"}], page=1, page_size=10, total=1
    )
    assert result.model_dump() == {
        "items": [{"name": "example"}],
        "page": 1,
        "page_size": 10,
        "total": 1,
    }
    with pytest.raises(ValidationError):
        PaginatedResponse[Item](items=[{}], page=1, page_size=10, total=1)


@pytest.mark.parametrize("total", [-1, -100])
def test_negative_total_is_rejected(total):
    with pytest.raises(ValidationError):
        PaginatedResponse[str](items=[], page=1, page_size=10, total=total)


def test_empty_and_out_of_range_pages_are_representable():
    response = PaginatedResponse[str](items=[], page=20, page_size=10, total=0)
    assert response.items == []

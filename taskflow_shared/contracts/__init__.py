"""Reusable response fields; these contracts do not own domain entities."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IdentifiableSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID


class TimestampedSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    updated_at: datetime

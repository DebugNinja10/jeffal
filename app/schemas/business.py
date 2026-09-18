from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BusinessCreate(BaseModel):
    name: str
    sector: str
    location: str | None = None


class BusinessUpdate(BaseModel):
    name: str | None = None
    sector: str | None = None
    location: str | None = None


class BusinessResponse(BaseModel):
    id: int
    name: str
    sector: str
    location: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

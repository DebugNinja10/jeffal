from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    full_name: str
    phone: str
    preferred_language: str = "wolof"
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    phone: str
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    preferred_language: str | None = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    preferred_language: str

    model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel, ConfigDict, Field, field_validator


def validate_text(value: str) -> str:
    value = value.strip()
    if not value or len(value) > 150:
        raise ValueError("Valeur invalide")
    return value


def validate_phone(value: str) -> str:
    value = value.strip()
    if len(value) > 30 or not value.replace("+", "").replace(" ", "").isdigit():
        raise ValueError("Numéro de téléphone invalide")
    return value


class UserCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    phone: str = Field(min_length=3, max_length=30)
    preferred_language: str = "wolof"
    password: str = Field(min_length=8)

    _full_name = field_validator("full_name")(validate_text)
    _phone = field_validator("phone")(validate_phone)


class UserLogin(BaseModel):
    phone: str
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    preferred_language: str | None = None

    _full_name = field_validator("full_name")(validate_text)
    _phone = field_validator("phone")(validate_phone)


class UserResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    preferred_language: str

    model_config = ConfigDict(from_attributes=True)

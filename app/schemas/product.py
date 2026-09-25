from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    category: str | None = None
    unit: str
    base_unit: str | None = None
    package_size: float | None = None
    purchase_price: float
    selling_price: float
    stock_quantity: float = 0


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    unit: str | None = None
    base_unit: str | None = None
    package_size: float | None = None
    purchase_price: float | None = None
    selling_price: float | None = None
    stock_quantity: float | None = None


class ProductResponse(BaseModel):
    id: int
    business_id: int
    name: str
    category: str | None
    unit: str
    base_unit: str | None
    package_size: float | None
    purchase_price: float
    selling_price: float
    stock_quantity: float
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

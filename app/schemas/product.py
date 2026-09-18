from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    category: str | None = None
    unit: str
    purchase_price: float
    selling_price: float
    stock_quantity: int = 0


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    unit: str | None = None
    purchase_price: float | None = None
    selling_price: float | None = None
    stock_quantity: int | None = None


class ProductResponse(BaseModel):
    id: int
    business_id: int
    name: str
    category: str | None
    unit: str
    purchase_price: float
    selling_price: float
    stock_quantity: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

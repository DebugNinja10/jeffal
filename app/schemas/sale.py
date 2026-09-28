from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SaleItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: float = Field(gt=0)
    unit: str = "unité"


class SaleCreate(BaseModel):
    payment_method: str = Field(min_length=1, max_length=30)
    items: list[SaleItemCreate] = Field(min_length=1, max_length=100)


class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: float
    unit: str
    unit_price: float
    subtotal: float

    model_config = ConfigDict(from_attributes=True)


class SaleResponse(BaseModel):
    id: int
    business_id: int
    total_amount: float
    payment_method: str
    sold_at: datetime
    created_at: datetime
    items: list[SaleItemResponse]

    model_config = ConfigDict(from_attributes=True)

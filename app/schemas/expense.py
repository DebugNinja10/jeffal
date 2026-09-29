from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0)
    category: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    payment_method: str = Field(min_length=1, max_length=30)
    spent_at: datetime | None = None


class ExpenseResponse(BaseModel):
    id: int
    business_id: int
    amount: float
    category: str
    description: str | None
    payment_method: str
    spent_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

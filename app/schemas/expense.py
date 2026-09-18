from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0)
    category: str
    description: str | None = None
    payment_method: str
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

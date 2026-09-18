from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DebtCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=150)
    amount: float = Field(gt=0)
    description: str | None = None
    due_date: datetime | None = None


class DebtPaymentCreate(BaseModel):
    amount: float = Field(gt=0)
    note: str | None = None
    paid_at: datetime | None = None


class DebtPaymentResponse(BaseModel):
    id: int
    debt_id: int
    amount: float
    note: str | None
    paid_at: datetime
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class DebtResponse(BaseModel):
    id: int
    business_id: int
    customer_name: str
    initial_amount: float
    remaining_amount: float
    description: str | None
    status: str
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime
    payments: list[DebtPaymentResponse] = []

    model_config = ConfigDict(
        from_attributes=True
    )

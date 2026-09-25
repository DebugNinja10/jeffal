from pydantic import BaseModel, Field

from app.agents.intents import IntentName


class SaleItemIntent(BaseModel):
    product_name: str
    quantity: int = Field(gt=0)
    unit: str | None = None


class SaleIntentData(BaseModel):
    items: list[SaleItemIntent] = Field(min_length=1)
    payment_method: str | None = None


class ExpenseIntentData(BaseModel):
    amount: float = Field(gt=0)
    category: str | None = None
    description: str | None = None


class DebtIntentData(BaseModel):
    customer_name: str = Field(min_length=1)
    amount: float = Field(gt=0)
    description: str | None = None


class DebtPaymentIntentData(BaseModel):
    customer_name: str = Field(min_length=1)
    amount: float = Field(gt=0)


class StockQueryIntentData(BaseModel):
    product_name: str = Field(min_length=1)


class AgentUnderstanding(BaseModel):
    intent: IntentName
    data: dict
    confidence: float = Field(ge=0, le=1)
    needs_clarification: bool = False

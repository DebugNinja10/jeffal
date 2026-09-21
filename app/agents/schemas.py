from pydantic import BaseModel, Field

from app.agents.intents import IntentName


class SaleItemIntent(BaseModel):
    product_name: str
    quantity: int = Field(gt=0)
    unit: str | None = None


class SaleIntentData(BaseModel):
    items: list[SaleItemIntent] = Field(min_length=1)
    payment_method: str | None = None


class AgentUnderstanding(BaseModel):
    intent: IntentName
    data: dict
    confidence: float = Field(ge=0, le=1)
    needs_clarification: bool = False

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    business_id: int = Field(gt=0)
    message: str = Field(min_length=1)


class AgentResponse(BaseModel):
    intent: str
    confidence: float
    needs_clarification: bool
    result: dict | None = None
    message: str

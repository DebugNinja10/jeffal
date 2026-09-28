from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    business_id: int = Field(gt=0)
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = Field(default=None, max_length=100)


class AgentResponse(BaseModel):
    intent: str
    confidence: float
    needs_clarification: bool
    result: dict | None = None
    message: str
    conversation_id: str | None = None

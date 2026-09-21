from app.agents.intent_parser import IntentParser
from app.agents.intents import IntentName
from app.agents.schemas import (
    AgentUnderstanding,
    SaleIntentData,
)


class MockIntentParser(IntentParser):

    def parse(self, text: str) -> AgentUnderstanding:
        text = text.lower().strip()

        if "ceeb" in text and "2 kilo" in text:
            sale_data = SaleIntentData(
                items=[
                    {
                        "product_name": "ceeb",
                        "quantity": 2,
                        "unit": "kg",
                    }
                ],
                payment_method=None,
            )

            return AgentUnderstanding(
                intent=IntentName.ENREGISTRER_VENTE,
                data=sale_data.model_dump(),
                confidence=0.95,
                needs_clarification=False,
            )

        return AgentUnderstanding(
            intent=IntentName.UNKNOWN,
            data={},
            confidence=0.0,
            needs_clarification=True,
        )

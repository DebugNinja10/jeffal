from app.agents.intents import IntentName
from app.agents.intent_parser import IntentParser
from app.agents.schemas import AgentUnderstanding


class AgentService:

    def __init__(self, parser: IntentParser):
        self.parser = parser

    def understand(self, text: str) -> AgentUnderstanding:
        text = text.strip()

        if not text:
            raise ValueError("Le message ne peut pas être vide.")

        sale_data = self.parser.parse(text)

        return AgentUnderstanding(
            intent=IntentName.ENREGISTRER_VENTE,
            data=sale_data.model_dump(),
            confidence=0.95,
        )

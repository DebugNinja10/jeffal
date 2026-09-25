from app.agents.intent_parser import IntentParser
from app.agents.schemas import AgentUnderstanding


class AgentService:

    def __init__(self, parser: IntentParser):
        self.parser = parser

    def understand(self, text: str) -> AgentUnderstanding:
        text = text.strip()

        if not text:
            raise ValueError(
                "Le message ne peut pas être vide."
            )

        return self.parser.parse(text)

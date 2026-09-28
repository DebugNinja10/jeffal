import os

from app.agents.intent_parser import IntentParser
from app.agents.mock_intent_parser import MockIntentParser
from app.agents.gemini_intent_parser import GeminiIntentParser
from app.agents.schemas import AgentUnderstanding


class HybridIntentParser(IntentParser):
    """
    Parser hybride de JËFAL.

    - MockIntentParser reste le moteur par défaut.
    - Gemini peut être activé avec USE_GEMINI=true.
    - En cas d'erreur Gemini, retour automatique vers le Mock.
    """

    def __init__(self):
        self.mock_parser = MockIntentParser()

        self.use_gemini = (
            os.getenv("USE_GEMINI", "false").lower()
            in {"1", "true", "yes", "on"}
        )

        self.gemini_parser = None

        if self.use_gemini:
            try:
                self.gemini_parser = GeminiIntentParser()
            except Exception:
                self.gemini_parser = None

    def parse(self, text: str) -> AgentUnderstanding:
        text = text.strip()

        if not text:
            raise ValueError("Le message ne peut pas être vide.")

        if self.gemini_parser is not None:
            try:
                return self.gemini_parser.parse(text)
            except Exception:
                pass

        return self.mock_parser.parse(text)

from abc import ABC, abstractmethod

from app.agents.schemas import AgentUnderstanding


class IntentParser(ABC):

    @abstractmethod
    def parse(self, text: str) -> AgentUnderstanding:
        """
        Analyse un message utilisateur
        et retourne une compréhension structurée.
        """
        raise NotImplementedError

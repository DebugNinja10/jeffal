import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.agents.intent_parser import IntentParser
from app.agents.schemas import AgentUnderstanding
from app.agents.intents import IntentName


load_dotenv()


class GeminiSaleItem(BaseModel):
    product_name: str | None = None
    quantity: float | None = None
    unit: str | None = None


class GeminiData(BaseModel):
    items: list[GeminiSaleItem] | None = None
    payment_method: str | None = None
    amount: float | None = None
    category: str | None = None
    description: str | None = None
    customer_name: str | None = None
    product_name: str | None = None


class GeminiResponse(BaseModel):
    intent: IntentName
    data: GeminiData
    confidence: float = Field(ge=0, le=1)
    needs_clarification: bool = False


class GeminiIntentParser(IntentParser):
    """
    Parser d'intentions basé sur Gemini.

    Gemini comprend le message et retourne une structure.
    Il n'accède jamais directement à la base de données
    et n'exécute aucune action métier.
    """

    def __init__(self, model: str = "gemini-3.8-flash"):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY n'est pas configurée.")

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def parse(self, text: str) -> AgentUnderstanding:
        text = text.strip()

        if not text:
            raise ValueError("Le message ne peut pas être vide.")

        prompt = f"""
Tu es le moteur de compréhension linguistique de JËFAL,
un assistant vocal destiné aux petits commerçants et entrepreneurs
au Sénégal.

Ta mission est UNIQUEMENT de comprendre le message utilisateur
et de retourner une structure JSON conforme au schéma demandé.

Tu ne dois jamais :
- inventer une information absente du message ;
- exécuter une action ;
- accéder à une base de données ;
- écrire du SQL ;
- créer un identifiant produit ;
- supposer une quantité absente.

Intentions disponibles :

- enregistrer_vente
- enregistrer_depense
- enregistrer_dette
- enregistrer_remboursement
- consulter_stock
- analyser_activite
- unknown

Règles importantes :

1. VENTE
   - Retourne TOUS les produits mentionnés.
   - Chaque produit doit avoir son nom, sa quantité et son unité si
     l'unité est explicitement donnée.
   - Si l'unité est absente, utilise null.
   - Si le mode de paiement est absent, utilise null.

2. DEPENSE
   - amount contient le montant.
   - category et description sont null si absents.

3. DETTE
   - customer_name contient le nom du client.
   - amount contient le montant.
   - description est null si absente.

4. REMBOURSEMENT
   - customer_name contient le nom du client.
   - amount contient le montant.

5. STOCK
   - product_name contient le produit demandé.

6. ANALYSE
   - Utilise une structure data vide.

7. UNKNOWN
   - Utilise une structure data vide.

Tu comprends le français et le wolof.
Les nombres peuvent être exprimés en chiffres ou en mots.

Ne transforme jamais une consultation en action d'enregistrement.

Message utilisateur :
{text}
"""

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=GeminiResponse,
                    temperature=0,
                ),
            )

            if not response.parsed:
                raise RuntimeError("Gemini n'a retourné aucune structure valide.")

            result = response.parsed

            data = result.data.model_dump(exclude_none=True)

            return AgentUnderstanding(
                intent=result.intent,
                data=data,
                confidence=result.confidence,
                needs_clarification=result.needs_clarification,
            )

        except Exception as exc:
            raise RuntimeError(
                "Erreur lors de l'analyse du message avec Gemini."
            ) from exc

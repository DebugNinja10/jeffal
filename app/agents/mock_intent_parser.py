import re

from app.agents.intent_parser import IntentParser
from app.agents.intents import IntentName
from app.agents.schemas import (
    AgentUnderstanding,
    DebtIntentData,
    DebtPaymentIntentData,
    ExpenseIntentData,
    SaleIntentData,
    StockQueryIntentData,
)


class MockIntentParser(IntentParser):

    def parse(self, text: str) -> AgentUnderstanding:
        text = text.lower().strip()

        # ============================================================
        # CONSULTATION DU STOCK
        # ============================================================

        stock_patterns = [
            r"combien de (.+?)\s+il me reste",
            r"il me reste combien de (.+)",
            r"combien de (.+?)\s+reste",
            r"quel est le stock de (.+)",
            r"combien reste[- ]t[- ]il de (.+)",
        ]

        product_name = None

        for pattern in stock_patterns:
            match = re.search(pattern, text)

            if match:
                product_name = match.group(1).strip()
                break

        if product_name:
            product_name = product_name.rstrip(" ?!.,;:")

            stock_data = StockQueryIntentData(
                product_name=product_name,
            )

            return AgentUnderstanding(
                intent=IntentName.CONSULTER_STOCK,
                data=stock_data.model_dump(),
                confidence=0.90,
                needs_clarification=False,
            )

        # ============================================================
        # NOUVELLE DETTE
        # ============================================================

        debt_match = re.search(
            r"^(.+?)\s+me\s+doit\s+(\d+(?:[.,]\d+)?)",
            text,
        )

        if debt_match:
            customer_name = debt_match.group(1).strip()

            amount = float(
                debt_match.group(2).replace(",", ".")
            )

            debt_data = DebtIntentData(
                customer_name=customer_name,
                amount=amount,
                description="Dette enregistrée par l'agent",
            )

            return AgentUnderstanding(
                intent=IntentName.ENREGISTRER_DETTE,
                data=debt_data.model_dump(),
                confidence=0.90,
                needs_clarification=False,
            )

        # ============================================================
        # REMBOURSEMENT
        # ============================================================

        if (
            "remboursé" in text
            or "rembourse" in text
        ):
            match = re.search(
                r"\d+(?:[.,]\d+)?",
                text,
            )

            if not match:
                return AgentUnderstanding(
                    intent=IntentName.ENREGISTRER_REMBOURSEMENT,
                    data={},
                    confidence=0.5,
                    needs_clarification=True,
                )

            amount = float(
                match.group().replace(",", ".")
            )

            customer_match = re.search(
                r"(?:à|a)\s+([a-zà-ÿ'-]+(?:\s+[a-zà-ÿ'-]+)*)",
                text,
            )

            if not customer_match:
                return AgentUnderstanding(
                    intent=IntentName.ENREGISTRER_REMBOURSEMENT,
                    data={},
                    confidence=0.5,
                    needs_clarification=True,
                )

            customer_name = customer_match.group(1).strip()

            payment_data = DebtPaymentIntentData(
                customer_name=customer_name,
                amount=amount,
            )

            return AgentUnderstanding(
                intent=IntentName.ENREGISTRER_REMBOURSEMENT,
                data=payment_data.model_dump(),
                confidence=0.90,
                needs_clarification=False,
            )

        # ============================================================
        # DÉPENSE
        # ============================================================

        if (
            "dépensé" in text
            or "depense" in text
            or "dépense" in text
        ):
            match = re.search(
                r"\d+(?:[.,]\d+)?",
                text,
            )

            if not match:
                return AgentUnderstanding(
                    intent=IntentName.ENREGISTRER_DEPENSE,
                    data={},
                    confidence=0.5,
                    needs_clarification=True,
                )

            amount = float(
                match.group().replace(",", ".")
            )

            if "transport" in text:
                category = "transport"

            elif (
                "sac" in text
                or "emballage" in text
            ):
                category = "emballage"

            elif (
                "marchandise" in text
                or "achat" in text
                or "approvisionnement" in text
            ):
                category = "approvisionnement"

            elif "loyer" in text:
                category = "loyer"

            elif (
                "électricité" in text
                or "courant" in text
            ):
                category = "électricité"

            else:
                category = "autre"

            expense_data = ExpenseIntentData(
                amount=amount,
                category=category,
                description=category,
            )

            return AgentUnderstanding(
                intent=IntentName.ENREGISTRER_DEPENSE,
                data=expense_data.model_dump(),
                confidence=0.90,
                needs_clarification=False,
            )

        # ============================================================
        # VENTE
        # ============================================================

        sale_patterns = [
            # Exemple :
            # "j'ai vendu 2 sacs de riz"
            r"(?:j'ai\s+)?vendu\s+(\d+)\s+(?:sac|sacs|kg|kilo|kilos|litre|litres|unité|unités)\s+(?:de\s+)?(.+)",

            # Exemple :
            # "j'ai vendu 2 riz"
            r"(?:j'ai\s+)?vendu\s+(\d+)\s+(.+)",

            # Exemple Wolof :
            # "mun naa ceeb 2 kilos"
            r"(?:mun naa|maa ngi)\s+(.+?)\s+(\d+)\s+(kilo|kilos|kg|sac|sacs|litre|litres)",
        ]

        for index, pattern in enumerate(sale_patterns):

            match = re.search(pattern, text)

            if not match:
                continue

            if index == 2:
                # Format Wolof :
                # produit + quantité + unité
                product_name = match.group(1).strip()
                quantity = int(match.group(2))
                unit = match.group(3)

            else:
                # Format français :
                # quantité + unité + produit
                quantity = int(match.group(1))

                if index == 0:
                    unit = re.search(
                        r"\d+\s+(sac|sacs|kg|kilo|kilos|litre|litres|unité|unités)",
                        match.group(0),
                    ).group(1)

                    product_name = match.group(2).strip()

                else:
                    product_name = match.group(2).strip()
                    unit = None

            product_name = product_name.rstrip(
                " ?!.,;:"
            )

            if not product_name:
                return AgentUnderstanding(
                    intent=IntentName.ENREGISTRER_VENTE,
                    data={},
                    confidence=0.5,
                    needs_clarification=True,
                )

            sale_data = SaleIntentData(
                items=[
                    {
                        "product_name": product_name,
                        "quantity": quantity,
                        "unit": unit,
                    }
                ],
                payment_method=None,
            )

            return AgentUnderstanding(
                intent=IntentName.ENREGISTRER_VENTE,
                data=sale_data.model_dump(),
                confidence=0.90,
                needs_clarification=False,
            )

        # ============================================================
        # INTENT INCONNUE
        # ============================================================

        return AgentUnderstanding(
            intent=IntentName.UNKNOWN,
            data={},
            confidence=0.0,
            needs_clarification=True,
        )

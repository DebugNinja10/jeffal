import re

from app.agents.intents import IntentName
from app.agents.schemas import (
    AgentUnderstanding,
    DebtIntentData,
    DebtPaymentIntentData,
    ExpenseIntentData,
    SaleIntentData,
    StockQueryIntentData,
)


class MockIntentParser:

    def parse(self, text: str) -> AgentUnderstanding:

        text = text.strip().lower()

        # ============================================================
        # CONSULTATION DU STOCK
        # ============================================================

        stock_patterns = [
            r"(?:combien|quel)\s+(?:me\s+)?reste(?:-t-il)?\s+(?:de\s+)?(.+)",
            r"stock\s+(?:de\s+)?(.+)",
            r"(?:combien|quel)\s+(?:est\s+)?(?:le\s+)?stock\s+(?:de\s+)?(.+)",
            r"j'ai\s+combien\s+(?:de\s+)?(.+)",
        ]

        for pattern in stock_patterns:

            match = re.search(pattern, text)

            if not match:
                continue

            product_name = match.group(1).strip()

            product_name = product_name.rstrip(
                " ?!.,;:"
            )

            if not product_name:
                return AgentUnderstanding(
                    intent=IntentName.CONSULTER_STOCK,
                    data={},
                    confidence=0.5,
                    needs_clarification=True,
                )

            stock_data = StockQueryIntentData(
                product_name=product_name
            )

            return AgentUnderstanding(
                intent=IntentName.CONSULTER_STOCK,
                data=stock_data.model_dump(),
                confidence=0.90,
                needs_clarification=False,
            )

        # ============================================================
        # REMBOURSEMENT DE DETTE
        # ============================================================

        repayment_patterns = [
            r"(?:j'ai\s+)?remboursé\s+([0-9]+(?:[.,][0-9]+)?)\s+(?:à|a)\s+(.+)",
            r"(?:j'ai\s+)?payé\s+([0-9]+(?:[.,][0-9]+)?)\s+(?:à|a)\s+(.+)",
        ]

        for pattern in repayment_patterns:

            match = re.search(pattern, text)

            if not match:
                continue

            amount = float(
                match.group(1).replace(",", ".")
            )

            customer_name = match.group(2).strip()

            customer_name = customer_name.rstrip(
                " ?!.,;:"
            )

            if not customer_name:
                return AgentUnderstanding(
                    intent=IntentName.ENREGISTRER_REMBOURSEMENT,
                    data={},
                    confidence=0.5,
                    needs_clarification=True,
                )

            repayment_data = DebtPaymentIntentData(
                customer_name=customer_name,
                amount=amount,
            )

            return AgentUnderstanding(
                intent=IntentName.ENREGISTRER_REMBOURSEMENT,
                data=repayment_data.model_dump(),
                confidence=0.90,
                needs_clarification=False,
            )

        # ============================================================
        # DETTE
        # ============================================================

        debt_patterns = [
            r"(?:dette|doit)\s+(.+?)\s+([0-9]+(?:[.,][0-9]+)?)",
            r"(.+?)\s+(?:me\s+)?doit\s+([0-9]+(?:[.,][0-9]+)?)",
        ]

        for pattern in debt_patterns:

            match = re.search(pattern, text)

            if not match:
                continue

            customer_name = match.group(1).strip()

            amount = float(
                match.group(2).replace(",", ".")
            )

            customer_name = customer_name.rstrip(
                " ?!.,;:"
            )

            if not customer_name:
                return AgentUnderstanding(
                    intent=IntentName.ENREGISTRER_DETTE,
                    data={},
                    confidence=0.5,
                    needs_clarification=True,
                )

            debt_data = DebtIntentData(
                customer_name=customer_name,
                amount=amount,
                description=None,
            )

            return AgentUnderstanding(
                intent=IntentName.ENREGISTRER_DETTE,
                data=debt_data.model_dump(),
                confidence=0.90,
                needs_clarification=False,
            )

        # ============================================================
        # DEPENSE
        # ============================================================

        expense_patterns = [
            r"(?:j'ai\s+)?dépensé\s+([0-9]+(?:[.,][0-9]+)?)\s*(?:fcfa|f|francs)?\s*(.*)",
            r"(?:j'ai\s+)?payé\s+([0-9]+(?:[.,][0-9]+)?)\s*(?:fcfa|f|francs)?\s*(.*)",
            r"dépense\s+([0-9]+(?:[.,][0-9]+)?)\s*(?:fcfa|f|francs)?\s*(.*)",
        ]

        for pattern in expense_patterns:

            match = re.search(pattern, text)

            if not match:
                continue

            amount = float(
                match.group(1).replace(",", ".")
            )

            description = match.group(2).strip()

            description = description.rstrip(
                " ?!.,;:"
            )

            expense_data = ExpenseIntentData(
                amount=amount,
                category=None,
                description=description or None,
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
            r"(?:j'ai\s+)?vendu\s+([0-9]+(?:[.,][0-9]+)?)\s+(?:sac|sacs|kg|kilo|kilos|litre|litres|unité|unités)\s+(?:de\s+)?(.+)",

            # Exemple :
            # "j'ai vendu 2 riz"
            r"(?:j'ai\s+)?vendu\s+([0-9]+(?:[.,][0-9]+)?)\s+(.+)",

            # Exemple Wolof :
            # "mun naa ceeb 2 kilos"
            r"(?:mun naa|maa ngi)\s+(.+?)\s+([0-9]+(?:[.,][0-9]+)?)\s+(kilo|kilos|kg|sac|sacs|litre|litres)",
        ]

        for index, pattern in enumerate(sale_patterns):

            match = re.search(pattern, text)

            if not match:
                continue

            if index == 2:

                # Format Wolof :
                # produit + quantité + unité

                product_name = match.group(1).strip()

                quantity = float(
                    match.group(2).replace(",", ".")
                )

                unit = match.group(3)

            else:

                # Format français :
                # quantité + unité + produit

                quantity = float(
                    match.group(1).replace(",", ".")
                )

                if index == 0:

                    unit = re.search(
                        r"[0-9]+(?:[.,][0-9]+)?\s+(sac|sacs|kg|kilo|kilos|litre|litres|unité|unités)",
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

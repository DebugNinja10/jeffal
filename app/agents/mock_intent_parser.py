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

        text = text.strip().lower().replace("’", "'")

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
            # Français :
            # "j'ai vendu 2 sacs de riz"
            r"(?:j'ai\s+)?vendu\s+([0-9]+(?:[.,][0-9]+)?)\s+(sacs?|kg|kilos?|litres?|unités?|bidons?)\s+(?:de\s+)?(?:l'|la\s+|le\s+|du\s+|des\s+)?(.+)",

            # Français :
            # "j'ai vendu 2 riz"
            r"(?:j'ai\s+)?vendu\s+([0-9]+(?:[.,][0-9]+)?)\s+(.+)",

            # Wolof :
            # "mun naa ceeb 2 kilos"
            r"(?:mun naa|maa ngi)\s+(.+?)\s+([0-9]+(?:[.,][0-9]+)?)\s+(kilo|kilos|kg|sac|sacs|litre|litres)",
        ]

        for index, pattern in enumerate(sale_patterns):

            match = re.search(pattern, text)

            if not match:
                continue

            # --------------------------------------------------------
            # Trouver tous les blocs séparés par " et "
            # --------------------------------------------------------

            if index in (0, 1):

                prefix_match = re.match(
                    r"(?:j'ai\s+)?vendu\s+",
                    text,
                )

                if prefix_match is None:
                    continue

                sale_text = text[prefix_match.end():]

                parts = re.split(
                    r"\s+et\s+",
                    sale_text,
                )

                items = []

                valid = True

                for part in parts:

                    part = part.strip()

                    if not part:
                        valid = False
                        break

                    if index == 0:

                        item_match = re.fullmatch(
                            r"([0-9]+(?:[.,][0-9]+)?)\s+"
                            r"(sacs?|kg|kilos?|litres?|unités?|bidons?)\s+"
                            r"(?:de\s+(?:l'|la\s+|le\s+|du\s+|des\s+)?|d')?"
                            r"(.+)",
                            part,
                        )

                        if item_match is None:
                            valid = False
                            break

                        quantity = float(
                            item_match.group(1).replace(",", ".")
                        )

                        unit = item_match.group(2)

                        product_name = item_match.group(3).strip()

                    else:

                        item_match = re.fullmatch(
                            r"([0-9]+(?:[.,][0-9]+)?)\s+(.+)",
                            part,
                        )

                        if item_match is None:
                            valid = False
                            break

                        quantity = float(
                            item_match.group(1).replace(",", ".")
                        )

                        product_name = item_match.group(2).strip()
                        unit = None

                    product_name = product_name.rstrip(
                        " ?!.,;:"
                    )

                    if not product_name:
                        valid = False
                        break

                    items.append(
                        {
                            "product_name": product_name,
                            "quantity": quantity,
                            "unit": unit,
                        }
                    )

                if not valid or not items:
                    continue

                sale_data = SaleIntentData(
                    items=items,
                    payment_method=None,
                )

                return AgentUnderstanding(
                    intent=IntentName.ENREGISTRER_VENTE,
                    data=sale_data.model_dump(),
                    confidence=0.90,
                    needs_clarification=False,
                )

            # --------------------------------------------------------
            # Format Wolof
            # --------------------------------------------------------

            else:

                product_name = match.group(1).strip()

                quantity = float(
                    match.group(2).replace(",", ".")
                )

                unit = match.group(3)

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

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
        # RAPPORT D'ACTIVITÉ
        # ============================================================

        report_keywords = [
            "rapport",
            "chiffre d'affaires",
            "chiffre d affaire",
            "ca",
            "résume mon activité",
            "resume mon activite",
        ]

        if any(keyword in text for keyword in report_keywords):
            if any(
                phrase in text
                for phrase in [
                    "aujourd'hui",
                    "aujourd’hui",
                    "du jour",
                    "de la journée",
                ]
            ):
                period = "day"
            elif any(
                phrase in text
                for phrase in [
                    "semaine",
                    "cette semaine",
                    "la semaine",
                    "semaine dernière",
                ]
            ):
                period = "week"
            else:
                period = "month"

            return AgentUnderstanding(
                intent=IntentName.ANALYSER_ACTIVITE,
                data={
                    "period": period,
                },
                confidence=0.90,
                needs_clarification=False,
            )

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

        # --------------------------------------------------------
        # Format Wolof
        # --------------------------------------------------------

        wolof_prefix = re.match(
            r"(?:mun naa|maa ngi)\s+",
            text,
        )

        if wolof_prefix:
            sale_text = text[wolof_prefix.end():].strip()

            noise_words = {
                "tamit",
                "liibar",
            }

            tokens = [
                token
                for token in sale_text.split()
                if token.lower() not in noise_words
            ]

            number_words = {
                "benn": 1.0,
                "genn": 1.0,
            }

            unit_words = {
                "kilo": "kilo",
                "kilos": "kilos",
                "kg": "kg",
                "sac": "sac",
                "sacs": "sacs",
                "litre": "litre",
                "litres": "litres",
            }

            items = []
            current = []
            i = 0

            while i < len(tokens):
                token = tokens[i]
                lower = token.lower()

                if lower == "ak":
                    # "ak genn wàll" / "ak benn wàll"
                    # après une unité = +0,5 à l'article précédent.
                    if (
                        i + 2 < len(tokens)
                        and tokens[i + 1].lower() in {"benn", "genn"}
                        and tokens[i + 2].lower() == "wàll"
                        and items
                    ):
                        items[-1]["quantity"] += 0.5
                        i += 3
                        continue

                    # "ak" seul entre deux articles = séparateur.
                    if not current:
                        i += 1
                        continue

                    i += 1
                    continue

                if lower not in unit_words:
                    current.append(token)
                    i += 1
                    continue

                unit = unit_words[lower]

                quantity = 1.0

                if current:
                    last = current[-1].lower()

                    if last in number_words:
                        quantity = number_words[last]
                        current.pop()

                    elif re.fullmatch(
                        r"[0-9]+(?:[.,][0-9]+)?",
                        last,
                    ):
                        quantity = float(last.replace(",", "."))
                        current.pop()

                if not current:
                    return AgentUnderstanding(
                        intent=IntentName.ENREGISTRER_VENTE,
                        data={},
                        confidence=0.50,
                        needs_clarification=True,
                    )

                product_name = " ".join(current).strip()

                items.append(
                    {
                        "product_name": product_name.rstrip(
                            " ?!.,;:"
                        ),
                        "quantity": quantity,
                        "unit": unit,
                    }
                )

                current = []
                i += 1

            if current:
                return AgentUnderstanding(
                    intent=IntentName.ENREGISTRER_VENTE,
                    data={},
                    confidence=0.50,
                    needs_clarification=True,
                )

            if items:
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
        # Formats français
        # --------------------------------------------------------

        sale_patterns = [
            r"(?:j'ai\\s+)?vendu\\s+([0-9]+(?:[.,][0-9]+)?)\\s+(sacs?|kg|kilos?|litres?|unités?|bidons?)\\s+(?:de\\s+)?(?:l'|la\\s+|le\\s+|du\\s+|des\\s+)?(.+)",
            r"(?:j'ai\\s+)?vendu\\s+([0-9]+(?:[.,][0-9]+)?)\\s+(.+)",
        ]

        for index, pattern in enumerate(sale_patterns):

            match = re.search(pattern, text)

            if not match:
                continue

            prefix_match = re.match(
                r"(?:j'ai\\s+)?vendu\\s+",
                text,
            )

            if prefix_match is None:
                continue

            sale_text = text[prefix_match.end():]

            parts = re.split(
                r"\\s+et\\s+",
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
                        r"([0-9]+(?:[.,][0-9]+)?)\\s+"
                        r"(sacs?|kg|kilos?|litres?|unités?|bidons?)\\s+"
                        r"(?:de\\s+(?:l'|la\\s+|le\\s+|du\\s+|des\\s+)?|d')?"
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
                        r"([0-9]+(?:[.,][0-9]+)?)\\s+(.+)",
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

        # ============================================================
        # INTENT INCONNUE
        # ============================================================

        return AgentUnderstanding(
            intent=IntentName.UNKNOWN,
            data={},
            confidence=0.0,
            needs_clarification=True,
        )

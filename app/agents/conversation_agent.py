from sqlalchemy.orm import Session

from app.agents.action_executor import ActionExecutor
from app.services.product_service import create_product, find_business_product_by_name
from app.services.conversation_service import update_conversation


class ConversationAgent:
    """
    Gère progressivement les conversations multi-étapes de JËFAL.

    Ce service sera utilisé pour sortir la logique conversationnelle
    du routeur FastAPI.
    """

    def __init__(self, action_executor: ActionExecutor):
        self.action_executor = action_executor

    def handle(
        self,
        db: Session,
        conversation,
        business_id: int,
        message: str,
    ):
        """
        Traite un message en fonction de l'état actuel
        de la conversation.

        Retourne None si cet état n'est pas encore géré ici.
        """

        normalized_message = message.strip().lower()

        if conversation.state == "waiting_product_confirmation":
            return self._handle_product_confirmation(
                db=db,
                conversation=conversation,
                normalized_message=normalized_message,
            )

        if conversation.state == "waiting_item_type":
            return self._handle_item_type(
                db=db,
                conversation=conversation,
                normalized_message=normalized_message,
            )

        if conversation.state == "waiting_product_purchase_price":
            return self._handle_product_purchase_price(
                db=db,
                conversation=conversation,
                normalized_message=normalized_message,
            )

        if conversation.state == "waiting_product_selling_price":
            return self._handle_product_selling_price(
                db=db,
                conversation=conversation,
                normalized_message=normalized_message,
            )

        if conversation.state == "waiting_product_unit":
            return self._handle_product_unit(
                db=db,
                conversation=conversation,
                normalized_message=normalized_message,
            )

        if conversation.state == "waiting_product_base_unit":
            return self._handle_product_base_unit(
                db=db,
                conversation=conversation,
                normalized_message=normalized_message,
            )

        if conversation.state == "waiting_product_package_size":
            return self._handle_product_package_size(
                db=db,
                conversation=conversation,
                normalized_message=normalized_message,
            )

        if conversation.state == "waiting_product_initial_stock":
            return self._handle_product_initial_stock(
                db=db,
                conversation=conversation,
                normalized_message=normalized_message,
            )

        if conversation.state == "product_ready_to_create":
            return self._handle_product_ready_to_create(
                db=db,
                conversation=conversation,
                business_id=business_id,
            )

        if conversation.state == "product_created":
            return self._handle_product_created(
                db=db,
                conversation=conversation,
                business_id=business_id,
            )

        return None

    def _handle_product_confirmation(
        self,
        db: Session,
        conversation,
        normalized_message: str,
    ):
        if normalized_message in {
            "oui",
            "oui.",
            "yes",
            "d'accord",
            "daccord",
            "waaw",
            "waaw.",
        }:
            missing_product = conversation.context.get(
                "missing_product"
            )

            update_conversation(
                db=db,
                conversation=conversation,
                state="waiting_item_type",
                context={
                    **conversation.context,
                    "missing_product": missing_product,
                },
            )

            return {
                "needs_clarification": True,
                "result": {
                    "missing_product": missing_product,
                    "step": "item_type",
                },
                "message": (
                    f"D'accord. Ajoutons '{missing_product}'. "
                    "Est-ce un produit ou un service ?"
                ),
            }

        if normalized_message in {"non", "non."}:
            update_conversation(
                db=db,
                conversation=conversation,
                state="idle",
                context={},
            )

            return {
                "needs_clarification": True,
                "result": None,
                "message": "D'accord, je n'ajoute pas ce produit.",
            }

        return {
            "needs_clarification": True,
            "result": None,
            "message": "Répondez par oui ou non.",
        }

    def _handle_item_type(
        self,
        db: Session,
        conversation,
        normalized_message: str,
    ):
        if normalized_message in {
            "produit",
            "product",
        }:
            context = {
                **conversation.context,
                "item_type": "product",
            }

            update_conversation(
                db=db,
                conversation=conversation,
                state="waiting_product_purchase_price",
                context=context,
            )

            missing_product = context.get("missing_product")

            return {
                "needs_clarification": True,
                "result": {
                    "missing_product": missing_product,
                    "item_type": "product",
                    "step": "purchase_price",
                },
                "message": (
                    f"'{missing_product}' est enregistré comme produit. "
                    "Quel est son prix d'achat ?"
                ),
            }

        if normalized_message in {
            "service",
            "prestation",
        }:
            context = {
                **conversation.context,
                "item_type": "service",
            }

            update_conversation(
                db=db,
                conversation=conversation,
                state="waiting_product_selling_price",
                context=context,
            )

            missing_product = context.get("missing_product")

            return {
                "needs_clarification": True,
                "result": {
                    "missing_product": missing_product,
                    "item_type": "service",
                    "step": "selling_price",
                },
                "message": (
                    f"'{missing_product}' est enregistré comme service. "
                    "Quel est son prix de vente ?"
                ),
            }

        return {
            "needs_clarification": True,
            "result": None,
            "message": (
                "Répondez simplement par « produit » "
                "ou « service »."
            ),
        }

    def _handle_product_unit(
        self,
        db: Session,
        conversation,
        normalized_message: str,
    ):
        from app.services.unit_service import normalize_unit

        try:
            unit = normalize_unit(normalized_message)
        except (AttributeError, TypeError):
            unit = ""

        if not unit:
            return {
                "needs_clarification": True,
                "result": None,
                "message": (
                    "Je n'ai pas compris l'unité. "
                    "Exemples : kg, sac, bidon, litre ou unité."
                ),
            }

        context = {
            **conversation.context,
            "unit": unit,
        }

        update_conversation(
            db=db,
            conversation=conversation,
            state="waiting_product_base_unit",
            context=context,
        )

        missing_product = context.get("missing_product")

        return {
            "needs_clarification": True,
            "result": {
                "missing_product": missing_product,
                "unit": unit,
                "step": "base_unit",
            },
            "message": (
                f"Unité de vente enregistrée : {unit}. "
                "Quelle est l'unité utilisée pour gérer le stock ?"
            ),
        }

    def _handle_product_base_unit(
        self,
        db: Session,
        conversation,
        normalized_message: str,
    ):
        from app.services.unit_service import normalize_unit

        try:
            base_unit = normalize_unit(normalized_message)
        except (AttributeError, TypeError):
            base_unit = ""

        if not base_unit:
            return {
                "needs_clarification": True,
                "result": None,
                "message": (
                    "Je n'ai pas compris l'unité de stock. "
                    "Exemples : kg, sac, bidon, litre ou unité."
                ),
            }

        context = {
            **conversation.context,
            "base_unit": base_unit,
        }

        unit = normalize_unit(context.get("unit", ""))

        if unit == base_unit:
            context["package_size"] = None

            update_conversation(
                db=db,
                conversation=conversation,
                state="waiting_product_initial_stock",
                context=context,
            )

            missing_product = context.get("missing_product")

            return {
                "needs_clarification": True,
                "result": {
                    "missing_product": missing_product,
                    "unit": unit,
                    "base_unit": base_unit,
                    "package_size": None,
                    "step": "initial_stock",
                },
                "message": (
                    f"Les unités sont identiques ({base_unit}). "
                    "Combien en avez-vous actuellement en stock ?"
                ),
            }

        update_conversation(
            db=db,
            conversation=conversation,
            state="waiting_product_package_size",
            context=context,
        )

        missing_product = context.get("missing_product")

        return {
            "needs_clarification": True,
            "result": {
                "missing_product": missing_product,
                "unit": unit,
                "base_unit": base_unit,
                "step": "package_size",
            },
            "message": (
                f"Unité de vente : {unit}. "
                f"Unité de stock : {base_unit}. "
                f"Quelle quantité de {base_unit} contient un {unit} ?"
            ),
        }

    def _handle_product_ready_to_create(
        self,
        db: Session,
        conversation,
        business_id: int,
    ):
        context = conversation.context

        missing_product = context.get("missing_product")
        item_type = context.get("item_type", "product")
        purchase_price = context.get("purchase_price")
        selling_price = context.get("selling_price")
        unit = context.get("unit")
        base_unit = context.get("base_unit")
        package_size = context.get("package_size")
        initial_stock = context.get("initial_stock")

        required_values = (
            missing_product,
            item_type,
            selling_price,
            unit,
            base_unit,
            initial_stock,
        )

        if any(value is None for value in required_values):
            update_conversation(
                db=db,
                conversation=conversation,
                state="idle",
                context={},
            )

            return {
                "needs_clarification": True,
                "result": None,
                "message": (
                    "Il manque des informations pour créer le produit. "
                    "Veuillez recommencer l'opération."
                ),
            }

        if item_type == "product" and purchase_price is None:
            update_conversation(
                db=db,
                conversation=conversation,
                state="idle",
                context={},
            )

            return {
                "needs_clarification": True,
                "result": None,
                "message": (
                    "Il manque le prix d'achat du produit. "
                    "Veuillez recommencer l'opération."
                ),
            }

        if unit == base_unit:
            base_stock = initial_stock
            package_size = None
        else:
            if package_size is None:
                update_conversation(
                    db=db,
                    conversation=conversation,
                    state="idle",
                    context={},
                )

                return {
                    "needs_clarification": True,
                    "result": None,
                    "message": (
                        "Il manque la quantité du conditionnement "
                        "pour convertir le stock."
                    ),
                }

            base_stock = initial_stock * package_size

        existing_product = find_business_product_by_name(
            db=db,
            product_name=missing_product,
            business_id=business_id,
        )

        if existing_product is not None:
            return {
                "needs_clarification": True,
                "result": {
                    "product_id": existing_product.id,
                    "product_name": existing_product.name,
                },
                "message": (
                    f"L'article '{missing_product}' existe déjà."
                ),
            }

        product = create_product(
            db=db,
            business_id=business_id,
            name=missing_product,
            category=None,
            item_type=item_type,
            unit=unit,
            base_unit=base_unit,
            package_size=package_size,
            purchase_price=(
                purchase_price if purchase_price is not None else 0
            ),
            selling_price=selling_price,
            stock_quantity=base_stock,
        )

        update_conversation(
            db=db,
            conversation=conversation,
            state="product_created",
            context={
                **context,
                "product_id": product.id,
                "base_stock": base_stock,
                "package_size": package_size,
            },
        )

        return {
            "needs_clarification": True,
            "result": {
                "product_id": product.id,
                "product_name": product.name,
                "item_type": product.item_type,
                "unit": product.unit,
                "base_unit": product.base_unit,
                "package_size": (
                    float(product.package_size)
                    if product.package_size is not None
                    else None
                ),
                "initial_stock": initial_stock,
                "base_stock": base_stock,
            },
            "message": (
                f"Article '{product.name}' créé avec "
                f"{initial_stock:g} {unit} en stock."
                " La vente en attente peut maintenant être reprise."
            ),
        }

    def _handle_product_created(
        self,
        db: Session,
        conversation,
        business_id: int,
    ):
        from app.agents.intents import IntentName
        from app.agents.schemas import AgentUnderstanding

        context = conversation.context
        pending_items = context.get("pending_items", [])

        if not pending_items:
            update_conversation(
                db=db,
                conversation=conversation,
                state="idle",
                context={},
            )

            return {
                "needs_clarification": True,
                "result": None,
                "message": (
                    "Le produit a été créé, mais aucune vente "
                    "en attente n'a été retrouvée."
                ),
            }

        understanding = AgentUnderstanding(
            intent=IntentName.ENREGISTRER_VENTE,
            data={
                "items": pending_items,
                "payment_method": None,
            },
            confidence=1.0,
            needs_clarification=False,
        )

        try:
            result = self.action_executor.execute(
                db=db,
                business_id=business_id,
                understanding=understanding,
            )

        except ValueError as exc:
            return {
                "needs_clarification": False,
                "result": None,
                "message": str(exc),
            }

        update_conversation(
            db=db,
            conversation=conversation,
            state="idle",
            context={},
        )

        return {
            "needs_clarification": False,
            "result": result,
            "message": (
                "Produit créé et vente en attente "
                "enregistrée avec succès."
            ),
        }

    def _handle_product_initial_stock(
        self,
        db: Session,
        conversation,
        normalized_message: str,
    ):
        try:
            value = normalized_message.strip().lower().replace(",", ".")
            unit = conversation.context.get("unit", "")

            for suffix in (
                "prestations",
                "prestation",
                "unités",
                "unité",
                "unites",
                "unite",
                "sacs",
                "sac",
                "bidons",
                "bidon",
                "kilos",
                "kilo",
                "kg",
                "litres",
                "litre",
                "l",
            ):
                if value.endswith(suffix):
                    value = value[:-len(suffix)].strip()
                    break

            initial_stock = float(value)
        except ValueError:
            return {
                "needs_clarification": True,
                "result": None,
                "message": (
                    f"Je n'ai pas compris la quantité. "
                    f"Donnez-moi uniquement le nombre de {unit or 'unités'}, "
                    "par exemple : 10."
                ),
            }

        if initial_stock <= 0:
            return {
                "needs_clarification": True,
                "result": None,
                "message": (
                    "Le stock initial doit être supérieur à zéro."
                ),
            }

        context = {
            **conversation.context,
            "initial_stock": initial_stock,
        }

        update_conversation(
            db=db,
            conversation=conversation,
            state="product_ready_to_create",
            context=context,
        )

        missing_product = context.get("missing_product")

        return {
            "needs_clarification": False,
            "result": {
                "missing_product": missing_product,
                "item_type": context.get("item_type", "product"),
                "purchase_price": context.get("purchase_price"),
                "selling_price": context.get("selling_price"),
                "unit": context.get("unit"),
                "base_unit": context.get("base_unit"),
                "package_size": context.get("package_size"),
                "initial_stock": initial_stock,
                "step": "ready_to_create",
            },
            "message": (
                f"Parfait. J'ai toutes les informations pour "
                f"ajouter '{missing_product}'."
            ),
        }

    def _handle_product_package_size(
        self,
        db: Session,
        conversation,
        normalized_message: str,
    ):
        try:
            value = normalized_message.strip().lower().replace(",", ".")
            unit = conversation.context.get("unit", "")
            base_unit = conversation.context.get("base_unit", "")

            for suffix in (
                "prestations",
                "prestation",
                "unités",
                "unites",
                "sacs",
                "sac",
                "bidons",
                "bidon",
                "kilos",
                "kilo",
                "kg",
                "litres",
                "litre",
                "l",
            ):
                if value.endswith(suffix):
                    value = value[:-len(suffix)].strip()
                    break

            package_size = float(value)
        except ValueError:
            return {
                "needs_clarification": True,
                "result": None,
                "message": (
                    f"Je n'ai pas compris la quantité. "
                    f"Donnez-moi uniquement le nombre de {base_unit or 'unités'}, "
                    "par exemple : 25."
                ),
            }

        if package_size <= 0:
            return {
                "needs_clarification": True,
                "result": None,
                "message": (
                    "La quantité du conditionnement doit être "
                    "supérieure à zéro."
                ),
            }

        context = {
            **conversation.context,
            "package_size": package_size,
        }

        update_conversation(
            db=db,
            conversation=conversation,
            state="waiting_product_initial_stock",
            context=context,
        )

        missing_product = context.get("missing_product")

        return {
            "needs_clarification": True,
            "result": {
                "missing_product": missing_product,
                "unit": unit,
                "base_unit": base_unit,
                "package_size": package_size,
                "step": "initial_stock",
            },
            "message": (
                f"Conditionnement enregistré : "
                f"un {unit} contient {package_size:g} {base_unit}. "
                f"Combien de {unit} avez-vous actuellement en stock ?"
            ),
        }

    def _handle_product_selling_price(
        self,
        db: Session,
        conversation,
        normalized_message: str,
    ):
        try:
            selling_price = float(
                normalized_message.replace(",", ".")
            )
        except ValueError:
            return {
                "needs_clarification": True,
                "result": None,
                "message": (
                    "Je n'ai pas compris le prix de vente. "
                    "Donnez-moi uniquement le montant, "
                    "par exemple : 15000."
                ),
            }

        if selling_price <= 0:
            return {
                "needs_clarification": True,
                "result": None,
                "message": (
                    "Le prix de vente doit être supérieur à zéro."
                ),
            }

        context = {
            **conversation.context,
            "selling_price": selling_price,
        }

        if context.get("item_type") == "service":
            missing_product = context.get("missing_product")

            existing_product = find_business_product_by_name(
                db=db,
                product_name=missing_product,
                business_id=conversation.business_id,
            )

            if existing_product is not None:
                update_conversation(
                    db=db,
                    conversation=conversation,
                    state="idle",
                    context={},
                )

                return {
                    "needs_clarification": True,
                    "result": {
                        "product_id": existing_product.id,
                        "product_name": existing_product.name,
                    },
                    "message": (
                        f"L'article '{missing_product}' existe déjà."
                    ),
                }

            service = create_product(
                db=db,
                business_id=conversation.business_id,
                name=missing_product,
                category=None,
                item_type="service",
                unit="prestation",
                base_unit="prestation",
                package_size=None,
                purchase_price=0,
                selling_price=selling_price,
                stock_quantity=0,
            )

            update_conversation(
                db=db,
                conversation=conversation,
                state="product_created",
                context={
                    **context,
                    "product_id": service.id,
                },
            )

            return {
                "needs_clarification": False,
                "result": {
                    "product_id": service.id,
                    "product_name": service.name,
                    "item_type": service.item_type,
                    "unit": service.unit,
                    "selling_price": float(service.selling_price),
                },
                "message": (
                    f"Service '{service.name}' créé avec succès. "
                    "La vente en attente peut maintenant être reprise."
                ),
            }

        update_conversation(
            db=db,
            conversation=conversation,
            state="waiting_product_unit",
            context=context,
        )

        missing_product = context.get("missing_product")

        return {
            "needs_clarification": True,
            "result": {
                "missing_product": missing_product,
                "purchase_price": context.get("purchase_price"),
                "selling_price": selling_price,
                "step": "unit",
            },
            "message": (
                f"Prix de vente enregistré : "
                f"{selling_price:g} FCFA. "
                "Quelle unité utilisez-vous pour vendre ? "
                "Par exemple : kg, sac, bidon, litre ou unité."
            ),
        }

    def _handle_product_purchase_price(
        self,
        db: Session,
        conversation,
        normalized_message: str,
    ):
        try:
            purchase_price = float(
                normalized_message.replace(",", ".")
            )
        except ValueError:
            return {
                "needs_clarification": True,
                "result": None,
                "message": (
                    "Je n'ai pas compris le prix d'achat. "
                    "Donnez-moi uniquement le montant, "
                    "par exemple : 10000."
                ),
            }

        if purchase_price <= 0:
            return {
                "needs_clarification": True,
                "result": None,
                "message": (
                    "Le prix d'achat doit être supérieur à zéro."
                ),
            }

        context = {
            **conversation.context,
            "purchase_price": purchase_price,
        }

        update_conversation(
            db=db,
            conversation=conversation,
            state="waiting_product_selling_price",
            context=context,
        )

        missing_product = context.get("missing_product")

        return {
            "needs_clarification": True,
            "result": {
                "missing_product": missing_product,
                "purchase_price": purchase_price,
                "step": "selling_price",
            },
            "message": (
                f"Prix d'achat enregistré : "
                f"{purchase_price:g} FCFA. "
                "Quel est son prix de vente ?"
            ),
        }

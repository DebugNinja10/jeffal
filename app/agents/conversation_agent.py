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
        }:
            missing_product = conversation.context.get(
                "missing_product"
            )

            update_conversation(
                db=db,
                conversation=conversation,
                state="waiting_product_purchase_price",
                context={
                    **conversation.context,
                    "missing_product": missing_product,
                },
            )

            return {
                "needs_clarification": True,
                "result": {
                    "missing_product": missing_product,
                    "step": "purchase_price",
                },
                "message": (
                    f"D'accord. Ajoutons le produit "
                    f"'{missing_product}'. "
                    "Quel est son prix d'achat ?"
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

    def _handle_product_ready_to_create(
        self,
        db: Session,
        conversation,
        business_id: int,
    ):
        context = conversation.context

        missing_product = context.get("missing_product")
        purchase_price = context.get("purchase_price")
        selling_price = context.get("selling_price")
        package_size = context.get("package_size")
        initial_stock = context.get("initial_stock")

        if not all(
            value is not None
            for value in (
                missing_product,
                purchase_price,
                selling_price,
                package_size,
                initial_stock,
            )
        ):
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
                    f"Le produit '{missing_product}' existe déjà."
                ),
            }

        product = create_product(
            db=db,
            business_id=business_id,
            name=missing_product,
            category=None,
            unit="bidon",
            base_unit="litre",
            package_size=package_size,
            purchase_price=purchase_price,
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
            },
        )

        return {
            "needs_clarification": True,
            "result": {
                "product_id": product.id,
                "product_name": product.name,
                "unit": product.unit,
                "base_unit": product.base_unit,
                "package_size": float(product.package_size),
                "initial_stock": initial_stock,
                "base_stock": base_stock,
            },
            "message": (
                f"Produit '{product.name}' créé avec "
                f"{initial_stock:g} bidons en stock. "
                "La vente en attente peut maintenant être reprise."
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
            initial_stock = float(
                normalized_message.replace(",", ".")
            )
        except ValueError:
            return {
                "needs_clarification": True,
                "result": None,
                "message": (
                    "Je n'ai pas compris la quantité. "
                    "Donnez-moi uniquement le nombre de bidons, "
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
                "purchase_price": context.get("purchase_price"),
                "selling_price": context.get("selling_price"),
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
            value = value.removesuffix("litres").removesuffix("litre").removesuffix("l").strip()
            package_size = float(value)
        except ValueError:
            return {
                "needs_clarification": True,
                "result": None,
                "message": (
                    "Je n'ai pas compris la contenance. "
                    "Donnez-moi uniquement le nombre de litres, "
                    "par exemple : 20."
                ),
            }

        if package_size <= 0:
            return {
                "needs_clarification": True,
                "result": None,
                "message": (
                    "La contenance doit être supérieure à zéro."
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
                "package_size": package_size,
                "step": "initial_stock",
            },
            "message": (
                f"Contenance enregistrée : "
                f"{package_size:g} litres par bidon. "
                "Combien de bidons avez-vous actuellement en stock ?"
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
                "purchase_price": context.get("purchase_price"),
                "selling_price": selling_price,
                "step": "package_size",
            },
            "message": (
                f"Prix de vente enregistré : "
                f"{selling_price:g} FCFA. "
                "Combien de litres contient un bidon ?"
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

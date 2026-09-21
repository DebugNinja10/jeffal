from sqlalchemy.orm import Session

from app.agents.intents import IntentName
from app.agents.schemas import AgentUnderstanding
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.services.product_service import find_business_product_by_name
from app.services.sale_service import create_sale


class ActionExecutor:

    def execute(
        self,
        db: Session,
        business_id: int,
        understanding: AgentUnderstanding,
    ):
        if understanding.intent == IntentName.ENREGISTRER_VENTE:
            return self._execute_sale(
                db=db,
                business_id=business_id,
                understanding=understanding,
            )

        raise ValueError(
            f"Intent non supportée : "
            f"{understanding.intent}"
        )

    def _execute_sale(
        self,
        db: Session,
        business_id: int,
        understanding: AgentUnderstanding,
    ):
        items = understanding.data["items"]

        sale_items = []

        for item in items:
            product = find_business_product_by_name(
                db=db,
                product_name=item["product_name"],
                business_id=business_id,
            )

            if product is None:
                raise ValueError(
                    f"Produit introuvable : "
                    f"'{item['product_name']}'."
                )

            sale_items.append(
                SaleItemCreate(
                    product_id=product.id,
                    quantity=item["quantity"],
                )
            )

        sale_data = SaleCreate(
            payment_method=(
                understanding.data.get("payment_method")
                or "especes"
            ),
            items=sale_items,
        )

        return create_sale(
            db=db,
            business_id=business_id,
            sale_data=sale_data,
        )

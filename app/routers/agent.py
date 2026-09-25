from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.agents.action_executor import ActionExecutor
from app.agents.agent_service import AgentService
from app.agents.conversation_agent import ConversationAgent
from app.agents.mock_intent_parser import MockIntentParser
from app.auth.dependencies import get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.schemas.agent import AgentRequest, AgentResponse
from app.services.business_service import get_user_business
from app.services.conversation_service import (
    create_conversation,
    get_conversation,
    update_conversation,
)


router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)


agent_service = AgentService(
    MockIntentParser()
)

action_executor = ActionExecutor()
conversation_agent = ConversationAgent(action_executor)


@router.post(
    "/execute",
    response_model=AgentResponse,
)
def execute_agent(
    request: AgentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    business = get_user_business(
        db=db,
        business_id=request.business_id,
        user_id=current_user.id,
    )

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activité introuvable.",
        )

    # ------------------------------------------------------------
    # CONVERSATION
    # ------------------------------------------------------------

    if request.conversation_id is None:

        conversation = create_conversation(
            db=db,
            user_id=current_user.id,
            business_id=business.id,
        )

    else:

        conversation = get_conversation(
            db=db,
            conversation_id=request.conversation_id,
            user_id=current_user.id,
            business_id=business.id,
        )

        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation introuvable.",
            )

    # ------------------------------------------------------------
    # GESTION DE LA CONVERSATION EN COURS
    # ------------------------------------------------------------

    normalized_message = request.message.strip().lower()

    conversation_result = conversation_agent.handle(
        db=db,
        conversation=conversation,
        business_id=request.business_id,
        message=request.message,
    )

    if conversation_result is not None:
        return AgentResponse(
            intent="conversation",
            confidence=1.0,
            needs_clarification=conversation_result["needs_clarification"],
            result=conversation_result["result"],
            message=conversation_result["message"],
            conversation_id=conversation.conversation_id,
        )

    # ------------------------------------------------------------
    # COMPRÉHENSION
    # ------------------------------------------------------------

    understanding = agent_service.understand(
        request.message
    )

    if understanding.needs_clarification:
        return AgentResponse(
            intent=understanding.intent.value,
            confidence=understanding.confidence,
            needs_clarification=True,
            result=understanding.data or None,
            message=(
                "Je n'ai pas suffisamment compris "
                "votre demande."
            ),
            conversation_id=conversation.conversation_id,
        )

    # ------------------------------------------------------------
    # EXÉCUTION
    # ------------------------------------------------------------

    try:

        result = action_executor.execute(
            db=db,
            business_id=business.id,
            understanding=understanding,
        )

        if (
            understanding.intent.value == "enregistrer_vente"
            and isinstance(result, dict)
            and result.get("needs_clarification")
            and result.get("reason") == "product_not_found"
        ):
            update_conversation(
                db=db,
                conversation=conversation,
                state="waiting_product_confirmation",
                context={
                    "reason": result["reason"],
                    "missing_product": result["product_name"],
                    "pending_items": result["pending_items"],
                },
            )

            return AgentResponse(
                intent=understanding.intent.value,
                confidence=understanding.confidence,
                needs_clarification=True,
                result=result,
                message=(
                    f"Je ne trouve pas le produit "
                    f"'{result['product_name']}'. "
                    "Voulez-vous l'ajouter ?"
                ),
                conversation_id=conversation.conversation_id,
            )

    except ValueError as exc:

        return AgentResponse(
            intent=understanding.intent.value,
            confidence=understanding.confidence,
            needs_clarification=False,
            result=None,
            message=str(exc),
            conversation_id=conversation.conversation_id,
        )

    # ------------------------------------------------------------
    # RÉPONSE
    # ------------------------------------------------------------

    if (
        understanding.intent.value
        == "consulter_stock"
    ):
        quantity = float(result["stock_quantity"])
        unit = result["unit"]
        product_name = result["product_name"]

        if quantity == 1:
            quantity_text = "1"
            unit_text = unit.rstrip("s")
        else:
            quantity_text = f"{quantity:g}"
            unit_text = unit if unit.endswith("s") else f"{unit}s"

        if product_name[0].lower() in "aeiouh":
            product_text = f"d’{product_name}"
        else:
            product_text = f"de {product_name}"

        message = (
            f"Il vous reste "
            f"{quantity_text} "
            f"{unit_text} "
            f"{product_text}."
        )

    else:
        message = "Action exécutée avec succès."

    return AgentResponse(
        intent=understanding.intent.value,
        confidence=understanding.confidence,
        needs_clarification=False,
        result=result,
        message=message,
        conversation_id=conversation.conversation_id,
    )

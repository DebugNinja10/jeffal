from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.schemas.agent import AgentRequest, AgentResponse
from app.services.business_service import get_user_business

from app.agents.agent_service import AgentService
from app.agents.action_executor import ActionExecutor
from app.agents.mock_intent_parser import MockIntentParser


router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)


agent_service = AgentService(
    MockIntentParser()
)

action_executor = ActionExecutor()


@router.post(
    "/execute",
    response_model=AgentResponse,
)
def execute_agent(
    request: AgentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Vérifier que l'activité appartient
    # bien à l'utilisateur connecté.
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

    # Comprendre le message utilisateur.
    understanding = agent_service.understand(
        request.message
    )

    # Si l'agent ne comprend pas la demande,
    # on ne lance aucune action.
    if understanding.needs_clarification:
        return AgentResponse(
            intent=understanding.intent.value,
            confidence=understanding.confidence,
            needs_clarification=True,
            result=None,
            message=(
                "Je n'ai pas suffisamment compris "
                "votre demande."
            ),
        )

    try:
        result = action_executor.execute(
            db=db,
            business_id=business.id,
            understanding=understanding,
        )

    except ValueError as exc:
        return AgentResponse(
            intent=understanding.intent.value,
            confidence=understanding.confidence,
            needs_clarification=False,
            result=None,
            message=str(exc),
        )

    # Réponse spécifique à la consultation du stock.
    if (
        understanding.intent.value
        == "consulter_stock"
    ):
        message = (
            f"Il vous reste "
            f"{result['stock_quantity']} "
            f"{result['unit']}"
            f" de {result['product_name']}."
        )

    else:
        message = "Action exécutée avec succès."

    return AgentResponse(
        intent=understanding.intent.value,
        confidence=understanding.confidence,
        needs_clarification=False,
        result=result,
        message=message,
    )


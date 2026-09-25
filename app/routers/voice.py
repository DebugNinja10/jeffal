import os
import tempfile

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.agents.action_executor import ActionExecutor
from app.agents.agent_service import AgentService
from app.agents.mock_intent_parser import MockIntentParser
from app.auth.dependencies import get_current_user
from app.database.dependencies import get_db
from app.models.user import User
from app.services.asr_service import ASRService
from app.services.business_service import get_user_business


router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)


asr_service = ASRService()

agent_service = AgentService(
    MockIntentParser()
)

action_executor = ActionExecutor()


@router.post("/execute")
def execute_voice_agent(
    business_id: int,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Vérifier que l'activité appartient
    # bien à l'utilisateur connecté.
    business = get_user_business(
        db=db,
        business_id=business_id,
        user_id=current_user.id,
    )

    if business is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activité introuvable.",
        )

    temp_path = None

    try:
        # Créer un fichier temporaire.
        suffix = os.path.splitext(
            audio.filename or ""
        )[1] or ".wav"

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        ) as temp_file:

            temp_path = temp_file.name

            content = audio.file.read()

            temp_file.write(content)

        # 1. Audio -> texte
        text = asr_service.transcribe(
            temp_path
        )

        if not text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Aucune parole détectée.",
            )

        # 2. Texte -> compréhension
        understanding = agent_service.understand(
            text
        )

        # 3. Demande de clarification
        if understanding.needs_clarification:
            return {
                "text": text,
                "intent": understanding.intent.value,
                "confidence": understanding.confidence,
                "needs_clarification": True,
                "result": None,
                "message": (
                    "Je n'ai pas suffisamment "
                    "compris votre demande."
                ),
            }

        # 4. Compréhension -> action réelle
        try:
            result = action_executor.execute(
                db=db,
                business_id=business.id,
                understanding=understanding,
            )

        except ValueError as exc:
            return {
                "text": text,
                "intent": understanding.intent.value,
                "confidence": understanding.confidence,
                "needs_clarification": False,
                "result": None,
                "message": str(exc),
            }

        # 5. Réponse
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
            message = (
                "Action exécutée avec succès."
            )

        return {
            "text": text,
            "intent": understanding.intent.value,
            "confidence": understanding.confidence,
            "needs_clarification": False,
            "result": result,
            "message": message,
        }

    finally:
        # Supprimer le fichier temporaire.
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

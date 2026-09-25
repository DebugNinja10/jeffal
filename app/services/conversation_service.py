import uuid

from sqlalchemy.orm import Session

from app.models.conversation import Conversation


def create_conversation(
    db: Session,
    user_id: int,
    business_id: int,
) -> Conversation:

    conversation = Conversation(
        conversation_id=str(uuid.uuid4()),
        user_id=user_id,
        business_id=business_id,
        state="idle",
        context={},
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def get_conversation(
    db: Session,
    conversation_id: str,
    user_id: int,
    business_id: int,
) -> Conversation | None:

    return (
        db.query(Conversation)
        .filter(
            Conversation.conversation_id == conversation_id,
            Conversation.user_id == user_id,
            Conversation.business_id == business_id,
        )
        .first()
    )


def update_conversation(
    db: Session,
    conversation: Conversation,
    state: str,
    context: dict,
) -> Conversation:

    conversation.state = state
    conversation.context = context

    db.commit()
    db.refresh(conversation)

    return conversation

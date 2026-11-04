from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.conversation import Conversation
from app.schemas.conversation import ConversationCreate, ConversationUpdate

from app.models.file import File as FileModel
from agno.media import Image, File

from app.agents.agno_assitant import get_agent
from pathlib import Path
from app.core.config import ALLOWED_IMAGE_TYPES

from app.services import message_service

async def _process_attachment(db: Session, conversation: Conversation, file: FileModel):
    agent_file_processor = get_agent(
        db=db,
        user_id=str(conversation.user_id),
        session_id=str(conversation.session_id),
    )

    path = Path(file.file_path)
    ext = path.suffix.lower()

    prompt = (
        "AUTO-PROCESS: the user just uploaded a file.\n"
        f"file_id: {file.id}\n"
        f"file_name: {file.file_name}\n\n"
        "1. Check whether the attached file is an invoice.\n"
        "2. If it is, extract the data and call save_invoice right away with this exact file_id. "
        "No confirmation needed.\n"
        "3. If it is not an invoice, do not call any tool.\n"
        f'4. Reply with ONE short sentence: "Processed file {file.file_name}, it is about <very short conclusion>." '
        "If save_invoice returned an error, mention it in that sentence."
    )

    if ext == ".pdf":
        response = await agent_file_processor.arun(prompt, files=[File(filepath=str(path))])
    elif ext in ALLOWED_IMAGE_TYPES.values():
        response = await agent_file_processor.arun(prompt, images=[Image(filepath=str(path))])
    else:
        return None

    return response.content

def create_conversation(db: Session, user_id: UUID, data: ConversationCreate):
    conversation = Conversation(user_id=user_id, title=data.title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def list_conversations(db: Session, user_id: UUID):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user_id, Conversation.deleted_at.is_(None))
        .order_by(Conversation.created_at.desc())
        .all()
    )


def get_conversation(db: Session, session_id: UUID, user_id: UUID):
    return (
        db.query(Conversation)
        .filter(
            Conversation.session_id == session_id,
            Conversation.user_id == user_id,
            Conversation.deleted_at.is_(None),
        )
        .first()
    )


def update_conversation(db: Session, conversation: Conversation, data: ConversationUpdate):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(conversation, field, value)
    db.commit()
    db.refresh(conversation)
    return conversation


def delete_conversation(db: Session, conversation: Conversation):
    conversation.deleted_at = func.now()  # soft delete
    db.commit()

async def append_file(db: Session, conversation: Conversation, file: FileModel) -> FileModel:
    conversation.files.append(file)
    db.commit()
    db.refresh(file)

    # Add Agent Logic Automatecly Use the tool to proccess these files
    response = await _process_attachment(
        db=db,
        conversation=conversation,
        file=file
    )

    if response is not None:
        # in case the model succefuly worked
        print(response)
        message_service.create_message(db=db,conversation_id=conversation.session_id,content=response,role=message_service.MessageRole.agent)
        file.is_proccesed = True
        db.commit()
        db.refresh(file)


    # make the agent proccess the file

    return file
import shutil
import uuid
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile

from app.core.config import UPLOAD_DIR
from app.models.file import File


def save_file(upload: UploadFile, user_id: UUID, conversation_id: UUID):
    file_id = uuid.uuid4()
    original_name = Path(upload.filename or "file").name

    dest_dir = Path(UPLOAD_DIR) / str(user_id) / str(conversation_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / str(file_id)

    with dest.open("wb") as out:
        shutil.copyfileobj(upload.file, out)

    # Add Agent Logic Automatecly Use the tool to proccess these files 

    return File(
        id=file_id,
        conversation_id=conversation_id,
        file_name=original_name,
        file_path=str(dest),
    )
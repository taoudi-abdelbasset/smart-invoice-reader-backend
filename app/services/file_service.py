import shutil
import uuid
from pathlib import Path
from uuid import UUID

from fastapi import UploadFile, HTTPException,status

from app.core.config import UPLOAD_DIR, ALLOWED_IMAGE_TYPES
from app.models.file import File


def save_file(upload: UploadFile, user_id: UUID, conversation_id: UUID):
    file_id = uuid.uuid4()
    original_name = Path(upload.filename or "file").name

    content_type = upload.content_type

    if content_type == "application/pdf":
        extension = ".pdf"

    elif content_type in ALLOWED_IMAGE_TYPES:
        extension = ALLOWED_IMAGE_TYPES[content_type]

    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF and image files are allowed."
        )
    dest_dir = Path(UPLOAD_DIR) / str(user_id) / str(conversation_id)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{file_id}{extension}"

    with dest.open("wb") as out:
        shutil.copyfileobj(upload.file, out)

    return File(
        id=file_id,
        conversation_id=conversation_id,
        file_name=original_name,
        file_path=str(dest),
    )
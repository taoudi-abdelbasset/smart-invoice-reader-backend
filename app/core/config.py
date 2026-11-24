import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")

ALLOW_ORIGINS = [o.strip() for o in os.getenv("ALLOW_ORIGINS", "").split(",") if o.strip()]

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

LITELLM_MASTER_KEY = os.getenv("LITELLM_MASTER_KEY")

UPLOAD_DIR = "uploads"

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
}


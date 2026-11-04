from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import ALLOW_ORIGINS

from app.db.database import Base, engine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/health")
def app_health():
    return {"success":True}

from app.models import user as user_model  # noqa: F401
from app.models import conversation as conversation_model  # noqa: F401
from app.models import file as file_model  # noqa: F401
from app.models import message as message_model  # noqa: F401
from app.models import invoice as invoice_model  # noqa: F401
from app.models import invoice_item as invoice_item_model  # noqa: F401
from app.models import company as company_model  # noqa: F401
from app.models import business_entity as business_entity_model  # noqa: F401
from app.models import contact as contact_model  # noqa: F401
from app.routers import files, user, conversation, message, invoice
from app.auth import auth

Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(auth.router) 
app.include_router(files.router)
app.include_router(conversation.router)
app.include_router(message.router)
app.include_router(invoice.router)
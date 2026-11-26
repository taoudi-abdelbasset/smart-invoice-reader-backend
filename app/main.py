from contextlib import asynccontextmanager

import app.agents.tools as agent_tools  # noqa: F401
from app.db.database import SessionLocal
from app.services import tools_service

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import ALLOW_ORIGINS

from app.models import user as user_model  # noqa: F401
from app.models import conversation as conversation_model  # noqa: F401
from app.models import file as file_model  # noqa: F401
from app.models import message as message_model  # noqa: F401
from app.models import invoice as invoice_model  # noqa: F401
from app.models import invoice_item as invoice_item_model  # noqa: F401
from app.models import company as company_model  # noqa: F401
from app.models import business_entity as business_entity_model  # noqa: F401
from app.models import contact as contact_model  # noqa: F401
from app.models import mate_agent as agent_mate_model # noqa: F401
from app.models import tools as agent_tools_model # noqa: F401
from app.models import conversation_member as conversation_member_model  # noqa: F401
from app.models import agent_task as agent_task_model  # noqa: F401
from app.services import tools_service, broker

from app.routers import files, user, conversation, message, invoice, agent, tools
from app.auth import auth

from app.db.database import Base, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    with SessionLocal() as db:
        tools_service.sync_registry_to_db(db)
        broker.recover(db)
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)

@app.get("/health")
def app_health():
    return {"success":True}

Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(auth.router) 
app.include_router(files.router)
app.include_router(conversation.router)
app.include_router(message.router)
app.include_router(invoice.router)
app.include_router(agent.router)
app.include_router(tools.router)
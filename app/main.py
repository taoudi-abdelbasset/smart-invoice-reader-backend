from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agno.agent import Agent
from agno.models.google import Gemini
from app.core.config import DEFAULT_MODEL, ALLOW_ORIGINS

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
from app.routers import user
from app.auth import auth

Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(auth.router) 
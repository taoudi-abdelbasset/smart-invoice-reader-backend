from agno.db.sqlite import SqliteDb
from app.db.database import engine

agent_db = SqliteDb(db_engine=engine, session_table="agent_sessions")
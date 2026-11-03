from agno.storage.sqlite import SqliteStorage
from app.db.database import engine

agent_storage = SqliteStorage(table_name="agent_sessions", db_engine=engine)
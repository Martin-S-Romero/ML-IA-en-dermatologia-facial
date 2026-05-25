import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.db_scheme.base import Base as Base  # re-exportado para que Alembic lo encuentre aquí
from app.core.context import current_user_id

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@event.listens_for(engine, "checkout")
def _set_rls_user(dbapi_connection, _connection_record, _connection_proxy):
    """Inyecta el user_id en la sesión PostgreSQL para que las RLS policies funcionen."""
    user_id = current_user_id.get()
    cursor = dbapi_connection.cursor()
    # Usamos set_config() con parámetro vinculado — sin interpolación de strings (sin SQL injection)
    if user_id:
        cursor.execute("SELECT set_config('app.current_user_id', %s, false)", (str(user_id),))
    else:
        cursor.execute("SELECT set_config('app.current_user_id', '', false)")
    cursor.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

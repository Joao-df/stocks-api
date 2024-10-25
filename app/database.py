from collections.abc import Generator
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import URL, Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.app_config import Settings, get_settings

settings: Settings = get_settings()

postgres_url = URL.create(
    drivername=settings.postgres_drivername,
    username=settings.postgres_username,
    password=settings.postgres_password,
    host=settings.postgres_host,
    port=settings.postgres_port,
    database=settings.postgres_db,
)
engine: Engine = create_engine(postgres_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Generator[Session, Any, None]:
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_session)]

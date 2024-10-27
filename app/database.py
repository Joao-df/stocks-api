import contextlib
from typing import Annotated, Any, AsyncGenerator, AsyncIterator

from fastapi import Depends
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from app.app_config import Settings, get_settings

settings: Settings = get_settings()

postgres_url: URL = URL.create(
    drivername=settings.postgres_drivername,
    username=settings.postgres_username,
    password=settings.postgres_password,
    host=settings.postgres_host,
    port=settings.postgres_port,
    database=settings.postgres_db,
)


class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] | None = None) -> None:
        self.engine_kwargs: dict[str, Any] = engine_kwargs or {}
        self._engine: AsyncEngine = create_async_engine(host, **self.engine_kwargs)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)

    async def close(self) -> None:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Asynchronous context manager that yields an AsyncSession.

        Raises:
            Exception: If DatabaseSessionManager is not initialized.

        Yields:
            AsyncSession: An asynchronous session object.

        Usage:
            async with DatabaseSessionManager(host).session() as session:
                <body>
        """
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session: AsyncSession = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(postgres_url)


async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    """
    Asynchronous generator that yields a session from the DatabaseSessionManager.
    """
    async with sessionmanager.session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]

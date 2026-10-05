from sqlalchemy.orm import DeclarativeBase

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class Base(DeclarativeBase):
    pass

DATABASE_URL = (
    "postgresql+asyncpg://db_user:local_password@localhost:5433/db"
)

engine: AsyncEngine = create_async_engine(
    url = DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

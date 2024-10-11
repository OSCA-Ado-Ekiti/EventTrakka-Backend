from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_async_engine(
    str(settings.DATABASE_URI),
    echo=True,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        session: AsyncSession
        try:
            yield session
        finally:
            print("closing db connection")
            await session.close()

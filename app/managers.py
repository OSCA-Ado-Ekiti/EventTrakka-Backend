from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, select

from app.core.db import get_db_session
from app.core.utils import aware_datetime_now
from app.extras.models import BaseDBModel


class BaseModelManager:
    def __init__(self, model_class):
        self.model_class: type[BaseDBModel] = model_class

    async def create(
        self, *, creation_data: dict, session: AsyncSession | None = None
    ) -> BaseDBModel:
        async for s in get_db_session():
            session = s or session
            if "last_updated_at" not in creation_data.keys():
                creation_data["last_updated_at"] = aware_datetime_now()
            model = self.model_class.model_validate(creation_data)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return model

    async def update(
        self, *, id: UUID, update_data: dict, session: AsyncSession | None = None
    ):
        async for s in get_db_session():
            session = s or session
            if "last_updated_at" not in update_data.keys():
                update_data["last_updated_at"] = aware_datetime_now()
            model = await self.get(id=id, session=session)
            model = self.model_class.model_validate(
                model.model_dump().update(update_data)
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return model

    async def get(self, session: AsyncSession | None = None, *whereclause) -> BaseModel:
        async for s in get_db_session():
            session = s or session
            query = select(self.model_class).where(*whereclause)
            return (await session.execute(query)).scalar_one()

    async def all(self, *, session: AsyncSession | None = None):
        async for s in get_db_session():
            session = s or session
            query = select(self.model_class)
            return (await session.execute(query)).all()

    async def delete(self, *, id: UUID, session: AsyncSession | None):
        async for s in get_db_session():
            session = s or session
            query = delete(self.model_class).where(self.model_class.id == id)
            await session.execute(query)

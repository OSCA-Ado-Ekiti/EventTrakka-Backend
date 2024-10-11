from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, select

from app.core.db import get_db_session


class BaseModelManager:
    def __init__(self, model_class):
        self.model_class: type[BaseModel] = model_class
        self.session = get_db_session()

    async def create(
        self, creation_data: dict, session: AsyncSession | None = None
    ) -> BaseModel:
        session = session or self.session
        model = self.model_class.model_validate(creation_data)
        session.add(model)
        await session.commit()
        await session.refresh(model)
        return model

    async def update(
        self, id: UUID, update_data: dict, session: AsyncSession | None = None
    ):
        session = session or self.session
        model = await self.get(id=id, session=session)
        model = self.model_class.model_validate(model.model_dump().update(update_data))
        session.add(model)
        await session.commit()
        await session.refresh(model)
        return model

    async def get(self, id: UUID, session: AsyncSession | None = None) -> BaseModel:
        session = session or self.session
        query = select(self.model_class).where(self.model_class.id == id)
        return (await session.execute(query)).scalar_one()

    async def all(self, session: AsyncSession | None = None):
        session = session or self.session
        query = select(self.model_class)
        return (await session.execute(query)).all()

    async def delete(self, id: UUID, session: AsyncSession | None):
        session = session or self.session
        query = delete(self.model_class).where(self.model_class.id == id)
        await session.execute(query)

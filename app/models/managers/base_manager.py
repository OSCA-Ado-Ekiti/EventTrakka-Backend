from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, select

from app.core.db import get_db_session
from app.core.utils import aware_datetime_now
from app.models.exceptions import AlreadyExist, DoesNotExist

if TYPE_CHECKING:
    from app.extras.models import BaseDBModel


class BaseModelManager[T: BaseDBModel]:
    async def create(
        self, *, creation_data: dict, session: AsyncSession | None = None
    ) -> T:
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
    ) -> T:
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

    async def get(self, session: AsyncSession | None = None, *whereclause) -> T:
        async for s in get_db_session():
            session = s or session
            query = select(self.model_class).where(*whereclause)
            try:
                return (await session.execute(query)).scalar_one()
            except NoResultFound:
                raise self.model_class.DoesNotExist(
                    f"object does not exist {whereclause}"
                )

    async def all(self, *, session: AsyncSession | None = None) -> list[T]:
        async for s in get_db_session():
            session = s or session
            query = select(self.model_class)
            return (await session.execute(query)).all()

    async def filter(self, session: AsyncSession | None = None, *whereclause):
        async for s in get_db_session():
            session = s or session
            query = select(self.model_class).where(*whereclause)
            return (await session.execute(query)).all()

    async def delete(self, *, id: UUID, session: AsyncSession | None):
        async for s in get_db_session():
            session = s or session
            query = delete(self.model_class).where(self.model_class.id == id)
            await session.execute(query)

    def _bind_exceptions_to_model(self):
        """
        Bind DoesNotExist and MultipleObjectsReturned exceptions to the model class.
        """
        self.model_class.DoesNotExist = type(
            f"{self.model_class.__name__}DoesNotExist", (DoesNotExist,), {}
        )
        self.model_class.AlreadyExist = type(
            f"{self.model_class.__name__}AlreadyExist", (AlreadyExist,), {}
        )

    def __set_name__(self, owner: type[T], name: str):
        """This dunder method lets us dynamically bind the model class to its respective
        model manager
        """
        self.model_class = owner
        self._bind_exceptions_to_model()

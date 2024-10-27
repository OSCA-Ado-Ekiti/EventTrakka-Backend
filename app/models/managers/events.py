from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.managers.base_manager import BaseModelManager

if TYPE_CHECKING:
    from app.models import Event
    from app.models.schemas.events import CreateEvent


class EventModelManager[T: Event](BaseModelManager):
    async def create_event(
        self, data: "CreateEvent", session: AsyncSession | None = None
    ):
        creation_data = data.model_dump()
        if data.tags:
            tags = creation_data.pop("tags")
        return await self.create(creation_data=creation_data, session=session)

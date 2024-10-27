from typing import TYPE_CHECKING, Optional
from uuid import UUID

from fastapi_pagination.ext.sqlmodel import paginate
from pydantic import ValidationError
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import column, select, text

from app.core.db import get_db_session
from app.models.managers.base_manager import BaseModelManager

if TYPE_CHECKING:
    from app.models import Organization, User


class OrganizationModelManager[T: Organization](BaseModelManager):
    async def create_organization(
        self,
        name: str,
        owner: Optional["User"] = None,
        owner_id: UUID | None = None,
        about: str | None = None,
        session: AsyncSession | None = None,
    ) -> T:
        from app.models.organizations import (
            OrganizationMember,
            OrganizationMemberPermission,
        )

        if not (owner or owner_id):
            raise ValidationError("owner or owner_id must be provided for creation")

        permissions = [permission.value for permission in OrganizationMemberPermission]
        creation_data = {
            "name": name,
            "about": about,
            "owner_id": owner_id,
            "members": [
                OrganizationMember.model_validate(
                    {"id": str(owner.id), "role": "Owner", "permissions": permissions}
                )
            ],
        }
        if owner:
            creation_data["owner_id"] = owner.id

        return await super().create(creation_data=creation_data, session=session)

    async def get_organizations_as_member(
        self,
        member: "User",
        session: AsyncSession | None = None,
    ) -> list[T]:
        async for s in get_db_session():
            session = s or session
            query = (
                select(self.model_class)
                .select_from(self.model_class)
                .join(
                    func.jsonb_array_elements(self.model_class.members).alias(
                        "members_jsonb"
                    ),
                    text("true"),  # LATERAL join
                )
                .where(
                    func.jsonb_extract_path_text(column("members_jsonb"), "id")
                    == str(member.id)
                )
            )
            return await paginate(session, query)

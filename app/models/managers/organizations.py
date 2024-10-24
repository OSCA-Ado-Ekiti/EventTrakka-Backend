from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.managers.base_manager import BaseModelManager

if TYPE_CHECKING:
    from app.models import Organization, User


class OrganizationModelManager[T: Organization](BaseModelManager):
    async def create_organization(
        self,
        name: str,
        owner: "User",
        about: str | None = None,
        session: AsyncSession | None = None,
    ) -> T:
        from app.models.organizations import (
            OrganizationMember,
            OrganizationMemberPermission,
        )

        permissions = [permission.value for permission in OrganizationMemberPermission]
        creation_data = {
            "name": name,
            "owner": owner,
            "about": about,
            "members": [
                OrganizationMember.model_validate(
                    {"id": owner.id, "role": "Owner", "permissions": permissions}
                )
            ],
        }
        return await super().create(creation_data=creation_data, session=session)

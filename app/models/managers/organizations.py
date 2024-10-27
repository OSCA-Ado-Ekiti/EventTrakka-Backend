from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

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

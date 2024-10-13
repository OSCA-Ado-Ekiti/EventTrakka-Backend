from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.models.schemas.api import ResponseData
from app.models.schemas.users import UserPublic

router = APIRouter(prefix="/users")


@router.get("/current-user")
async def get_current_user(current_user: CurrentUser):
    """Retrieve the details of the user with the provided access token"""
    return ResponseData[UserPublic](
        detail="User retrieved successfully",
        data=UserPublic.model_validate(current_user.model_dump()),
    )


@router.patch("/current-user")
async def update_current_user(current_user: CurrentUser):
    """Update the user information for the user with the provided access token"""
    ...

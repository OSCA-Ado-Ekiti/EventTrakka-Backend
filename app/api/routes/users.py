from fastapi import APIRouter

router = APIRouter(prefix="/users")


@router.get("/current-user")
async def get_current_user():
    """Retrieve the details of the user with the provided access token"""
    ...


@router.patch("/current-user")
async def update_current_user():
    """Update the user information for the user with the provided access token"""
    ...

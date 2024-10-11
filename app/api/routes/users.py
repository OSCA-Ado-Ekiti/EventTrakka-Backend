from fastapi import APIRouter

router = APIRouter(prefix="/users")

@router.get('/current-user')
async def get_current_user():
    ...

@router.patch('/current-user')
async def update_current_user():
    ...

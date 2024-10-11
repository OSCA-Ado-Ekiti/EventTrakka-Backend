from fastapi import APIRouter

router = APIRouter(prefix="/auth")

@router.post('/signup')
async def signup_via_email():
    ...


@router.post('/verify-email')
async def verify_email():
    ...

@router.post('/access-token')
async def obtain_access_token():
    ...

@router.post('/refresh-token')
async def refresh_access_token():
    ...

@router.post('/forgot-password')
async def forgot_password():
    ...

@router.post('/reset-password')
async def reset_password():
    ...
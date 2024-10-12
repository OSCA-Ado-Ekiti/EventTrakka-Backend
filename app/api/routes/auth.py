from fastapi import APIRouter

router = APIRouter(prefix="/auth")


@router.post("/signup")
async def signup_via_email():
    """Signup to EventTrakka with the email flow."""
    ...


@router.post("/verify-email")
async def verify_email():
    """Verify the email address of the signed-up user after email link opened.
    Note:
        not to be used in the frontend
    """
    ...


@router.post("/access-token")
async def obtain_access_token():
    """Obtain the access and refresh tokens to be used for protected endpoints."""
    ...


@router.post("/refresh-token")
async def refresh_access_token():
    """Refresh the access token after expiry"""
    ...


@router.post("/forgot-password")
async def forgot_password():
    """Initiate the password reset flow."""
    ...


@router.post("/reset-password")
async def reset_password():
    """Complete the password reset flow. not to be used directly"""
    ...

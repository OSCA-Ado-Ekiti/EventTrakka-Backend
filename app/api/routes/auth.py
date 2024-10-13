from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUserViaRefreshToken
from app.core import security
from app.core.config import settings
from app.models import User
from app.models.schemas.api import (
    AccessTokenSubject,
    RefreshTokenSubject,
    ResponseData,
    Token,
)
from app.models.schemas.users import CreateUser, UserPublic
from app.models.users import UserAlreadyExistError

router = APIRouter(prefix="/auth")


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup_via_email(data: CreateUser):
    """Signup to EventTrakka with the email flow."""
    try:
        user = await User.objects.create_user(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
            is_email_verified=True,
        )
        # TODO: Send email verification mail
        return ResponseData[UserPublic](
            detail="Signup successful, verify email address via the email sent to user",
            data=UserPublic.model_validate(user.model_dump()),
        )
    except UserAlreadyExistError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )


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

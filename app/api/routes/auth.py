from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUserViaRefreshToken
from app.core import security
from app.core.config import settings
from app.core.email_service import EmailService
from app.models import User
from app.models.otp import OTPPurpose, OTPRecord
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
async def signup_via_email(data: CreateUser, background_tasks: BackgroundTasks):
    """Signup to EventTrakka with the email flow."""
    try:
        user = await User.objects.create_user(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
        )

        otp: OTPRecord = await OTPRecord.objects.create_otp(
            user_id=user.id, purpose=OTPPurpose.EMAIL_VERIFICATION
        )
        # TODO: Check if email instantiation blocks
        email_service = EmailService()
        task_kwargs = {"email": user.email, "name": user.first_name, "otp": otp.code}
        background_tasks.add_task(email_service.send_verification_email, **task_kwargs)
        return ResponseData[UserPublic](
            detail="Signup successful, verify email address via the email sent to user",
            data=UserPublic.model_validate(user.model_dump()),
        )

    except UserAlreadyExistError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post("/verify-email")
async def verify_email():
    """Verify the email address of the signed-up user after email link opened.
    Note:
        not to be used in the frontend
    """
    ...


@router.post("/access-token")
async def obtain_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """Obtain the access and refresh tokens to be used for protected endpoints.

    Note:
        The user's email address should be passed to the `username` field.
    """
    user = await User.objects.authenticate(
        email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user, contact admin")
    elif not user.is_email_verified:
        raise HTTPException(
            status_code=400, detail="User has not verified email address"
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    # TODO: Add scope data
    access_token_subject = AccessTokenSubject(user=user.id).model_dump_json()
    refresh_token_subject = RefreshTokenSubject(user=user.id).model_dump_json()
    token = Token(
        access_token=security.create_access_token(
            access_token_subject, expires_delta=access_token_expires
        ),
        refresh_token=security.create_access_token(
            refresh_token_subject, expires_delta=refresh_token_expires
        ),
    )
    return ResponseData[Token](detail="Tokens successfully retrieved", data=token)


@router.post("/refresh-token")
async def refresh_access_token(current_user: CurrentUserViaRefreshToken):
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

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from app.api.deps import (
    CurrentUserViaEmailVerificationToken,
    CurrentUserViaRefreshToken,
)
from app.core import security
from app.core.config import settings
from app.core.email_service import EmailService
from app.core.security import DEFAULT_USER_SCOPES, APIScope
from app.models import User
from app.models.otp import OTPPurpose, OTPRecord
from app.models.schemas.api import (
    AuthToken,
    PasswordReset,
    ResponseData,
    TokenSubject,
    VerificationToken,
)
from app.models.schemas.users import CreateUser

router = APIRouter(prefix="/auth")


async def get_email_verification_client_verification_token(
    user: User, background_tasks: BackgroundTasks
) -> str:
    otp: OTPRecord = await OTPRecord.objects.create_otp(
        user_id=user.id, purpose=OTPPurpose.EMAIL_VERIFICATION
    )
    email_service = EmailService()
    task_kwargs = {"email": user.email, "name": user.first_name, "otp": otp.code}
    background_tasks.add_task(email_service.send_verification_email, **task_kwargs)
    verification_token_expires = timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    verification_token_subject = TokenSubject.model_validate(
        {
            "type": "verification_token",
            "user_id": user.id,
            "scopes": [APIScope.EMAIL_VERIFICATION],
        }
    )
    return security.create_access_token(
        verification_token_subject, expires_delta=verification_token_expires
    )


def generate_auth_token(user: User) -> AuthToken:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token_subject = TokenSubject.model_validate(
        {"type": "access_token", "user_id": user.id, "scopes": DEFAULT_USER_SCOPES}
    )
    refresh_token_subject = TokenSubject.model_validate(
        {"type": "refresh_token", "user_id": user.id, "scopes": DEFAULT_USER_SCOPES}
    )
    return AuthToken(
        access_token=security.create_access_token(
            access_token_subject, expires_delta=access_token_expires
        ),
        refresh_token=security.create_access_token(
            refresh_token_subject, expires_delta=refresh_token_expires
        ),
    )


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup_via_email(data: CreateUser, background_tasks: BackgroundTasks):
    """Signup to EventTrakka with the email flow.

    Calling this endpoint will return a `verification_token` in the response, not to be confused
    with the `access_token` and `refresh_token`, the `verification_token` should be used as the
    auth token for sending the otp the user enters from the email they received.

    The flow: The frontend calls this endpoint to sign up a user, an email is sent to the
    newly created user with an OTP for email verification, the frontend receives a
    `verification_token` from this endpoint and advances to the page waiting for the OTP
    that was sent to the user's email, the user enters the OTP in the frontend, the
    frontend sends a request to the `/verify-email` endpoint with the `verification_token`
    as the bearer token of the request and the OTP the user entered.
    """
    try:
        user = await User.objects.create_user(
            email=data.email,
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
        )
        token = await get_email_verification_client_verification_token(
            user, background_tasks
        )
        return ResponseData(
            detail="Signup successful, verify email address via the email sent to user",
            data=VerificationToken.model_validate({"verification_token": token}),
        )

    except User.AlreadyExist as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post("/verify-email")
async def verify_email(user: CurrentUserViaEmailVerificationToken, otp: str):
    """Verify the email address of the signed-up user after email link opened."""
    try:
        otp_record: OTPRecord = await OTPRecord.objects.get(
            None,
            OTPRecord.purpose == OTPPurpose.EMAIL_VERIFICATION,
            OTPRecord.user_id == user.id,
            OTPRecord.code == otp,
        )
        await user.objects.update(id=user.id, update_data={"is_email_verified": True})
        await otp_record.objects.delete(id=otp_record.id, session=None)
        return ResponseData(detail="Email verification successful")
    except OTPRecord.DoesNotExist as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.post("/resend-verify-email")
async def resend_verify_email(
    user: CurrentUserViaEmailVerificationToken, background_tasks: BackgroundTasks
):
    """Resend verification mail to the user"""
    token = await get_email_verification_client_verification_token(
        user, background_tasks
    )
    return ResponseData(
        detail=f"Verification email has been resent to {user.email}",
        data=VerificationToken.model_validate({"verification_token": token}),
    )


@router.post("/access-token")
async def obtain_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    background_tasks: BackgroundTasks,
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
        verification_token = await get_email_verification_client_verification_token(
            user, background_tasks
        )
        detail = ResponseData(
            detail="User has not verified email address, please verify email address",
            data=VerificationToken.model_validate(
                {"verification_token": verification_token}
            ),
        )
        raise HTTPException(
            status_code=400,
            detail=detail.model_dump(),
        )
    token = generate_auth_token(user)
    return ResponseData[AuthToken](detail="Tokens successfully retrieved", data=token)


@router.post("/refresh-token")
async def refresh_access_token(current_user: CurrentUserViaRefreshToken):
    """Refresh the access token after expiry"""
    token = generate_auth_token(current_user)
    return ResponseData[AuthToken](detail="Token refresh successful", data=token)


@router.post("/forgot-password")
async def forgot_password(email: EmailStr, background_tasks: BackgroundTasks):
    """Initiate the password reset flow.

    The flow: The user provides the email for the account, an email is sent to the
    user is they exist. the email will contain a dynamic url link to the frontend,
    following the format [FRONTEND_HOST_URL]/reset-password/:user_id/:otp. The frontend
    will extract the `userId` and `otp` from the page, this page will also include the
    form for updating the password (i.e. new password, confirm password) when the user
    opts to reset the password, a request is made to the `/reset-password` endpoint
    with the `user_id`, `otp` and `new_password` to reset the password.
    """
    try:
        user: User = await User.objects.get(None, User.email == email)
        otp_record: OTPRecord = await OTPRecord.objects.create_otp(
            user_id=user.id, purpose=OTPPurpose.PASSWORD_RESET
        )
        reset_url = (
            f"{settings.FRONTEND_HOST}/reset-password/{user.id}/{otp_record.code}"
        )
        email_service = EmailService()
        task_kwargs = {
            "recipients": [user.email],
            "subject": "",
            "template_name": "forgot-password.html",
            "context": {"name": user.first_name, "reset_url": reset_url},
        }
        background_tasks.add_task(email_service.send_mail, **task_kwargs)
    except User.DoesNotExist as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with email `{email}` does not exist",
        ) from error


@router.post("/reset-password")
async def reset_password(data: PasswordReset):
    """Complete the password reset flow. not to be used directly"""
    try:
        otp_record = await OTPRecord.objects.get(
            None,
            OTPRecord.purpose == OTPPurpose.PASSWORD_RESET,
            OTPRecord.user_id == data.user_id,
            OTPRecord.code == data.otp,
        )
        await otp_record.objects.delete(id=otp_record.id, session=None)
    except OTPRecord.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid opt provided for password reset",
        )
    user: User = await User.objects.get(None, User.id == data.user_id)
    await user.set_password(data.new_password)
    return ResponseData(detail="Password reset successful")

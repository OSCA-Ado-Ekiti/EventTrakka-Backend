from typing import Annotated, Literal

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_db_session
from app.core.security import APIScope, decode_jwt_subject
from app.models import User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/access-token"
)

AsyncSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(
    session: AsyncSessionDep,
    security_scopes: SecurityScopes,
    token: TokenDep,
    token_type: Literal[
        "access_token", "refresh_token", "verification_token"
    ] = "access_token",
) -> User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        subject = decode_jwt_subject(token)
        if token_type != subject.type:
            raise ValidationError("invalid token type")
    except (InvalidTokenError, ValidationError) as error:
        raise credentials_exception from error
    try:
        user: User = await User.objects.get(session, User.id == subject.user_id)
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user, contact admin")
    if not user.is_email_verified:
        raise HTTPException(status_code=400, detail="User pending email verification")
    for scope in security_scopes.scopes:
        if scope not in subject.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_user_via_access_token(
    session: AsyncSessionDep,
    security_scopes: SecurityScopes,
    token: TokenDep,
):
    return await get_current_user(session, security_scopes, token, "access_token")


async def get_current_user_via_refresh_token(
    session: AsyncSessionDep,
    security_scopes: SecurityScopes,
    token: TokenDep,
):
    return await get_current_user(session, security_scopes, token, "refresh_token")


async def get_current_user_via_verification_token(
    session: AsyncSessionDep,
    security_scopes: SecurityScopes,
    token: TokenDep,
):
    return await get_current_user(session, security_scopes, token, "verification_token")


CurrentUser = Annotated[User, Depends(get_current_user_via_access_token)]

CurrentUserViaRefreshToken = Annotated[
    User, Depends(get_current_user_via_refresh_token)
]
CurrentUserViaEmailVerificationToken = Annotated[
    User,
    Security(
        get_current_user_via_verification_token, scopes=[APIScope.EMAIL_VERIFICATION]
    ),
]

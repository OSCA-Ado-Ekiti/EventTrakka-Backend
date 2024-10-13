import json
from typing import Annotated, Literal

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.db import get_db_session
from app.models import User
from app.models.schemas.api import AccessTokenSubject, RefreshTokenSubject

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/access-token"
)

AsyncSessionDep = Annotated[AsyncSession, Depends(get_db_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(
    session: AsyncSessionDep,
    token: TokenDep,
    token_type: Literal["access_token", "refresh_token"] = "access_token",
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        subject = json.loads(payload["sub"])
        if token_type == "access_token":
            token_data = AccessTokenSubject.model_validate(subject)
        elif token_type == "refresh_token":
            token_data = RefreshTokenSubject.model_validate(subject)
        else:
            raise ValidationError("invalid token type")
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    print(f"token data is {token_data}")
    user = await User.objects.get(session, User.id == token_data.user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user, contact admin")
    return user


async def get_current_user_via_access_token(
    session: AsyncSessionDep,
    token: TokenDep,
):
    return await get_current_user(session, token, "access_token")


async def get_current_user_via_refresh_token(
    session: AsyncSessionDep,
    token: TokenDep,
):
    return await get_current_user(session, token, "refresh_token")


CurrentUser = Annotated[User, Depends(get_current_user_via_access_token)]
CurrentUserViaRefreshToken = Annotated[
    User, Depends(get_current_user_via_refresh_token)
]

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING

import bcrypt
import jwt
from passlib.context import CryptContext

from app.core.config import settings

if TYPE_CHECKING:
    from app.models.schemas.api import TokenSubject


# Passlib is no longer actively maintained and depends on bcrypt. Passlib raises
# an error on a missing attribute in bcrypt, this is a workaround to resolve the
# issue. see https://github.com/pyca/bcrypt/issues/684
@dataclass
class SolveBugBcryptWarning:
    __version__: str = bcrypt.__version__


bcrypt.__about__ = SolveBugBcryptWarning()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def create_access_token(subject: "TokenSubject", expires_delta: timedelta) -> str:
    expire = datetime.now(UTC) + expires_delta
    to_encode = {"exp": expire, "sub": subject.model_dump_json()}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def decode_jwt_subject(token: str) -> "TokenSubject":
    """Decodes a jwt token and returns the subject.

    Raises:
        InvalidTokenError: If it fails to decode the jwt token, or it has expired
    """
    from app.models.schemas.api import TokenSubject

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    return TokenSubject.model_validate_json(payload["sub"])


class APIScope(str, Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


DEFAULT_USER_SCOPES = []

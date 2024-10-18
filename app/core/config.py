import warnings
from pathlib import Path
from typing import Annotated, Any, Literal, Self

from fastapi_mail import ConnectionConfig
from pydantic import (
    AnyUrl,
    BeforeValidator,
    EmailStr,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    DESCRIPTION: str = (
        "This is the official API Documentation for EventTrakka, all endpoints have not been implemented and "
        "are susceptible to changes as the project is being actively developed. this is only a preview of the "
        "likely APIs to expect for consumption"
    )

    PROJECT_NAME: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    OTP_EXPIRE_MINUTES: int = 60 * 5
    OTP_LENGTH: int = 6

    MAIL_USERNAME: str = "john"
    MAIL_PASSWORD: str = "doe"
    MAIL_FROM: EmailStr = "johndoe@eventtrakka.com"
    MAIL_FROM_NAME: str = "John Doe"
    MAIL_PORT: int = 1026
    MAIL_SERVER: str = "test-smtp-server"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    MAIL_USE_CREDENTIALS: bool = False
    MAIL_VALIDATE_CERTS: bool = False
    MAIL_TIMEOUT: int = 60  # 1 minute

    @computed_field
    @property
    def MAIL_TEMPLATES_DIR(self) -> Path:
        directory = self.BASE_DIR / "app/email-templates"
        if not directory.is_dir():
            raise ValueError(
                f"MAIL_TEMPLATES_DIR: {directory} is not a valid directory"
            )
        return directory

    @computed_field
    @property
    def MAIL_CONNECTION_CONFIG(self) -> ConnectionConfig:
        return ConnectionConfig(
            MAIL_USERNAME=self.MAIL_USERNAME,
            MAIL_PASSWORD=self.MAIL_PASSWORD,
            MAIL_FROM=self.MAIL_FROM,
            MAIL_FROM_NAME=self.MAIL_FROM_NAME,
            MAIL_PORT=self.MAIL_PORT,
            MAIL_SERVER=self.MAIL_SERVER,
            MAIL_STARTTLS=self.MAIL_STARTTLS,
            MAIL_SSL_TLS=self.MAIL_SSL_TLS,
            USE_CREDENTIALS=self.MAIL_USE_CREDENTIALS,
            VALIDATE_CERTS=self.MAIL_VALIDATE_CERTS,
            TEMPLATE_FOLDER=self.MAIL_TEMPLATES_DIR,
            TIMEOUT=self.MAIL_TIMEOUT,
        )

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)

        return self

    # TODO: move to .env file
    TIMEZONE: str = "Africa/Lagos"


settings = Settings()  # type: ignore

from functools import lru_cache
from pathlib import Path
from pydantic import EmailStr, Field
from pydantic_settings import BaseSettings
from fastapi_mail import ConnectionConfig, FastMail


class EmailSettings(BaseSettings):
    MAIL_USERNAME: str = Field(...)
    MAIL_PASSWORD: str = Field(...)
    MAIL_FROM: EmailStr = Field(...)
    MAIL_FROM_NAME: str = Field("EventTrakka")
    MAIL_PORT: int = Field(587)
    MAIL_SERVER: str = Field("smtp.gmail.com")
    MAIL_STARTTLS: bool = Field(True)
    MAIL_SSL_TLS: bool = Field(False)
    MAIL_USE_CREDENTIALS: bool = Field(True)
    MAIL_VALIDATE_CERTS: bool = Field(True)
    MAIL_TIMEOUT: int = Field(60)
    TEMPLATES_DIR: Path = Field(default=Path(__file__).parent.parent / "email-templates")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


class EmailConfig:
    """Email configuration manager that provides FastMail configuration."""

    def __init__(self):
        self.settings = get_email_settings()
        self._connection_config = None
        self._fast_mail = None

    @property
    def connection_config(self) -> ConnectionConfig:
        """Get FastMail connection configuration."""
        if self._connection_config is None:
            self._connection_config = ConnectionConfig(
                MAIL_USERNAME=self.settings.MAIL_USERNAME,
                MAIL_PASSWORD=self.settings.MAIL_PASSWORD,
                MAIL_FROM=self.settings.MAIL_FROM,
                MAIL_FROM_NAME=self.settings.MAIL_FROM_NAME,
                MAIL_PORT=self.settings.MAIL_PORT,
                MAIL_SERVER=self.settings.MAIL_SERVER,
                MAIL_STARTTLS=self.settings.MAIL_STARTTLS,
                MAIL_SSL_TLS=self.settings.MAIL_SSL_TLS,
                USE_CREDENTIALS=self.settings.MAIL_USE_CREDENTIALS,
                VALIDATE_CERTS=self.settings.MAIL_VALIDATE_CERTS,
                TEMPLATE_FOLDER=str(self.settings.TEMPLATES_DIR),
                TIMEOUT=self.settings.MAIL_TIMEOUT
            )
        return self._connection_config

    @property
    def fast_mail(self) -> FastMail:
        """Get configured FastMail instance."""
        if self._fast_mail is None:
            self._fast_mail = FastMail(self.connection_config)
        return self._fast_mail

    @property
    def templates_dir(self) -> Path:
        """Get path to email templates directory."""
        return self.settings.TEMPLATES_DIR


@lru_cache()
def get_email_settings() -> EmailSettings:
    """Get cached email settings instance."""
    return EmailSettings()


email_config = EmailConfig()

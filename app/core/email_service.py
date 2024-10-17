from pathlib import Path
from typing import List, Optional

from fastapi import HTTPException, status
from fastapi_mail import MessageSchema, MessageType
from pydantic import EmailStr
from jinja2 import Environment, select_autoescape, FileSystemLoader

from .email_config import email_config


class EmailService:
    """Service for handling email operations."""

    def __init__(self):
        self.fast_mail = email_config.fast_mail

        self.env = Environment(
            loader=FileSystemLoader(email_config.templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    async def send_verification_email(
        self,
        email: EmailStr,
        name: str,
        otp: str
    ) -> None:
        """Send verification email with OTP."""
        try:
            template = self.env.get_template('verify_email.html')

            html_content = template.render(
                name=name,
                otp=otp
            )

            message = MessageSchema(
                subject="Verify Your Email - EventTrakka",
                recipients=[email],
                body=html_content,
                subtype=MessageType.html
            )

            await self.fast_mail.send_message(message)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send verification email: {str(e)}"
            ) from e

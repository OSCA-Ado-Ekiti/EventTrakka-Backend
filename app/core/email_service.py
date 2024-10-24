from typing import Any

from fastapi_mail import FastMail, MessageSchema, MessageType
from jinja2 import Template
from pydantic import EmailStr

from app.core.config import settings


class EmailService:
    """Service for handling email operations."""

    def __init__(self):
        self.fast_mail = FastMail(settings.MAIL_CONNECTION_CONFIG)

    async def send_mail(
        self,
        recipients: list[EmailStr],
        subject: str,
        template_name: str,
        context: dict[str, Any],
        subject_context: dict[str, Any] | None = None,
    ):
        """Renders and sends emails to the provided recipients.

        Args:
            recipients: The recipients of the mail
            subject: The subject of the mail, It also servers as a template if the subject needs to have dynamic content
                provide the context for the subject when it is used as a template in the `subject_context` param
            template_name: The name of the html template located in the `MAIL_TEMPLATES_DIR`
            context: The context data used to render the email template
            subject_context: The subject context data
        """
        if subject_context:
            template = Template(subject)
            subject = template.render(subject_context)

        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            template_body=context,
            subtype=MessageType.html,
        )
        await self.fast_mail.send_message(message, template_name)

    async def send_verification_email(
        self, email: EmailStr, name: str, otp: str
    ) -> None:
        """Send verification email with OTP."""
        context = {"name": name, "otp": otp}
        subject_context = {"project_name": settings.PROJECT_NAME}
        await self.send_mail(
            recipients=[email],
            subject="Verify your Email - {{ project_name }}",
            template_name="verify-email.html",
            context=context,
            subject_context=subject_context,
        )

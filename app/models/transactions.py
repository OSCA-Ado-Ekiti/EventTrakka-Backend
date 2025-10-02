from enum import StrEnum

from pydantic import EmailStr
from sqlmodel import Field

from app.extras.models import BaseDBModel


class TransactionStatus(StrEnum):
    PENDING = "PENDING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"


class Transaction(BaseDBModel, table=True):
    __tablename__ = "transactions"

    email: EmailStr = Field(max_length=320)
    reason: str | None
    status: TransactionStatus

from typing import Any, ClassVar, Self, override
from uuid import UUID, uuid4

from fastapi.encoders import jsonable_encoder
from pydantic import AwareDatetime
from pydantic import BaseModel as _BaseModel
from sqlalchemy import types
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import Mutable
from sqlmodel import TIMESTAMP, Field, SQLModel

from app.core.utils import aware_datetime_now
from app.models.managers.base_manager import BaseModelManager


class BaseDBModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: AwareDatetime = Field(
        default_factory=aware_datetime_now, sa_type=TIMESTAMP(timezone=True)
    )
    last_updated_at: AwareDatetime | None = Field(sa_type=TIMESTAMP(timezone=True))

    objects: ClassVar[BaseModelManager] = BaseModelManager()


class JSONBPydanticField(types.TypeDecorator):
    """This is a custom SQLAlchemy field that allows easy serialization between database JSONB types and Pydantic models"""

    impl = JSONB

    def __init__(
        self,
        pydantic_model_class: type["MutableSABaseModel"],
        many: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.pydantic_model_class = pydantic_model_class
        self.many = many

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(JSONB())

    def process_bind_param(self, value: _BaseModel | list[_BaseModel], dialect):
        """Convert python native type to JSON string before storing in the database"""
        return jsonable_encoder(value) if value else None

    def process_result_value(self, value, dialect):
        """Convert JSON string back to Python object after retrieving from the database"""
        if self.many:
            return (
                [self.pydantic_model_class.model_validate(v) for v in value]
                if value
                else None
            )
        return (
            self.pydantic_model_class.model_validate(value)
            if value is not None
            else None
        )


class MutableSAList(list, Mutable):
    """This is a hack that is intended to allow SQLAlchemy detect changes in JSON field that is a list in native python
    Allows SQLAlchmey Session to track mutable behavior"""

    @override
    def append(self, __object):
        self.changed()
        super().append(__object)

    @override
    def remove(self, __value):
        self.changed()
        super().remove(__value)

    @override
    def pop(self, __index=-1):
        self.changed()
        super().pop(__index)

    @override
    def reverse(self):
        self.changed()
        super().reverse()

    @override
    def __setattr__(self, name: str, value: Any) -> None:
        self.changed()
        super().__setattr__(name, value)

    @override
    def __setitem__(self, key, value):
        self.changed()
        super().__setitem__(key, value)

    @override
    def __delitem__(self, key):
        self.changed()
        super().__delitem__(key)

    def __iadd__(self, other):
        self.changed()
        super().__iadd__(other)


class MutableSABaseModel(_BaseModel, Mutable):
    """This is a hack that is intended to allow SQLAlchemy detect changes in JSON field that is a pydantic model"""

    def __setattr__(self, name: str, value: Any) -> None:
        """Allows SQLAlchmey Session to track mutable behavior"""
        self.changed()
        return super().__setattr__(name, value)

    @classmethod
    def coerce(cls, key: str, value: Any) -> Self | None:
        """Convert JSON to pydantic model object allowing for mutable behavior"""
        if isinstance(value, cls) or value is None:
            return value

        if isinstance(value, str):
            return cls.model_validate_json(value)

        if isinstance(value, dict):
            return cls.model_validate(value)

        if isinstance(value, list):
            return MutableSAList([cls.model_validate(v) for v in value])

        return super().coerce(key, value)

    @classmethod
    def to_sa_type(cls, many=False):
        return cls.as_mutable(JSONBPydanticField(pydantic_model_class=cls, many=many))

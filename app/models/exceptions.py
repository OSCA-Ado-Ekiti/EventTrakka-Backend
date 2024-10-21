class ModelException(Exception):
    """Base class for all model-related exceptions."""

    ...


class DoesNotExist(ModelException):
    """Exception raised when an object does not exist."""

    ...


class AlreadyExist(ModelException):
    """Exception raised when an object with the constraints already exist."""

    ...

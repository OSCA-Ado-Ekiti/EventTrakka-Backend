from enum import Enum


class UserType(str, Enum):
    ROOT = "ROOT"
    ADMINISTRATOR = "ADMINISTRATOR"
    REGULAR = "REGULAR"

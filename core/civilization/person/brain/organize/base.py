from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel


if TYPE_CHECKING:
    pass


class Decision(Enum):
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class WrongSchemaException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class BaseOrganize(BaseModel, ABC):
    @abstractmethod
    def stringify(self, **kwargs):
        pass

    @abstractmethod
    def parse(self, **kwargs):
        pass

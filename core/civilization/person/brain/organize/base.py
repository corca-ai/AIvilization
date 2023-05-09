from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel

from core.logging.ansi import ANSI, Color

if TYPE_CHECKING:
    pass


class Decision(Enum):
    ACCEPT = "Accept"
    REJECT = "Reject"

    def __str__(self):
        if self == Decision.ACCEPT:
            return ANSI(self.value).to(Color.green())
        elif self == Decision.REJECT:
            return ANSI(self.value).to(Color.red())


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

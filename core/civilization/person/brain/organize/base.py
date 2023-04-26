from abc import ABC, abstractmethod
from enum import Enum
from http.client import ACCEPTED
from typing import TYPE_CHECKING

from pydantic import BaseModel

from core.civilization.person.action import Action

if TYPE_CHECKING:
    from core.civilization.person import BasePerson


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

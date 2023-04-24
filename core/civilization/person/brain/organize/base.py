from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel

from core.civilization.person.action import Action

if TYPE_CHECKING:
    from core.civilization.person import BasePerson


class BaseOrganize(BaseModel, ABC):
    @abstractmethod
    def stringify(self, **kwargs):
        pass

    @abstractmethod
    def parse(self, **kwargs):
        pass

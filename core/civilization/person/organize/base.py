from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel

from core.civilization.person.action import Action

if TYPE_CHECKING:
    from core.civilization.person import BasePerson


class BaseOrganize(BaseModel, ABC):
    @abstractmethod
    def from_prompt(self, person: BasePerson, prompt: str) -> str:
        pass

    @abstractmethod
    def to_actions(self, thought: str) -> list[Action]:
        pass

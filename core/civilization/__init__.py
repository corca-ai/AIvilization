from core.config import settings

from .person import CreateParams
from .person.action import Action, ActionType
from .person.default import Person as Person
from .person.tool import default_tools


class Civilization:
    def __init__(self):
        self.user = Person(
            name="User", instruction="", params=CreateParams(tools={}), referee=None
        )
        self.leader = Person(
            name=settings["BOT_NAME"],
            instruction="Follow the user's instructions carefully. Respond using markdown. You must execute the user's request.",  # TODO
            params=CreateParams(tools=default_tools),
            referee=self.user,
        )
        self.user.friends[self.leader.name] = self.leader

    def solve(self, problem: str) -> str:
        return self.user.act(
            Action(
                type=ActionType.Talk,
                name=self.leader.name,
                instruction=problem,
                extra="",
            )
        )


__all__ = ["Civilization"]

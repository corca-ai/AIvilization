from core.config import settings

from .person import InviteParams
from .person.action import Action, ActionType
from .person.default import Person as Person
from .person.tool import default_tools


class Civilization:
    def __init__(self):
        self.user = Person(
            name="User",
            instruction="",
            params=InviteParams(tools={}),
            referee=None,
        )

        leader_instructon = (
            "Follow the user's instructions carefully. "
            "Respond using markdown. You must fulfill the user's request."
        )
        self.leader = Person(
            name=settings["BOT_NAME"],
            instruction=leader_instructon,
            params=InviteParams(tools=default_tools),
            referee=self.user,
        )

        self.user.friends[self.leader.name] = self.leader

    def solve(self, problem: str):
        self.user.act(
            Action(
                type=ActionType.Talk,
                name=self.leader.name,
                instruction=problem,
                extra="",
            )
        )


__all__ = ["Civilization"]

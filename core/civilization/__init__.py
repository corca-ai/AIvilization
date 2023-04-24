from core.config import settings
from core.logging import Color

from .person import InviteParams
from .person.action import Action, ActionType
from .person.default import Person as Person
from .person.tool import default_tools
from .person.tracer.log import LogTracer


class Civilization:
    def __init__(self):
        self.user = Person(
            name="David",
            instruction="The person who you should give the final answer to.",
            params=InviteParams(tools={}),
            referee=None,
            color=Color.white(),
        )
        self.user.add_tracer(LogTracer)

        leader_instructon = (
            f"Follow {self.user.name}'s instructions carefully. "
            f"Respond using markdown. You must fulfill {self.user.name}'s request."
        )
        self.leader = Person(
            name=settings["BOT_NAME"],
            instruction=leader_instructon,
            params=InviteParams(tools=default_tools),
            referee=self.user,
        )
        self.leader.add_tracer(LogTracer)

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

from core.config import settings

from .person import InviteParams
from .person.action import Action, ActionType
from .person.default import Person as Person
from .person.tool import default_tools
from .person.tracer.log import LogTracer


class Civilization:
    def __init__(self):
        self.user = Person(
            name="User",
            instruction="",
            final_goal="",
            params=InviteParams(tools={}),
            referee=None,
        )
        self.user.add_tracer(LogTracer)

    def solve(self, problem: str) -> str:
        self.leader = Person(
            name=settings["BOT_NAME"],
            instruction="Follow the user's instructions carefully. Respond using markdown. You must fulfill the user's request.",  # TODO
            final_goal=problem,
            params=InviteParams(tools=default_tools),
            referee=self.user,
        )
        self.leader.add_tracer(LogTracer)

        self.user.friends[self.leader.name] = self.leader
        return self.user.act(
            Action(
                type=ActionType.Talk,
                name=self.leader.name,
                instruction=problem,
                extra="",
            )
        )


__all__ = ["Civilization"]

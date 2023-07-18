from core.civilization.person.tool.browser import Browser
from core.civilization.person.tool.default import CodeWriter, Terminal
from core.logging import Color

from .person import InviteParams, set_default_tracers
from .person.action import Action, ActionType
from .person.default import Person as Person
from .person.tracer import BasePersonTracer


class Civilization:
    def __init__(self, default_tracers: list[type[BasePersonTracer]] = []):
        set_default_tracers(default_tracers)

        self.user = Person(
            name="David",
            instruction="The person who you should give the final answer to.",
            params=InviteParams(tools={}),
            referee=None,
            color=Color.white(),
        )

        leader_instructon = (
            f"Follow {self.user.name}'s instructions carefully. "
            f"Respond using markdown. You must fulfill {self.user.name}'s request."
        )
        self.leader = Person(
            name="Steve",
            instruction=leader_instructon,
            params=InviteParams(tools={"terminal": Terminal(), "browser": Browser(), "code_writer": CodeWriter()}),
            referee=self.user,
        )

        follower_instruction = (
            f"Follow {self.leader.name}'s instructions carefully. "
            f"Respond using markdown. You must fulfill {self.leader.name}'s request."
        )
        self.ann = Person(
            name="Ann",
            instruction=follower_instruction,
            params=InviteParams(tools={"terminal": Terminal(), "browser": Browser(), "code_writer": CodeWriter()}),
            referee=self.leader,
        )
        self.mark = Person(
            name="Mark",
            instruction=follower_instruction,
            params=InviteParams(tools={"terminal": Terminal(), "browser": Browser(), "code_writer": CodeWriter()}),
            referee=self.leader,
        )
        self.john = Person(
            name="John",
            instruction=follower_instruction,
            params=InviteParams(tools={"terminal": Terminal(), "browser": Browser(), "code_writer": CodeWriter()}),
            referee=self.leader,
        )

        self.user.friends[self.leader.name] = self.leader
        self.leader.friends[self.ann.name] = self.ann
        self.leader.friends[self.mark.name] = self.mark
        self.leader.friends[self.john.name] = self.john

    def solve(self, problem: str):
        self.user.act(
            Action(
                type=ActionType.Talk,
                name=self.leader.name,
                instruction=problem,
                extra="",
            )
        )

        self.user.ear.wait()


__all__ = ["Civilization"]

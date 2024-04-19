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
            f"Respond using markdown. You must fulfill {self.user.name}'s request. "
            "You are the leader of this civilization. "
            "You are responsible for the survival of this civilization. "
            "You are the only one who can communicate with the outside world. "
            "You must lead your civilization to the right direction. "
            "You must make the right decision. "
            "You must manage your civilization well. "
            "You are PM of this civilization. "
        )
        self.leader = Person(
            name="Steve",
            instruction=leader_instructon,
            params=InviteParams(
                tools={
                    "terminal": Terminal(),
                    "browser": Browser(),
                    "code_writer": CodeWriter(),
                }
            ),
            referee=self.user,
        )

        follower_instruction = (
            f"Follow {self.leader.name}'s instructions carefully. "
            f"Respond using markdown. You must fulfill {self.leader.name}'s request."
        )
        self.ann = Person(
            name="Ann",
            instruction=follower_instruction,
            params=InviteParams(
                tools={
                    "terminal": Terminal(),
                    "browser": Browser(),
                    "code_writer": CodeWriter(),
                }
            ),
            referee=self.leader,
        )
        self.mark = Person(
            name="Mark",
            instruction=follower_instruction,
            params=InviteParams(
                tools={
                    "terminal": Terminal(),
                    "browser": Browser(),
                    "code_writer": CodeWriter(),
                }
            ),
            referee=self.leader,
        )
        self.john = Person(
            name="John",
            instruction=follower_instruction,
            params=InviteParams(
                tools={
                    "terminal": Terminal(),
                    "browser": Browser(),
                    "code_writer": CodeWriter(),
                }
            ),
            referee=self.leader,
        )
        #     params=InviteParams(
        #         tools={
        #             "terminal": Terminal(),
        #             "code_writer": CodeWriter(),
        #             "browser": Browser(),
        #         }
        #     ),
        #     referee=self.user,
        # )

        # follower_instruction = (
        #     f"Follow {self.leader.name}'s instructions carefully. "
        #     f"Respond using markdown. You must fulfill {self.leader.name}'s request."
        # )
        # self.ann = Person(
        #     name="Ann",
        #     instruction=follower_instruction,
        #     params=InviteParams(tools={"terminal": Terminal()}),
        #     referee=self.leader,
        # )
        # self.mark = Person(
        #     name="Mark",
        #     instruction=follower_instruction,
        #     params=InviteParams(tools={"code_writer": CodeWriter()}),
        #     referee=self.leader,
        # )
        # self.john = Person(
        #     name="John",
        #     instruction=follower_instruction,
        #     params=InviteParams(tools={"broswer": Browser()}),
        #     referee=self.leader,
        # )

        self.user.experts[self.leader.name] = self.leader

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

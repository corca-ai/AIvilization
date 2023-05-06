from __future__ import annotations

from typing import List, Optional, Tuple

from core.civilization.god.system import System
from core.civilization.person.action.base import Plan
from core.logging import Color

from .action import Action, ActionType
from .base import BasePerson, InviteParams, TalkParams
from .brain.default import Brain
from .tool import BaseTool, BuildParams, CodedTool, UseParams
from .tracer import Trace
from .ear.default import Ear
from .mouth.default import Mouth


class Person(BasePerson):
    def __init__(
        self,
        name: str,
        instruction: str,
        params: InviteParams,
        referee: BasePerson,
        color: Optional[Color] = None,
    ):
        super().__init__(
            name=name,
            instruction=instruction,
            params=params,
            referee=referee,
            color=color or Color.rgb(),
        )
        self.tools: dict[str, BaseTool] = params.tools

        self.brain = Brain(self, name, instruction)

        self.friends: dict[str, Person] = {}
        if referee:
            self.friends[referee.name] = referee

        self.ear = Ear(self)
        self.mouth = Mouth(self)

    @Trace.respond()
    def respond(self, sender: Person, request: str, params: TalkParams) -> str:
        request = request.split(System.PROMPT_SEPARATOR)[1].strip()

        while True:
            plans = self.plan(request)
            result, is_finish = self.execute(plans[0], sender=sender)

            if is_finish:
                self.mouth.talk(sender.ear.port, result, "")
                return result

    def plan(self, request: str) -> List[Plan]:
        opinions = []

        while True:
            plans = self.brain.plan(request, opinions)
            opinion, ok = self.brain.optimize(request, plans)

            if ok:
                return plans

            opinions.append(opinion)

    def execute(self, plan: Plan, sender: Person) -> Tuple[str, bool]:
        opinions = []

        while True:
            action = self.brain.execute(plan, opinions)

            if action.type == ActionType.Talk and action.name == sender.name:
                return self.to_format(action.instruction), True

            result = self.act(action)
            opinion, ok = self.brain.review(plan, action, result)

            if ok:
                return result, False

            opinions.append(opinion)

    @Trace.act()
    def act(self, action: Action) -> str:
        try:
            method = getattr(self, action.type.value.lower())
            return method(action.name, action.instruction, action.extra)
        except KeyError:
            return f"Unknown action type '{action.type}'"

    def invite(self, name: str, instruction: str, extra: str) -> str:
        if name in self.friends:
            return System.error(f"Friend {name} already exists.")

        friend = Person(
            name,
            instruction,
            InviteParams.from_str(extra, self.tools),
            referee=self,
        )
        self.friends[name] = friend

        return friend.greeting()

    def talk(self, name: str, instruction: str, extra: str):
        # TODO: break a relationship with a friend
        if name not in self.friends:
            return System.error(f"Friend {name} not found.")

        friend = self.friends[name]
        self.mouth.talk(friend.ear.port, instruction, extra)

    def build(self, name: str, instruction: str, extra: str) -> str:
        if name in self.friends:
            return System.error(f"Tool {name} already exists.")

        tool = CodedTool(name=name, instruction=instruction)
        tool.build(params=BuildParams.from_str(extra))
        self.tools[name] = tool

        return tool.greeting()

    def use(self, name: str, instruction: str, extra: str) -> str:
        if name not in self.tools:
            return System.error(f"Tool {name} not found.")

        # TODO: delete tool by instruction
        tool = self.tools[name]
        result = tool.use(instruction, UseParams.from_str(extra))
        return tool.to_format(result)

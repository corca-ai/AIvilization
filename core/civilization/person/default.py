from __future__ import annotations

from typing import List, Optional, Tuple

from core.civilization.god.system import System
from core.civilization.person.action.base import Plan
from core.logging import Color

from .action import Action
from .base import BasePerson, InviteParams, TalkParams
from .brain.default import Brain
from .ear.default import Ear
from .mouth.default import Mouth
from .tool import BaseTool, BuildParams, CodedTool, UseParams


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

        self.experts: dict[str, Person] = {}
        if referee:
            self.experts[referee.name] = referee

        self.ear = Ear(self)
        self.mouth = Mouth(self)

    def respond(self, sender: Person, request: str, params: TalkParams) -> str:
        self.tracer.on_request(sender, request, params)

        request = request.split(System.PROMPT_SEPARATOR)[1].strip()

        constraints = []
        while True:
            plans = self.plan(request, constraints)
            is_plan_valid = True

            for plan in plans:
                result, is_plan_valid = self.execute(plan, sender=sender)

                if not is_plan_valid:
                    break

            if not is_plan_valid:
                constraints.append(result)
                continue

            self.mouth.talk(sender.ear, result, "")
            self.tracer.on_response(sender, result)
            return result

    def plan(self, request: str, constraints: list[str]) -> list[Plan]:
        opinions = []

        while True:
            plans = self.brain.plan(request, opinions, constraints)
            self.tracer.on_plans(plans)
            opinion, ok = self.brain.optimize(request, plans)
            self.tracer.on_optimize(opinion, ok)

            if ok:
                return plans

            opinions.append(opinion)

    def execute(self, plan: Plan, sender: Person) -> Tuple[str, bool]:
        opinions = []

        action = self.brain.execute(plan, opinions)

        result = self.act(action)
        opinion, ok = self.brain.review(plan, action, result)
        self.tracer.on_review(opinion, ok)

        if ok:
            return result, True

        return opinion, False

    def act(self, action: Action) -> str:
        self.tracer.on_act(action)
        try:
            method = getattr(self, action.type.value.lower())
            result = method(action.name, action.instruction, action.extra)
            self.tracer.on_act_result(action, result)
            return result
        except KeyError as e:
            self.tracer.on_act_error(action, e)
            return f"Unknown action type '{action.type}'"
        except Exception as e:
            self.tracer.on_act_error(action, e)
            return f"Error while execution: {e}"

    def invite(self, name: str, instruction: str, extra: str) -> str:
        if name in self.experts:
            return System.error(f"Friend {name} already exists.")

        expert = Person(
            name,
            instruction,
            InviteParams.from_str(extra, self.tools),
            referee=self,
        )
        self.experts[name] = expert

        return expert.greeting()

    def talk(self, name: str, instruction: str, extra: str) -> str:
        # TODO: break a relationship with a expert
        if name not in self.experts:
            return System.error(f"Friend {name} not found.")

        expert = self.experts[name]
        self.mouth.talk(expert.ear, instruction, extra)

        return System.announcement(f"{self.name} talks to {name}")

    def build(self, name: str, instruction: str, extra: str) -> str:
        if name in self.experts:
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

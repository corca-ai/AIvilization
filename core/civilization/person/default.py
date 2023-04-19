from typing import Optional

from core.civilization.god.system import System
from core.logging import Color

from .action import Action, ActionType
from .base import BasePerson, InviteParams, TalkParams
from .brain.default import Brain
from .organize.template import TemplateOrganize as Organize
from .tool import BaseTool, BuildParams, CodedTool, UseParams
from .tracer import Trace


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

        self.brain = Brain(name, instruction)

        self.friends: dict[str, "Person"] = {}
        if referee:
            self.friends[referee.name] = referee
        self.organize = Organize()

    @Trace.respond()
    def respond(self, sender: "Person", prompt: str, params: TalkParams) -> str:
        while True:
            idea = self.to_idea(prompt)
            thought = self.think(idea)
            actions = self.to_actions(thought)
            next_action = actions[0]
            if next_action.type == ActionType.Talk and next_action.name == sender.name:
                return self.to_format(next_action.instruction)
            result = self.act(next_action)
            prompt = result

    @Trace.to_idea()
    def to_idea(self, prompt: str) -> str:
        return self.organize.from_prompt(self, prompt)

    @Trace.think()
    def think(self, idea: str) -> str:
        return self.brain.think(idea)

    @Trace.to_actions()
    def to_actions(self, thought: str) -> list[Action]:
        return self.organize.to_actions(self, thought)

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

    def talk(self, name: str, instruction: str, extra: str) -> str:
        # TODO: break a relationship with a friend
        if name not in self.friends:
            return System.error(f"Friend {name} not found.")

        friend = self.friends[name]

        return friend.respond(
            self,
            self.to_format(instruction),
            TalkParams.from_str(extra),
        )

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

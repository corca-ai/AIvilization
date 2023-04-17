import re

from core.civilization.god.system import System
from core.logging import Color

from .action import Action, ActionType
from .base import BasePerson, InviteParams, Log, TalkParams
from .brain.default import Brain as Brain
from .organize.template import TemplateOrganize as Organize
from .tool import BuildParams, UseParams
from .tool.base import BaseTool
from .tool.coded import CodedTool


class Person(BasePerson):
    def __init__(
        self, name: str, instruction: str, params: InviteParams, referee: "Person"
    ):
        super().__init__(
            name=name, instruction=instruction, params=params, referee=referee
        )
        self.memory = []
        self.tools: dict[str, BaseTool] = params.tools
        # self.channels: list[str] = kwargs["channels"] # TODO

        self.brain = Brain(name, instruction, self.memory)

        self.friends: dict[str, "Person"] = {}
        self.organize = Organize()

    @Log.respond(log_level="info")
    def respond(self, sender: "Person", prompt: str, params: TalkParams) -> str:
        memory = []

        while True:
            idea = self.organize.from_prompt(self, prompt)
            thought = self.brain.think(idea)
            actions = self.organize.to_actions(thought)
            next_action = actions[0]
            result = self.act(next_action)
            if next_action.type == ActionType.Answer:
                return self.to_format(result)

            memory.append((prompt, thought, result))
            prompt = result

    @Log.act(log_level="info")
    def act(self, action: Action) -> str:
        try:
            method = getattr(self, action.type.value.lower())
            return method(action.name, action.instruction, action.extra)
        except KeyError:
            raise ValueError(f"Unknown action type '{type}'")

    def invite(self, name: str, instruction: str, extra: str) -> str:
        if name in self.friends:
            return System.error(f"Friend {name} already exists.")

        friend = Person(
            name, instruction, InviteParams.from_str(extra, self.tools), referee=self
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

    def answer(self, name: str, instruction: str, extra: str):
        return f"{instruction}\nExtra: {extra}"

    def invite(self, channel: str):  # TODO
        pass

import re

from core.civilization.god.system import System
from core.logging import Color

from .action import Action, ActionType
from .base import BasePerson, CreateParams, Log, TalkParams
from .brain.default import Brain as Brain
from .organize.template import TemplateOrganize as Organize
from .tool import BaseTool, BuildParams, UseParams
from .tool.coded import CodedTool as Tool


class Person(BasePerson):
    def __init__(
        self,
        name: str,
        instruction: str,
        final_goal: str,
        params: CreateParams,
        referee: BasePerson,
    ):
        super().__init__(
            name=name,
            instruction=instruction,
            final_goal=final_goal,
            params=params,
            referee=referee,
        )
        self.color = Color.rgb(r=128)
        self.memory = []
        self.tools: dict[str, BaseTool] = params.tools
        # self.channels: list[str] = kwargs["channels"] # TODO

        self.brain = Brain(name, instruction, self.memory)

        self.friends: dict[str, BasePerson] = {}
        self.organize = Organize()

    @Log.respond(log_level="info")
    def respond(self, sender: BasePerson, prompt: str, params: TalkParams) -> str:
        memory = []

        while True:
            idea = self.to_idea(prompt)
            thought = self.think(idea)
            actions = self.to_actions(thought)
            next_action = actions[0]
            result = self.act(next_action)
            if next_action.type == ActionType.Answer:
                return result

            memory.append((prompt, thought, result))
            prompt = result

    @Log.to_idea(log_level="debug")
    def to_idea(self, prompt: str) -> str:
        return self.organize.from_prompt(self, prompt)

    @Log.think(log_level="debug")
    def think(self, idea: str) -> str:
        return self.brain.think(idea)

    @Log.to_actions(log_level="debug")
    def to_actions(self, thought: str) -> list[Action]:
        return self.organize.to_actions(thought)

    @Log.act(log_level="info")
    def act(self, action: Action) -> str:
        try:
            method = getattr(self, action.type.value.lower())
            return method(action.name, action.instruction, action.extra)
        except KeyError:
            raise ValueError(f"Unknown action type '{type}'")

    def create(self, name: str, instruction: str, extra: str) -> str:
        if name in self.friends:
            return System.error(f"Friend {name} already exists.")

        friend = Person(
            name,
            instruction,
            self.final_goal,
            CreateParams.from_str(extra),
            referee=self,
        )
        self.friends[name] = friend

        return (
            f"{name}'s talk\n{System.PROMPT_SEPARATOR}\n"
            + "Hello, I am "
            + name
            + ".\n"
        )

    def talk(self, name: str, instruction: str, extra: str) -> str:
        # TODO: break a relationship with a friend
        if name not in self.friends:
            return System.error(f"Friend {name} not found.")

        return f"{name}'s talk\n{System.PROMPT_SEPARATOR}\n" + self.friends[
            name
        ].respond(
            self,
            f"{self.name}'s talk\n{System.PROMPT_SEPARATOR}\n" + instruction,
            TalkParams.from_str(extra),
        )

    def build(self, name: str, instruction: str, extra: str) -> str:
        if name in self.friends:
            return System.error(f"Tool {name} already exists.")

        self.tools[name] = Tool(name=name, instruction=instruction)
        self.tools[name].build(params=BuildParams.from_str(extra))

        return (
            f"{name}'s result\n{System.PROMPT_SEPARATOR}\n"
            + f"You have built a tool named {name}. Test if you can use the tool well."
        )

    def use(self, name: str, instruction: str, extra: str) -> str:
        if name not in self.tools:
            return System.error(f"Tool {name} not found.")

        # TODO: delete tool by instruction
        return f"{name}'s result\n{System.PROMPT_SEPARATOR}\n" + self.tools[name].use(
            instruction,
            UseParams.from_str(extra),
        )

    def answer(self, name: str, instruction: str, extra: str):
        return f"{instruction}"

    def invite(self, channel: str):  # TODO
        pass

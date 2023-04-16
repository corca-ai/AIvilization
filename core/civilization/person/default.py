import re

from core.civilization.god.system import System
from core.logging import Color

from .action import Action, ActionType
from .base import BasePerson, CreateParams, Log, TalkParams
from .brain.default import DefaultBrain as Brain
from .tool import BuildParams, UseParams
from .tool.coded import CodedTool as Tool


class Person(BasePerson):
    def __init__(
        self, name: str, instruction: str, params: CreateParams, referee: BasePerson
    ):
        super().__init__(
            name=name, instruction=instruction, params=params, referee=referee
        )
        self.color = Color.rgb(r=128)
        self.memory = []
        self.tools: dict[str, Tool] = params.tools
        # self.channels: list[str] = kwargs["channels"] # TODO

        self.brain = Brain(name, instruction, self.memory)

        self.friends: dict[str, BasePerson] = {}

    @Log.respond(log_level="info")
    def respond(self, sender: BasePerson, prompt: str, params: TalkParams) -> str:
        memory = []

        while True:
            idea = self.organize(prompt)
            thought = self.brain.think(idea)
            actions = Person.parse_thought(thought)
            next_action = actions[0]
            result = self.act(next_action)
            if next_action.type == ActionType.Answer:
                return result

            memory.append((prompt, thought, result))
            prompt = result

    @Log.organize(log_level="debug")
    def organize(self, prompt: str) -> str:
        friend_names = ", ".join([name for name in self.friends.keys()])
        tool_names = ", ".join([name for name in self.tools.keys()])
        friends = "".join(
            [
                f"\n    {name}: {person.instruction}"
                for name, person in self.friends.items()
            ]
        )
        tools = "".join(
            [f"\n    {name}: {tool.instruction}" for name, tool in self.tools.items()]
        )
        return System.TEMPLATE.format(
            friend_names=friend_names,
            tool_names=tool_names,
            friends=friends,
            tools=tools,
            prompt=prompt,
            referee=self.referee.name,
        )

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

        friend = Person(name, instruction, CreateParams.from_str(extra), referee=self)
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
        self.tools[name].build(BuildParams.from_str(extra))

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

    @Log.parse_thought(log_level="debug")
    @staticmethod
    def parse_thought(thought: str) -> list[Action]:
        pattern = r"Type:\s+(\w+)\s+Name:\s+(\w+)\s+Instruction:\s+((?:(?!\nExtra:).)+)\nExtra:\s*((?:(?!\nType:).)*)"
        matches = re.findall(pattern, thought, re.DOTALL)

        if len(matches) == 0:
            raise Exception("parse error")

        result = [
            Action(
                type=ActionType[match[0]],
                name=match[1],
                instruction=match[2],
                extra=match[3],
            )
            for match in matches
        ]
        return result

    def invite(self, channel: str):  # TODO
        pass

import logging
import os
import re
import readline
import subprocess
from abc import ABC, abstractmethod
from enum import Enum

import openai
from pydantic import BaseModel

from core.config import settings
from core.logging import ANSI, Color, Style, logger
from core.terminal.tracer import StdoutTracer

openai.api_key = settings["OPENAI_API_KEY"]

TEMPLATE = """Your response should be in the following schema:

Plan: Each plan should be concise and clear to achieve the goal.
- [ ] plan #1
- [ ] plan #2

Type:
Name:
Instruction:
Extra:

The action types you can use are:
Type | Description | Name | Instruction | Extra
-|-|-|-|-
Create | Create a friend you need. | Friend's Name (usual person name) | Friend's Personality | Friend's Default Tools
Talk |  Talk to your friends. | Friend's Name (should be one of [{friend_names}]) | Message | Attachment File List
Build | Build or rebuild a new tool when you can't do it yourself. It must have stdout, stderr messages. It should be executable with the following schema of commands: `python tools/example.py instruction extra` | Tool's Name (snake_case) | Tool Description | Python Code (not exceeding 100 lines) for Building Tools
Use | Use one of your tools. | Tool's Name (should be one of [{tool_names}]) | Tool's Input | Tool's Args
Answer | Answer to {referee} | {referee} | Answer | Attachment File List

Your friends:{friends}
Your tools:{tools}

{prompt}
"""

PROMPT_SEPARATOR = "===================="


class CreateParams(BaseModel):
    tools: dict
    # channels: list[str] # TODO

    @staticmethod
    def from_str(content: str):
        return CreateParams(tools={})


class TalkParams(BaseModel):
    attachment: list[str]

    @staticmethod
    def from_str(content: str):
        return TalkParams(attachment=[])


class BuildParams(BaseModel):
    code: str

    @staticmethod
    def from_str(content: str):
        match = re.search(r"```python(.*?)```", content, re.DOTALL)
        if not match:
            return BuildParams(code="")

        code = match.group(1).strip()
        return BuildParams(code=code)


class UseParams(BaseModel):
    input: str

    @staticmethod
    def from_str(content: str):
        return UseParams(input=content)


class System:
    ERROR_MESSAGE = "error message\n"
    ANNOUNCEMENT_MESSAGE = "announcement\n"

    @staticmethod
    def error(message: str) -> str:
        return System.ERROR_MESSAGE + PROMPT_SEPARATOR + "\n" + message

    @staticmethod
    def announcement(message: str) -> str:
        return System.ANNOUNCEMENT_MESSAGE + PROMPT_SEPARATOR + "\n" + message


class BaseLLM(ABC):
    @abstractmethod
    def chat_completion(self, prompt: str) -> str:
        pass


class OpenAILLM(BaseLLM, BaseModel):
    model: str = "gpt-4"

    def chat_completion(self, messages: list[dict]) -> str:
        level = logger.level
        logger.setLevel(logging.ERROR)
        result = openai.ChatCompletion.create(
            model=self.model, messages=messages, temperature=0.7, max_tokens=2048
        )["choices"][0]["message"]["content"]
        logger.setLevel(level)
        return result


class Brain:
    llm = OpenAILLM()

    def __init__(self, name: str, instruction: str, memory: list[dict]):
        content = f"Your name is {name}. {instruction}"
        self.stm = [{"role": "system", "content": content}] + (memory if memory else [])

    def think(self, prompt: str) -> str:
        result = self.llm.chat_completion(
            self.stm + [{"role": "user", "content": prompt}]
        )
        self.stm.append({"role": "user", "content": prompt.split(PROMPT_SEPARATOR)[1]})
        self.stm.append({"role": "assistant", "content": result})
        return result


class Tool:
    def __init__(self, name: str, instruction: str, params: BuildParams):
        self.name = name
        self.instruction = instruction
        self.color = Color.rgb(g=128)

        self.file_path = f"tools/{name}.py"
        os.makedirs("tools", exist_ok=True)
        with open(self.file_path, "w") as f:
            f.write(params.code)

    def use(self, prompt: str, params: UseParams) -> str:
        process = subprocess.Popen(
            ["python", self.file_path, prompt, params.input],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        tracer = StdoutTracer(
            process,
            on_output=lambda p, o: logger.info(
                ANSI(p).to(Style.dim()) + " " + o.strip("\n")
            ),
        )
        _, output = tracer.wait_until_stop_or_exit()
        return output

    def __str__(self):
        return ANSI((f"{self.name}({self.__class__.__name__})").center(20)).to(
            self.color, Style.bold()
        )


class ActionType(Enum):
    Respond = "Respond"
    Create = "Create"
    Talk = "Talk"
    Build = "Build"
    Use = "Use"
    Answer = "Answer"

    def __str__(self):
        return ANSI((self.value.lower() + "s ").center(12)).to(
            Color.rgb(210, 210, 210), Style.italic(), Style.dim()
        )


class Action(BaseModel):
    type: ActionType
    name: str
    instruction: str
    extra: str


class Log:
    def organize(log_level: str):
        def decorator(func):
            def wrapper(self, prompt: str):
                idea = func(self, prompt)
                try:
                    getattr(logger, log_level)(ANSI(idea).to(Color.rgb(144, 144, 144)))
                except KeyError as e:
                    logger.error("Failed to log organize: " + str(e))

                return idea

            return wrapper

        return decorator

    def respond(log_level: str):
        def decorator(func):
            def wrapper(
                self: "Person", sender: "Person", prompt: str, params: TalkParams
            ):
                result = func(self, sender, prompt, params)

                try:
                    getattr(logger, log_level)(
                        str(self)
                        + str(ActionType.Respond)
                        + str(sender)
                        + " | "
                        + ANSI(result).to(Color.white())
                    )
                except KeyError as e:
                    logger.error("Failed to log respond: " + str(e))

                return result

            return wrapper

        return decorator

    def act(log_level: str):
        def get_target(self, type: ActionType, name: str):
            if type in [ActionType.Create, ActionType.Talk]:
                return self.friends[name]
            elif type in [ActionType.Build, ActionType.Use]:
                return self.tools[name]

        def decorator(func):
            def wrapper(self, action: Action):
                f = lambda target: (
                    str(self)
                    + str(action.type)
                    + ANSI(str(target)).to(Color.green(), Style.bold())
                    + " | "
                    + ANSI(action.instruction).to(Color.white())
                    + "\n"
                    + ANSI(action.extra).to(Style.dim())
                )

                if action.type in [ActionType.Talk, ActionType.Use]:
                    try:
                        getattr(logger, log_level)(
                            f(get_target(self, action.type, action.name))
                        )
                    except KeyError as e:
                        logger.error("Failed to log act: " + str(e))

                result = func(self, action)

                if action.type in [ActionType.Create, ActionType.Build]:
                    try:
                        getattr(logger, log_level)(
                            f(get_target(self, action.type, action.name))
                        )
                    except KeyError as e:
                        logger.error("Failed to log act: " + str(e))

                return result

            return wrapper

        return decorator

    def parse_thought(log_level: str):
        def decorator(func):
            def wrapper(thought: str):
                try:
                    getattr(logger, log_level)(
                        ANSI(thought).to(Color.rgb(208, 208, 208))
                    )
                except KeyError as e:
                    logger.error("Failed to log parse_thought: " + str(e))

                return func(thought)

            return wrapper

        return decorator


class Person:
    def __init__(
        self, name: str, instruction: str, params: CreateParams, referee: "Person"
    ):
        self.name = name
        self.instruction = instruction
        self.color = Color.rgb(r=128)
        self.memory = []
        self.tools: dict[str, Tool] = params.tools
        # self.channels: list[str] = kwargs["channels"] # TODO

        self.brain = Brain(name, instruction, self.memory)

        self.referee: "Person" = referee
        self.friends: dict[str, Person] = {}

    @Log.respond(log_level="info")
    def respond(self, sender: "Person", prompt: str, params: TalkParams) -> str:
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
        return TEMPLATE.format(
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

        return f"{name}'s talk\n{PROMPT_SEPARATOR}\n" + "Hello, I am " + name + ".\n"

    def talk(self, name: str, instruction: str, extra: str) -> str:
        # TODO: break a relationship with a friend
        if name not in self.friends:
            return System.error(f"Friend {name} not found.")

        return f"{name}'s talk\n{PROMPT_SEPARATOR}\n" + self.friends[name].respond(
            self,
            f"{self.name}'s talk\n{PROMPT_SEPARATOR}\n" + instruction,
            TalkParams.from_str(extra),
        )

    def build(self, name: str, instruction: str, extra: str) -> str:
        if name in self.friends:
            return System.error(f"Tool {name} already exists.")

        self.tools[name] = Tool(name, instruction, BuildParams.from_str(extra))
        return (
            f"{name}'s result\n{PROMPT_SEPARATOR}\n"
            + f"You have built a tool named {name}. Test if you can use the tool well."
        )

    def use(self, name: str, instruction: str, extra: str) -> str:
        if name not in self.tools:
            return System.error(f"Tool {name} not found.")

        # TODO: delete tool by instruction
        return f"{name}'s result\n{PROMPT_SEPARATOR}\n" + self.tools[name].use(
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

    def __str__(self):
        return ANSI((f"{self.name}({self.__class__.__name__})").center(20)).to(
            self.color, Style.bold()
        )


class Civilization:
    def __init__(self, default_tools: dict[str, Tool]):
        self.default_tools = default_tools

        self.user = Person(
            name="User", instruction="", params=CreateParams(tools={}), referee=None
        )
        self.leader = Person(
            name=settings["BOT_NAME"],
            instruction="Follow the user's instructions carefully. Respond using markdown. You must execute the user's request.",  # TODO
            params=CreateParams(tools=self.default_tools),
            referee=self.user,
        )
        self.user.friends[self.leader.name] = self.leader

    def solve(self, problem: str) -> str:
        return self.user.act(
            Action(
                type=ActionType.Talk,
                name=self.leader.name,
                instruction=problem,
                extra="",
            )
        )


if __name__ == "__main__":
    civilization = Civilization({})
    while True:
        try:
            problem = input(">>> ")
            civilization.solve(problem)

            readline.add_history(problem)
        except KeyboardInterrupt:
            print()
            continue
        except EOFError:
            logger.info("Bye!")
            break

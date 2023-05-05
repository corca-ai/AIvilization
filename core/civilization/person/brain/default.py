from argparse import Action
from typing import Generator, List, Tuple

from core.civilization.person.action.base import Plan
from core.civilization.person.base import BasePerson
from core.civilization.person.brain.organize.base import BaseOrganize
from core.civilization.person.brain.organize.execute import Executor
from core.civilization.person.brain.organize.optimize import Optimizer
from core.civilization.person.brain.organize.plan import Planner
from core.civilization.person.brain.organize.review import Reviewer
from core.config.env import settings
from core.logging.ansi import ANSI, Color, Style

from .base import BaseBrain
from .llm.openai import OpenAILLM
from .memory import BaseMemory, LongTermMemory, ShortTermMemory


class Brain(BaseBrain):
    person: BasePerson = None
    sterm_memory: BaseMemory[list[dict[str, str]]] = None
    lterm_memory: BaseMemory[str] = None

    planner: BaseOrganize = None
    optimizer: BaseOrganize = None
    executor: BaseOrganize = None
    reviewer: BaseOrganize = None

    init_message: str = "Your name is {name}. {instruction}"

    def __init__(self, person: BasePerson, name: str, instruction: str):
        super().__init__(llm=OpenAILLM())
        self.lterm_memory = (
            LongTermMemory(name, instruction) if settings["PINECONE_API_KEY"] else None
        )
        self.sterm_memory = ShortTermMemory(name, instruction, self.init_message)

        self.person = person
        self.planner = Planner()
        self.optimizer = Optimizer()
        self.executor = Executor()
        self.reviewer = Reviewer()

    def plan(self, request: str, opinions: List[str]) -> List[Plan]:
        prompt = self.planner.stringify(self.person, request, opinions)
        print(ANSI(prompt).to(Color.rgb(236, 201, 238)))

        result = ""
        for t in self.__think(prompt):
            result += t
            print(ANSI(t).to(Style.dim()), end="")
        print("\n")

        return self.planner.parse(self.person, result)

    def optimize(self, request: str, plans: List[Plan]) -> Tuple[str, bool]:
        prompt = self.optimizer.stringify(self.person, request, plans)
        print(ANSI(prompt).to(Color.rgb(236, 201, 238)))

        result = ""
        for t in self.__think(prompt):
            result += t
            print(ANSI(t).to(Style.dim()), end="")
        print("\n")

        opinion, ok = self.optimizer.parse(self.person, result)
        if ok:
            self.sterm_memory.save(
                "Make a plan to respond to the request. Request is:\n" + request,
                "\n".join(map(str, plans)),
            )
        return opinion, ok

    def execute(self, plan: Plan, opinions: str) -> Action:
        prompt = self.executor.stringify(self.person, plan, opinions)
        print(ANSI(prompt).to(Color.rgb(236, 201, 238)))

        result = ""
        for t in self.__think(prompt):
            result += t
            print(ANSI(t).to(Style.dim()), end="")
        print("\n")

        return self.executor.parse(self.person, result)

    def review(self, plan: str, action: Action, result: str) -> Tuple[str, bool]:
        prompt = self.reviewer.stringify(self.person, plan, action, result)
        print(ANSI(prompt).to(Color.rgb(236, 201, 238)))

        result = ""
        for t in self.__think(prompt):
            result += t
            print(ANSI(t).to(Style.dim()), end="")
        print("\n")

        opinion, ok = self.reviewer.parse(self.person, result)
        if ok:
            self.sterm_memory.save("Execute this plan:\n" + str(plan), result)
        return opinion, ok

    def __think(self, prompt: str) -> Generator[str, None, None]:
        print(self.sterm_memory.storage)
        messages = self.sterm_memory.load(prompt)

        for thought in self.llm.chat_completion(messages):
            yield thought["choices"][0]["delta"].get("content", "")

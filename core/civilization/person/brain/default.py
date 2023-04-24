from argparse import Action
from typing import Generator, List

from core.civilization.person.action.base import Plan
from core.civilization.person.base import BasePerson
from core.civilization.person.brain.organize.base import BaseOrganize
from core.civilization.person.brain.organize.execute import Executor
from core.civilization.person.brain.organize.optimize import Optimizer
from core.civilization.person.brain.organize.plan import Planner
from core.civilization.person.brain.organize.review import Reviewer

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

    def __init__(self, person: BasePerson, name: str, instruction: str):
        super().__init__(llm=OpenAILLM())
        self.lterm_memory = LongTermMemory(name, instruction)
        self.sterm_memory = ShortTermMemory(name, instruction)
        self.sterm_memory.storage.append(
            {
                "role": "system",
                "content": f"Your name is {name}. {instruction}",
            }
        )
        self.person = person
        self.planner = Planner()
        self.optimizer = Optimizer()
        self.executor = Executor()
        self.reviewer = Reviewer()

    def plan(self, request: str, opinion: str) -> List[Plan]:
        prompt = self.planner.stringify(self.person, request, opinion)

        result = "".join([t for t in self.__think(prompt)])
        print(result)

        return self.planner.parse(self.person, result)

    def optimize(self, plans: List[Plan]) -> str:
        prompt = self.optimizer.stringify(self.person, plans)

        result = "".join([t for t in self.__think(prompt)])

        return self.optimizer.parse(self.person, result)

    def execute(self, prompt: str) -> Action:
        prompt = self.executor.stringify(self.person, prompt)

        result = "".join([t for t in self.__think(prompt)])

        return self.executor.parse(self.person, result)

    def review(self, action: Action, result: str) -> str:
        prompt = self.reviewer.stringify(self.person, action, result)

        result = "".join([t for t in self.__think(prompt)])

        return self.reviewer.parse(self.person, result)

    def __think(self, prompt: str) -> Generator[str, None, None]:
        prompt = self.sterm_memory.load(prompt)

        for thought in self.llm.chat_completion(prompt):
            yield thought["choices"][0]["delta"].get("content", "")

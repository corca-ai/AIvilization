import re
import uuid

import pinecone

from core.civilization.god.system import System
from core.config.env import settings
from core.logging.logger import logger

from .base import BaseBrain
from .llm.openai import OpenAILLM
from .vector.openai import OpenAIVector


class Brain(BaseBrain):
    _PLAN_PATTERN = r"- \[(?:x| )\]\s+(.+)\n"

    def __init__(self, name: str, instruction: str, memory: list[dict]):
        pinecone.init(api_key=settings["PINECONE_API_KEY"], environment="us-east1-gcp")
        index = pinecone.Index(settings["PINECONE_INDEX"])
        # index.delete(delete_all=True)

        super().__init__(
            llm=OpenAILLM(),
            vector=OpenAIVector(),
            ltm=index,
            stm=[{"role": "system", "content": f"Your name is {name}. {instruction}"}]
            + (memory if memory else []),
            name=name,
            instruction=instruction,
        )

    def think(self, prompt: str) -> str:
        result = self.llm.chat_completion(
            self.stm + [{"role": "user", "content": prompt}]
        )
        self.stm.append(
            {"role": "user", "content": self.remove_guide(prompt)},
        )
        self.stm.append({"role": "assistant", "content": result})

        plans = re.findall(self._PLAN_PATTERN, result, re.DOTALL)
        vectors = [
            pinecone.Vector(
                id=f"{self.name}-{uuid.uuid4()}", values=self.vector.embedding(plan)
            )
            for plan in plans
        ]
        if vectors:
            self.ltm.upsert(vectors=vectors)
        return result

    def memo(self, plan: list[str]) -> str:
        pass

    def remove_guide(self, content: str) -> str:
        return content.split(System.MESSAGE_SEPARATOR)[1]

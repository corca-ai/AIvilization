import openai
import pinecone

from core.config import settings

from .base import BaseMemory
from .vector.openai import OpenAIVector

openai.api_key = settings["OPENAI_API_KEY"]

import re


class LongTermMemory(BaseMemory):
    _PLAN_PATTERN = r"- \[(?:x| )\]\s+(.+)\n"

    def __init__(self, name: str, instruction: str):
        pinecone.init(api_key=settings["PINECONE_API_KEY"], environment="us-east1-gcp")
        index = pinecone.Index(settings["PINECONE_INDEX"])

        vector = OpenAIVector()

        super().__init__(
            name=name,
            instruction=instruction,
            storage=index,
            change_to_memory=lambda x: vector.embedding(x),
        )

    def load(self, prompt: str) -> str:
        return prompt  # TODO

    def save(self, prompt: str, thought: str) -> None:
        plans = re.findall(LongTermMemory._PLAN_PATTERN, thought, re.DOTALL)
        vectors = [
            pinecone.Vector(
                id=LongTermMemory.get_plan_id(self.name, i),
                values=self.change_to_memory(plan),
                metadata={"name": self.name},
            )
            for i, plan in enumerate(plans)
        ]
        if vectors:
            self.storage.upsert(vectors=vectors)

    @staticmethod
    def get_plan_id(name: str, index: int) -> str:
        return f"{name}-plan#{index}"

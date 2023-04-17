import logging

import openai
from pydantic import BaseModel

from core.config import settings
from core.logging import logger

from .base import BaseMemory

openai.api_key = settings["OPENAI_API_KEY"]


class OpenAIMemory(BaseMemory, BaseModel):
    model: str = "text-embedding-ada-002"

    def embedding(self, prompt: str) -> str:
        level = logger.level
        logger.setLevel(logging.ERROR)
        result = openai.Embedding.create(model=self.model, input=[prompt])["data"][0][
            "embedding"
        ]
        logger.setLevel(level)
        return result

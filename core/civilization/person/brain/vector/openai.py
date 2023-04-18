import logging

import openai
from pydantic import BaseModel

from core.config import settings
from core.logging import logger

from .base import BaseVector

openai.api_key = settings["OPENAI_API_KEY"]


class OpenAIVector(BaseVector, BaseModel):
    model: str = "text-embedding-ada-002"

    def embedding(self, prompt: str) -> list[float]:
        level = logger.level
        logger.setLevel(logging.ERROR)
        result = openai.Embedding.create(model=self.model, input=[prompt])["data"][0][
            "embedding"
        ]
        logger.setLevel(level)
        return result

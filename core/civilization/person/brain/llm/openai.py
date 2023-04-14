import logging

import openai
from pydantic import BaseModel

from core.config import settings
from core.logging import logger

from .base import BaseLLM

openai.api_key = settings["OPENAI_API_KEY"]


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

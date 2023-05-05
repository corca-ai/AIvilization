from typing import Dict, Generator, List

import openai
from pydantic import BaseModel
from retry import retry

from core.config import settings
from core.logging import logger

from .base import BaseLLM

openai.api_key = settings["OPENAI_API_KEY"]


class OpenAILLM(BaseLLM, BaseModel):
    MAX_RETRIES = 3
    DELAY = 3
    model: str = "gpt-4"

    @retry(
        (
            openai.error.RateLimitError,
            openai.error.Timeout,
            openai.error.APIError,
            openai.error.APIConnectionError,
            openai.error.ServiceUnavailableError,
        ),
        tries=MAX_RETRIES,
        delay=DELAY,
    )
    @logger.disable
    def chat_completion(self, messages: List[Dict[str, str]]) -> Generator:
        return openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            stream=True,
        )

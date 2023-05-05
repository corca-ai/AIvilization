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
    model = "gpt-4"

    def __init__(
        self,
        model: str = "gpt-4",
    ) -> None:
        super().__init__()
        self.model = model

    # https://platform.openai.com/docs/api-reference/chat/create
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
    def chat_completion(
        self,
        messages: list[dict],
        temparture: float = 0.7,
        top_p: float = 1.0,
        max_tokens: int = 2048,
        stream: bool = True,
        **kargs,
    ) -> Generator:
        return openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=temparture,
            top_p=top_p,
            max_tokens=max_tokens,
            stream=stream,
            **kargs,
        )

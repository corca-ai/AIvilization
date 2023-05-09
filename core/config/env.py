import os
from typing import TypedDict

from dotenv import load_dotenv

load_dotenv()


class DotEnv(TypedDict):
    LOG_LEVEL: str  # optional
    BOT_NAME: str  # optional
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str  # optional
    PINECONE_INDEX: str  # optional
    REDIS_HOST: str  # optional
    REDIS_PORT: str  # optional


settings: DotEnv = {
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    "BOT_NAME": os.getenv("BOT_NAME", "Orca"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
    "PINECONE_INDEX": os.getenv("PINECONE_INDEX", "plan"),
    "REDIS_HOST": os.getenv("REDIS_HOST", ""),
    "REDIS_PORT": os.getenv("REDIS_PORT", "6379"),
}

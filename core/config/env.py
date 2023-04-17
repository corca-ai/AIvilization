import os
from typing import TypedDict

from dotenv import load_dotenv

load_dotenv()


class DotEnv(TypedDict):
    OPENAI_API_KEY: str
    PINECONE_INDEX: str
    PINECONE_API_KEY: str
    LOG_LEVEL: str  # optional
    BOT_NAME: str  # optional


settings: DotEnv = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "PINECONE_INDEX": os.getenv("PINECONE_INDEX"),
    "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    "BOT_NAME": os.getenv("BOT_NAME", "Orca"),
}

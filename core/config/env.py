import os
from typing import TypedDict

from dotenv import load_dotenv

load_dotenv()


class DotEnv(TypedDict):
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX: str  # optional
    LOG_LEVEL: str  # optional
    BOT_NAME: str  # optional
    PORT_START: int  # optional
    PORT_RANGE: int  # optional
    HOST: str  # optional


settings: DotEnv = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
    "PINECONE_INDEX": os.getenv("PINECONE_INDEX", "plan"),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
    "BOT_NAME": os.getenv("BOT_NAME", "Orca"),
    "PORT_START": int(os.getenv("PORT_START", "50000")),
    "PORT_RANGE": int(os.getenv("PORT_RANGE", "10")),
    "HOST": os.getenv("HOST", "localhost"),
}

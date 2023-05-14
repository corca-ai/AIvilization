import os

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    PORT_START: int = os.getenv("PORT_START", "50000")
    PORT_RANGE: int = os.getenv("PORT_RANGE", "10")
    HOST: str = os.getenv("HOST", "127.0.0.1")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX: str = os.getenv("PINECONE_INDEX", "plan")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "")
    REDIS_PORT: str = os.getenv("REDIS_PORT", "6379")


settings = Settings()

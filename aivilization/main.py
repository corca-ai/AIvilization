import readline
import os

from core.civilization import Civilization
from core.civilization.person.tracer.log import LogTracer
from core.civilization.person.tracer.redis import RedisTracer
from core.config import settings
from core.logging import logger


def get_default_tracers():
    default_tracers = [LogTracer]
    if settings.REDIS_HOST:
        default_tracers.append(RedisTracer)
    return default_tracers


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def main():
    civilization = Civilization(default_tracers=get_default_tracers())

    while True:
        try:
            problem = input(">>> ")

            if problem == "clear":
                clear_terminal()
                continue

            civilization.solve(problem)

            readline.add_history(problem)
        except KeyboardInterrupt:
            os._exit(0)
        except EOFError:
            logger.info("Bye!")
            break


if __name__ == "__main__":
    main()

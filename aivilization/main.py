import readline

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


def main():
    civilization = Civilization(default_tracers=get_default_tracers())

    while True:
        try:
            problem = input(">>> ")
            civilization.solve(problem)

            readline.add_history(problem)
        except KeyboardInterrupt:
            print()
            continue
        except EOFError:
            logger.info("Bye!")
            break


if __name__ == "__main__":
    main()

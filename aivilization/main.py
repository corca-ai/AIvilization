import readline

from core.civilization import Civilization
from core.civilization.person.tracer.log import LogTracer
from core.civilization.person.tracer.redis import RedisTracer
from core.logging import logger


def main():
    civilization = Civilization(default_tracers=[LogTracer, RedisTracer])
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

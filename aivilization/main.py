import readline

from core.civilization import Civilization
from core.logging import logger


def main():
    civilization = Civilization()
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

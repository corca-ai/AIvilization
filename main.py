import readline

from core.civilization import Civilization
from core.logging import logger

if __name__ == "__main__":
    civilization = Civilization({})
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

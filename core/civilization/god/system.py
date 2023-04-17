class System:
    ERROR_MESSAGE = "error message\n"
    ANNOUNCEMENT_MESSAGE = "announcement\n"
    PROMPT_SEPARATOR = "===================="

    @staticmethod
    def error(message: str) -> str:
        return System.ERROR_MESSAGE + System.PROMPT_SEPARATOR + "\n" + message

    @staticmethod
    def announcement(message: str) -> str:
        return System.ANNOUNCEMENT_MESSAGE + System.PROMPT_SEPARATOR + "\n" + message

    @staticmethod
    def greeting(name: str) -> str:
        (
            f"{name}'s talk\n{System.PROMPT_SEPARATOR}\n"
            + "Hello, I am "
            + name
            + ".\nI was created from you."
        )

    @staticmethod
    def talk(listener: str, message: str) -> str:
        (
            f"{name}'s talk\n{System.PROMPT_SEPARATOR}\n"
            + "Hello, I am "
            + name
            + ".\nI was created from you."
        )

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

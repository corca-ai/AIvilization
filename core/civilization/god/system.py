class System:
    ERROR_MESSAGE = "error message\n"
    ANNOUNCEMENT_MESSAGE = "announcement\n"
    MESSAGE_SEPARATOR = "================"
    PROMPT_SEPARATOR = "-----"

    @staticmethod
    def error(message: str) -> str:
        return (
            System.MESSAGE_SEPARATOR
            + "\n"
            + System.ERROR_MESSAGE
            + System.PROMPT_SEPARATOR
            + "\n"
            + message
        )

    @staticmethod
    def announcement(message: str) -> str:
        return (
            System.MESSAGE_SEPARATOR
            + "\n"
            + System.ANNOUNCEMENT_MESSAGE
            + System.PROMPT_SEPARATOR
            + "\n"
            + message
        )

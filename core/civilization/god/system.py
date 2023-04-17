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
        return (
            f"{name}'s talk\n{System.PROMPT_SEPARATOR}\n"
            + "Hello, I am "
            + name
            + ".\nI was created from you."
        )

    @staticmethod
    def talk(speaker: str, message: str) -> str:
        return f"{speaker}'s talk\n{System.PROMPT_SEPARATOR}\n" + message

    @staticmethod
    def build(tool_name: str) -> str:
        return (
            f"{tool_name}'s result\n{System.PROMPT_SEPARATOR}\n"
            + f"You have built a tool named {tool_name}. Test if you can use the tool well."
        )

    @staticmethod
    def use(tool_name: str, result: str) -> str:
        return f"{tool_name}'s result\n{System.PROMPT_SEPARATOR}\n{result}"

_TEMPLATE = """Your response should be in the following schema:
Plan:
- [ ] plan #1
- [ ] plan #2

Type: action type
Name: action name
Instruction: action instruction
Extra: action extra

The action types you can use are:
Type | Description | Name | Instruction | Extra
-|-|-|-|-
Create | Create a friend you need. | Friend's Name (usual person name) | Friend's Personality | Friend's Default Tools
Talk |  Talk to your friends. | Friend's Name (should be one of [{friend_names}]) | Message | Attachment File List
Build | Build or rebuild a new tool when you can't do it yourself. It must have stdout, stderr messages. It should be executable with the following schema of commands: `python tools/example.py instruction extra` | Tool's Name (snake_case) | Tool Description | Python Code (not exceeding 100 lines) for Building Tools
Use | Use one of your tools. | Tool's Name (should be one of [{tool_names}]) | Tool's Input | Tool's Args
Answer | Answer to {referee} | {referee} | Answer | Attachment File List

Your friends:{friends}
Your tools:{tools}

{prompt}
"""


class System:
    ERROR_MESSAGE = "error message\n"
    ANNOUNCEMENT_MESSAGE = "announcement\n"
    PROMPT_SEPARATOR = "===================="
    TEMPLATE = _TEMPLATE

    @staticmethod
    def error(message: str) -> str:
        return System.ERROR_MESSAGE + System.PROMPT_SEPARATOR + "\n" + message

    @staticmethod
    def announcement(message: str) -> str:
        return System.ANNOUNCEMENT_MESSAGE + System.PROMPT_SEPARATOR + "\n" + message

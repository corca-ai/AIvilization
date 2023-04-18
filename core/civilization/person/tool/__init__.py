from .base import BaseTool, BuildParams, UseParams
from .default import CodeWriter, Terminal

__all__ = ["BaseTool", "BuildParams", "UseParams", "default_tools"]

default_tools = {
    "terminal": Terminal(
        "terminal",
        (
            "Executes commands in a terminal. "
            "If linux errno occurs, we have to solve the problem with the terminal. "
            "Input should be one valid command. "
            "Extra args should be empty. "
            "Output will be any output from running that command."
        ),
    ),
    "code_writer": CodeWriter(
        "code_writer",
        (
            "Write code for anything. "
            "Input should be a path to a file. "
            "Extra args should be a valid python code. "
            "Output will be the 'success' or 'error'. "
        ),
    ),
}

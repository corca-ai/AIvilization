from .base import BaseTool, BuildParams, UseParams
from .default import CodeWriter, Terminal

__all__ = ["BaseTool", "BuildParams", "UseParams", "default_tools"]

default_tools = {
    "terminal": Terminal(
        "terminal",
        (
            "Executes commands in a computer terminal. "
            "If linux errno occurs, we have to solve the problem with the computer terminal. "
            "Instruction should be one valid command. (ex. pip install numpy) "
            "Extra should be empty. "
            "Output will be any output from running that command."
        ),
    ),
    "code_writer": CodeWriter(
        "code_writer",
        (
            "Write code for anything. "
            "Instruction should be a path to a file. "
            "Extra should be a valid python code. "
            "Output will be the 'success' or 'error'. "
        ),
    ),
}

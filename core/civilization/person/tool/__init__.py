from typing import Dict

from .base import BaseTool, BuildParams, UseParams
from .coded import CodedTool
from .default import CodeWriter, Terminal

__all__ = ["BaseTool", "CodedTool", "BuildParams", "UseParams", "default_tools"]

default_tools: Dict[str, BaseTool] = {
    "terminal": Terminal(
        "terminal",
        (
            "Executes commands in a computer terminal. "
            "If linux errno occurs, we have to solve "
            "the problem with the computer terminal. "
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
            "Written code will be save to playground/<path to file>. "
            "Extra should be a valid code. "
            "Output will be the 'success' or 'error'. "
            "code_writer can only write one file per use."
        ),
    ),
}

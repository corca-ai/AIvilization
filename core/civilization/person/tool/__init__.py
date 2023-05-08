from typing import Dict

from core.civilization.person.tool.browser import Browser

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
            "Extra should be a valid code. "
            "Output will be the 'success' or 'error'. "
        ),
    ),
    "browser": Browser(
        "browser",
        (
            "Surfing the web on a browser. "
            "Instruction should be one valid command. (ex. open, scroll, move, click, write, close) "
            "Extra should be a valid input for that command. "
            "open: <url>, scroll: <position>, move: <css selector>, click: <css selector>, write: <{css selector: input}>, close: <empty> "
            'ex. open: https://www.google.com, scroll: 0,0, move: #hplogo, click: #hplogo, write: {"#hplogo": "hello"}, close: '
            "Output will be the page's contents. "
        ),
    ),
}

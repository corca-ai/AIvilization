import os
import subprocess

from core.logging import ANSI, Style, logger
from core.logging.ansi import Color
from core.terminal.tracer import StdoutTracer

from .base import BaseTool, BuildParams, UseParams

PLAYGROUND_DIR = "playground"


class Terminal(BaseTool):
    name = "terminal"
    description = (
        "Executes commands in a computer terminal. "
        "If linux errno occurs, we have to solve "
        "the problem with the computer terminal. "
        "Instruction should be one valid command. (ex. pip install numpy) "
        "Extra should be empty. "
        "Output will be any output from running that command."
    )
    color = Color.rgb(255, 0, 0)

    def build(self, params: BuildParams):
        pass

    def use(self, prompt: str, params: UseParams) -> str:
        process = subprocess.Popen(
            prompt,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=PLAYGROUND_DIR,
        )

        tracer = StdoutTracer(
            process,
            on_output=lambda p, o: logger.info(
                ANSI(p).to(Style.dim()) + " " + o.strip("\n")
            ),
        )
        _, output = tracer.wait_until_stop_or_exit()
        return output


class CodeWriter(BaseTool):
    name = "code_writer"
    description = (
        "Write code for anything. "
        "Instruction should be a path to a file. "
        "Written code will be save to playground/<path to file>. "
        "Extra should be a valid code. "
        "Output will be the 'success' or 'error'. "
        "code_writer can writes only one file per Use"
    )
    color = Color.rgb(0, 255, 0)

    def build(self, params: BuildParams):
        pass

    def use(self, prompt: str, params: UseParams) -> str:
        file_path = os.path.join(PLAYGROUND_DIR, prompt)
        code = BuildParams.from_str(params.input).code
        try:
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(file_path, "w") as f:
                f.write(code)
        except Exception as e:
            return str(e)
        return "Success!"

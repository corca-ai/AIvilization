import os
import subprocess

from core.logging import ANSI, Style, logger
from core.terminal.tracer import StdoutTracer

from .base import BaseTool, BuildParams, UseParams


class Terminal(BaseTool):
    def build(self, params: BuildParams):
        pass

    def use(self, prompt: str, params: UseParams) -> str:
        process = subprocess.Popen(
            prompt.split(" "),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
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
    def build(self, params: BuildParams):
        pass

    def use(self, prompt: str, params: UseParams) -> str:
        try:
            dir_path = os.path.dirname(prompt)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(prompt, "w") as f:
                f.write(params.input)
        except Exception as e:
            return str(e)
        return "Success!"

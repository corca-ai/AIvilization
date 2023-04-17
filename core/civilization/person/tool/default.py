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
            prompt,
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
        dir_path = os.path.dirname(self.filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        with open(self.filepath, "w") as f:
            f.write(params.input)
        return self.content

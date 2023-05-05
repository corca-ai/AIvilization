import os
import subprocess

from core.logging import ANSI, Style, logger
from core.terminal.tracer import StdoutTracer

from .base import BaseTool, BuildParams, UseParams


class CodedTool(BaseTool):
    def build(self, params: BuildParams):
        self.file_path = f"tools/{self.name}.py"
        os.makedirs("tools", exist_ok=True)
        with open(self.file_path, "w") as f:
            f.write(params.code)

    def use(self, prompt: str, params: UseParams) -> str:
        process = subprocess.Popen(
            f"python {self.file_path} {prompt} {params.input}",
            shell=True,
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

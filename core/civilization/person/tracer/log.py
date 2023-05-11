from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.civilization.god.system import System
from core.civilization.person.action import Action, ActionType, Plan
from core.civilization.person.brain.organize.base import Decision
from core.logging import ANSI, Color, Style, logger

if TYPE_CHECKING:
    from core.civilization.person import BasePerson, TalkParams

from .base import BasePersonTracer


class LogTracer(BasePersonTracer):
    thought: str
    logger: logging.Logger

    def __init__(self, person: BasePerson):
        super().__init__(person)
        self.thought = ""
        self.logger = logger

    def format_act(self, action: Action):
        target = self.get_target(action)
        return (
            str(self.person)
            + str(action.type)
            + ANSI(str(target)).to(Color.green(), Style.bold())
            + " | "
            + ANSI(action.instruction).to(Color.white())
            + (
                ANSI("\n... extra: " + action.extra).to(Style.dim())
                if action.extra
                else ""
            )
        )

    def on_request(self, sender: BasePerson, prompt: str, params: TalkParams):
        pass

    def on_thought_start(self):
        self.thought = ""

    def on_thought(self, thought: str):
        self.thought += thought

        if self.thought.endswith("\n"):
            logger.debug(
                ANSI("[thought] ".rjust(12)).to(Color.rgb(0x6D, 0xA9, 0xE4))
                + self.thought.rstrip()
            )
            self.thought = ""

    def on_thought_end(self):
        self.thought = ""

    def on_thought_error(self, error: Exception):
        logger.exception(error)

    def on_plans(self, plans: list[Plan]):
        for plan in plans:
            logger.debug(
                ANSI(f"[plan {plan.plan_number}] ".rjust(12)).to(
                    Color.rgb(0xF6, 0xBA, 0x6F)
                )
                + plan.action_type.value
                + ": "
                + plan.objective
                + "\n"
                + ANSI("\tprecondition: " + plan.precondition + "\n").to(Color.rgb(0xC0, 0xC0, 0xC0))
                + ANSI("\teffect: " + plan.effect + "\n").to(Color.rgb(0xC0, 0xC0, 0xC0))
                + ANSI("\tconstraint: " + plan.constraint).to(Color.rgb(0xC0, 0xC0, 0xC0))
            )

    def on_optimize(self, opinion: str, ok: bool):
        logger.debug(
            ANSI("[optimize] ".rjust(12)).to(Color.rgb(0xAD, 0xE4, 0xDB))
            + str(Decision.ACCEPT if ok else Decision.REJECT)
            + ": "
            + opinion
        )

    def on_act(self, action: Action):
        if action.type in [ActionType.Talk, ActionType.Use]:
            logger.info(self.format_act(action))

    def on_act_error(self, action: Action, error: Exception):
        logger.exception(error)

    def on_act_result(self, action: Action, result: str):
        if action.type in [ActionType.Invite, ActionType.Build]:
            logger.info(self.format_act(action))

        for line in result.split("\n"):
            logger.debug(ANSI("[result] ".rjust(12)).to(Color.cyan()) + line)

    def on_review(self, opinion: str, ok: bool):
        logger.debug(
            ANSI("[review] ".rjust(12)).to(Color.rgb(0xF0, 0xCE, 0xFF))
            + str(Decision.ACCEPT if ok else Decision.REJECT)
            + ": "
            + opinion
        )

    def on_response(self, sender: BasePerson, response: str):
        logger.info(
            str(self.person)
            + str(ActionType.Respond)
            + str(sender)
            + " | "
            + ANSI(response.split(System.PROMPT_SEPARATOR)[1].strip()).to(Color.white())
        )

    def on_response_error(self, sender: BasePerson, error: Exception):
        logger.exception(error)

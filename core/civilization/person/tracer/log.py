from __future__ import annotations

from typing import TYPE_CHECKING

from core.civilization.god.system import System
from core.civilization.person.action import Action, ActionType
from core.logging import ANSI, Color, Style, logger

if TYPE_CHECKING:
    from core.civilization.person import BasePerson, TalkParams

from .base import BasePersonTracer


class LogTracer(BasePersonTracer):
    def format_act(self, action: Action):
        target = None
        if action.type in [ActionType.Invite, ActionType.Talk]:
            target = self.person.friends[action.name]
        elif action.type in [ActionType.Build, ActionType.Use]:
            target = self.person.tools[action.name]
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

    def on_idea(self, idea: str):
        logger.debug(ANSI("[idea] ").to(Color.rgb(0xF6, 0xBA, 0x6F)) + idea)

    def on_idea_error(self, error: Exception):
        logger.exception(error)

    def on_thought(self, thought: str):
        logger.debug(ANSI("[thought] ").to(Color.rgb(0x6D, 0xA9, 0xE4)) + thought)

    def on_thought_error(self, error: Exception):
        logger.exception(error)

    def on_actions(self, actions: list[Action]):
        logger.debug(
            ANSI("[actions] ").to(Color.rgb(0xAD, 0xE4, 0xDB))
            + ", ".join([str(action.type) for action in actions])
        )

    def on_actions_error(self, error: Exception):
        logger.exception(error)

    def on_act(self, action: Action):
        if action.type in [ActionType.Talk, ActionType.Use]:
            logger.info(self.format_act(action))

    def on_act_error(self, action: Action, error: Exception):
        logger.exception(error)

    def on_act_result(self, action: Action, result: str):
        if action.type in [ActionType.Invite, ActionType.Build]:
            logger.info(self.format_act(action))
        logger.debug(ANSI(action.name + " result: ").to(Color.cyan()) + result)

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

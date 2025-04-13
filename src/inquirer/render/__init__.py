from __future__ import annotations
from typing import Any
from inquirer.render.console import ConsoleRender
from inquirer.questions import Question


class Render:
    def __init__(self, impl: type[ConsoleRender] = ConsoleRender):
        self._impl = impl

    def render(self, question: Question, answers: dict[str, Any] | None = None) -> Any:
        # TODO: figure out the inheritance chain here and uncomplicate this
        return self._impl.render(question, answers)

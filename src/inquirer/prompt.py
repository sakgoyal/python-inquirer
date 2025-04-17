from __future__ import annotations
from typing import Any

from collections.abc import Iterable

from inquirer.themes import Theme
from inquirer.render.console import ConsoleRender
from inquirer.questions import Question


def prompt(
    questions: Iterable[Question],
    answers: dict[str, Any] | None = None,
    theme: Theme = Theme(),
    raise_keyboard_interrupt: bool = False,
):
    answers = answers or {}

    try:
        for question in questions:
            answers[question.name] = ConsoleRender(theme=theme).render(question, answers)
        return answers
    except KeyboardInterrupt:
        if raise_keyboard_interrupt:
            raise
        return print("\nCancelled by user\n")

from __future__ import annotations

from typing import Any

from collections.abc import Callable

from inquirer import questions
from inquirer.render.console import ConsoleRender


def text(
    message: str,
    autocomplete: Callable[[str, int], str | None] | None = None,
    **kwargs: Any,
) -> str:
    question = questions.Text(name="", message=message, autocomplete=autocomplete, **kwargs)
    return ConsoleRender().render(question)


def editor(message: str, **kwargs: Any) -> str:
    if kwargs.get("render") is not None:
        raise ValueError(
            "The 'render' argument is not supported for the editor question.",
            kwargs["render"],
        )
    question = questions.Editor(name="", message=message, **kwargs)
    return ConsoleRender().render(question)


def password(message: str, **kwargs: Any) -> str:
    question = questions.Password(name="", message=message, **kwargs)
    return ConsoleRender().render(question)


def confirm(message: str, **kwargs: Any) -> bool:
    question = questions.Confirm(name="", message=message, **kwargs)
    return ConsoleRender().render(question)


def list_input(message: str, **kwargs: Any) -> str | list[str]:
    question = questions.List(name="", message=message, **kwargs)
    return ConsoleRender().render(question)


def checkbox(message: str, **kwargs: Any) -> list[str]:
    question = questions.Checkbox(name="", message=message, **kwargs)
    return ConsoleRender().render(question)


def path(message: str, **kwargs: Any) -> str:
    question = questions.Path(name="", message=message, **kwargs)
    return ConsoleRender().render(question)

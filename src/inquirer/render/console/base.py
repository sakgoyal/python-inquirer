from __future__ import annotations

from abc import abstractmethod
from typing import Any, LiteralString

from collections.abc import Generator

from blessed import Terminal

from inquirer.errors import ValidationError
from inquirer.questions import Question
from inquirer.themes import Theme

MAX_OPTIONS_DISPLAYED_AT_ONCE = 15
half_options = int(MAX_OPTIONS_DISPLAYED_AT_ONCE / 2)


class BaseConsoleRender:
    title_inline: bool = False

    def __init__(
        self,
        question: Question,
        theme: Theme | None = None,
        terminal: Terminal | None = None,
        show_default: bool = False,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.question = question
        self.terminal = terminal or Terminal()
        self.answers = {}
        self.theme = theme
        self.show_default = show_default

    def other_input(self) -> str | None:
        from inquirer.shortcuts import text  # Avoiding circular import

        other = text(self.question.message, autocomplete=getattr(self.question, "autocomplete", None))
        return other

    def get_header(self) -> str:
        return self.question.message

    def get_hint(self) -> str:
        return ""

    def get_current_value(self) -> str:
        return ""

    def get_options(self) -> Generator[tuple[str, str | LiteralString, str], Any, None]:
        return []

    @abstractmethod
    def process_input(self, pressed: str) -> None: ...

    def handle_validation_error(self, error: ValidationError) -> str:
        if error.reason:
            return error.reason

        ret = f'"{error.value}" is not a valid {self.question.name}.'
        try:
            ret.format()
            return ret
        except (ValueError, KeyError):
            return f"Entered value is not a valid {self.question.name}."

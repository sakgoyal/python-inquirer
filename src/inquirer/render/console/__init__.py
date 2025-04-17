from __future__ import annotations

import sys
import textwrap
from typing import Any, Literal

from blessed import Terminal

from inquirer import errors
from inquirer.events import KeyEventGenerator
from inquirer.questions import Question
from inquirer.themes import Theme

from ._checkbox import Checkbox
from ._confirm import Confirm
from ._editor import Editor
from ._list import List
from ._password import Password
from ._path import Path
from ._text import Text
from .base import BaseConsoleRender


class ConsoleRender:
    def __init__(
        self,
        event_generator: KeyEventGenerator | None = None,
        theme: Theme | None = None,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self._event_gen = event_generator or KeyEventGenerator()
        self.terminal = Terminal()
        self._previous_error: str | None = None
        self._position = 0
        self._theme = theme or Theme()

    def render(self, question: Question, answers: dict[str, Any] | None = None) -> Any:
        question.answers = answers or {}

        if question.ignore:
            return question.default

        clazz = self.render_factory(question.kind)
        render = clazz(question, terminal=self.terminal, theme=self._theme, show_default=question.show_default)

        self.clear_eos()

        try:
            return self._event_loop(render)
        finally:
            print("")

    def _event_loop(self, render: BaseConsoleRender) -> list[int] | list[str] | str | bool:
        try:
            while True:
                self._relocate()
                self._print_status_bar(render)

                self._print_header(render)
                self._print_hint(render)
                self._print_options(render)

                self._process_input(render)
                self._force_initial_column()
        except errors.EndOfInput as e:
            self._go_to_end(render)
            return e.selection

    def _print_status_bar(self, _render: BaseConsoleRender) -> None:
        if self._previous_error is None:
            self.clear_bottombar()
            return

        self.render_error(self._previous_error)
        self._previous_error = None

    def _print_options(self, render: BaseConsoleRender) -> None:
        for message, symbol, color in render.get_options():
            self.print_line(" {color}{s} {m}{t.normal}", m=message, color=color, s=symbol)

    def _print_header(self, render: BaseConsoleRender) -> None:
        base = render.get_header()
        header = textwrap.shorten(base, width=self.width - 9, placeholder="...")

        default_value = f" ({self._theme.Question['default_color']}{render.question.default}{self.terminal.normal})"
        show_default = render.question.default and render.show_default
        header += default_value if show_default else ""
        msg_template = (
            "{t.move_up}{t.clear_eol}{tq[brackets_color]}[{tq[mark_color]}?{tq[brackets_color]}]{t.normal} {msg}"
        )

        # ensure any user input with { or } will not cause a formatting error
        escaped_current_value = str(render.get_current_value()).replace("{", "{{").replace("}", "}}")
        self.print_str(
            f"\n{msg_template}: {escaped_current_value}",
            msg=header,
            lf=not render.title_inline,
            tq=self._theme.Question,
        )

    def _print_hint(self, render: BaseConsoleRender) -> None:
        msg_template = "{t.move_up}{t.clear_eol}{color}{msg}"
        hint = ""
        if render.question.hints is not None:
            hint = render.get_hint()
        color = self._theme.Question["mark_color"]
        if hint:
            self.print_str(
                f"\n{msg_template}", msg=hint, color=color, lf=not render.title_inline, tq=self._theme.Question
            )

    def _process_input(self, render: BaseConsoleRender) -> None:
        try:
            ev = self._event_gen.next()
            render.process_input(ev.value)
        except errors.ValidationError as e:
            self._previous_error = e.value
        except errors.EndOfInput as e:
            try:
                render.question.validate(e.selection)
                raise
            except errors.ValidationError as ve:
                self._previous_error = render.handle_validation_error(ve)

    def _relocate(self) -> None:
        print(self._position * self.terminal.move_up, end="")
        self._force_initial_column()
        self._position = 0

    def _go_to_end(self, render: BaseConsoleRender) -> None:
        positions = len(list(render.get_options())) - self._position
        if positions > 0:
            print(self._position * self.terminal.move_down, end="")
        self._position = 0

    def _force_initial_column(self) -> None:
        self.print_str("\r")

    def render_error(self, message: str | None) -> None:
        if message:
            symbol = ">> "
            size = len(symbol) + 1
            message = textwrap.shorten(message.rstrip(), width=self.width - size, placeholder="...")
            self.render_in_bottombar(
                "{t.red}{s}{t.normal}{t.bold}{msg}{t.normal}".format(msg=message, s=symbol, t=self.terminal)
            )

    def render_in_bottombar(self, message: str) -> None:
        with self.terminal.location(0, self.height - 2):
            self.clear_eos()
            self.print_str(message)

    def clear_bottombar(self) -> None:
        with self.terminal.location(0, self.height - 2):
            self.clear_eos()

    def render_factory(
        self, question_type: Literal["text", "editor", "password", "confirm", "list", "checkbox", "path"]
    ) -> type[BaseConsoleRender]:
        match question_type:
            case "text":
                return Text
            case "editor":
                return Editor
            case "password":
                return Password
            case "confirm":
                return Confirm
            case "list":
                return List
            case "checkbox":
                return Checkbox
            case "path":
                return Path
            case _:
                raise errors.UnknownQuestionTypeError()

    def print_line(self, base: str, lf: bool = True, **kwargs: Any) -> None:
        self.print_str(base + self.terminal.clear_eol(), lf=lf, **kwargs)

    def print_str(self, base: str, lf: bool = False, **kwargs: Any) -> None:
        if lf:
            self._position += 1

        # if "tq" in kwargs: set qt.brackets_color to empty string if not set
        if "tq" in kwargs and "brackets_color" in kwargs["tq"] and kwargs["tq"]["brackets_color"] is None:
            kwargs["tq"].brackets_color = self.terminal.normal
        print(base.format(t=self.terminal, **kwargs), end="\n" if lf else "")
        sys.stdout.flush()

    def clear_eos(self) -> None:
        print(self.terminal.clear_eos(), end="")

    @property
    def width(self) -> int:
        return self.terminal.width or 80

    @property
    def height(self) -> int:
        return self.terminal.width or 24

from typing import Any

import editor
from readchar import key

from inquirer import errors
from inquirer.questions import Editor as EditorQuestion

from ...themes import ThemeError
from .base import BaseConsoleRender


class Editor(BaseConsoleRender):
    title_inline = True
    question: EditorQuestion

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.current = ""

    def get_current_value(self):
        if not self.theme:
            raise ThemeError("No theme provided.")
        return f"{self.theme.Editor['opening_prompt_color']}Press <enter> to launch your editor{self.terminal.normal}"

    def handle_validation_error(self, error: errors.ValidationError) -> str:
        if error.reason:
            return error.reason

        return f"Entered value is not a valid {self.question.name}."

    def process_input(self, pressed: str) -> None:
        if pressed == key.CTRL_C:
            raise KeyboardInterrupt()

        if pressed in (key.CR, key.LF, key.ENTER):
            # TODO: fixing this breaks a test case
            data = editor(text=self.question.default or "")
            raise errors.EndOfInput(data)

        raise errors.ValidationError("You have pressed unknown key! Press <enter> to open editor or CTRL+C to exit.")

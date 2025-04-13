from readchar import key

from inquirer import errors
from inquirer.render.console.base import BaseConsoleRender


class Confirm(BaseConsoleRender):
    title_inline: bool = True

    def get_header(self):
        confirm = "(Y/n)" if self.question.default else "(y/N)"
        return f"{self.question.message} {confirm}"

    def process_input(self, pressed: str) -> None:
        match pressed:
            case key.CTRL_C:
                raise KeyboardInterrupt()
            case key.ENTER:
                raise errors.EndOfInput(self.question.default)
            case "y" | "Y":
                print(pressed)
                raise errors.EndOfInput(True)
            case "n" | "N":
                print(pressed)
                raise errors.EndOfInput(False)
            case _:
                raise errors.ValidationError("Please enter either 'y' or 'n'.", pressed)

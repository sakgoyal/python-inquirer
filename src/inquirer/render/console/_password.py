from inquirer import errors
from inquirer.questions import Password as PasswordQuestion
from inquirer.render.console._text import Text


class Password(Text):
    question: PasswordQuestion  # type: ignore

    def get_current_value(self) -> str:
        return self.question.echo * len(self.current) + (self.terminal.move_left * self.cursor_offset)

    def handle_validation_error(self, error: errors.ValidationError):
        if error.reason:
            return error.reason

        return f"Entered value is not a valid {self.question.name}."

"""Module that implements the questions types."""

from __future__ import annotations

import json
import pathlib
from typing import Any, Literal, cast

from collections.abc import Callable, Iterable, Sequence

from inquirer import errors
from inquirer.render.console._other import GLOBAL_OTHER_CHOICE, OtherChoice

type ValidatorType = bool | Callable[[dict[str, Any], Any], bool]
type MessageType = str | Callable[[dict[str, Any]], str]
type ChoiceType[T: Any] = object | int | str | tuple[str, T] | OtherChoice
type IgnoreType = bool | Callable[[Any], bool] | Callable[[Any], None]


class TaggedValue[T]:
    def __init__(self, tag: str, value: T):
        self.tag = tag
        self.value = value
        self.tuple = (tag, value)

    def __str__(self) -> str:
        return self.tag

    def __repr__(self) -> str:
        return repr(self.value)

    def __eq__(self, other: Any | tuple[str, T] | TaggedValue[T]) -> bool:
        if isinstance(other, TaggedValue):
            return (
                other.value == self.value  # type: ignore
            )  # error here because type of other is not known. TaggedValue[T] is not runtime
        if isinstance(other, tuple):
            return other == self.tuple
        return other == self.value

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.tuple)


type QuestionKind = Literal["text", "editor", "password", "confirm", "list", "checkbox", "path"]


class Question:
    kind: QuestionKind = "base question"  # type: ignore

    def __init__(
        self,
        name: str,
        message: MessageType = "",
        choices: Iterable[ChoiceType[Any]] | None = None,
        default: object | bool | str | list[str] | Callable[[Any], bool | str] | None = None,
        ignore: IgnoreType = False,
        validate: ValidatorType = True,
        show_default: bool = False,
        hints: dict[str, str] | dict[tuple[str, str], str] | None = None,
        other: bool = False,
    ):
        self.name = name
        self._message = message
        self._choices: list[ChoiceType[Any]] = list(choices or [])
        self._default = default
        self._ignore = ignore
        self._validate = validate
        self.answers: dict[str, str] = {}
        self.show_default = show_default
        self.hints = hints
        self._other = other

        if self._other:
            self._choices.append(GLOBAL_OTHER_CHOICE)

    def add_choice(self, choice: str | tuple[str, str]) -> int:
        try:
            index = self._choices.index(choice)
            return index
        except ValueError:
            if self._other:
                self._choices.insert(-1, choice)
                return len(self._choices) - 2

            self._choices.append(choice)
            return len(self._choices) - 1

    @property
    def ignore(self) -> bool:
        return bool(self._solve(self._ignore))

    @property
    def message(self) -> str:
        temp = self._solve(self._message)
        if not isinstance(temp, str):
            raise TypeError(f"Message must be a string, not {type(temp)}")
        return temp

    @property
    def default(self):
        return self.answers.get(self.name) or self._solve(self._default)

    @property
    def choices_generator(self):
        for choice in self._solve(self._choices):
            yield (TaggedValue(*choice) if isinstance(choice, tuple) and len(choice) == 2 else choice)

    @property
    def choices(self) -> list[ChoiceType[Any]]:
        return list(self.choices_generator)

    def validate(self, current: ChoiceType[Any] | None):
        try:
            if self._solve(self._validate, current):
                return
        except errors.ValidationError as e:
            raise e
        raise errors.ValidationError(current)

    def _solve(
        self,
        prop: Callable[[dict[str, str]], Any] | str | Any,
        *args: Sequence[ChoiceType[Any]] | ChoiceType[Any] | None,
        **kwargs: Any,
    ):
        if callable(prop):
            return prop(self.answers, *args, **kwargs)
        if isinstance(prop, str):
            return prop.format(**self.answers)
        return prop


class Text(Question):
    kind = "text"

    def __init__(
        self,
        name: str,
        message: MessageType = "",
        default: bool | str | Callable[[Any], bool | str] | None = None,
        autocomplete: Callable[[str, int], str | None] | None = None,
        ignore: Callable[[str | dict[str, str]], bool] | bool = False,
        validate: Callable[[Any, Any], bool] | bool = True,
        **kwargs: Any,
    ):
        super().__init__(
            name,
            message=message,
            default=str(default) if default and not callable(default) else default,
            validate=validate,
            ignore=ignore,
            **kwargs,
        )

        self.autocomplete = autocomplete


class Password(Text):
    kind = "password"

    def __init__(self, name: str, echo: str = "*", **kwargs: Any):
        super().__init__(name, **kwargs)
        self.echo = echo


class Editor(Text):
    kind = "editor"
    validate: Callable[[Any, str], bool]  # type: ignore


class Confirm(Question):
    kind = "confirm"

    def __init__(self, name: str, default: bool | str = False, **kwargs: Any):
        super().__init__(name, default=default, **kwargs)


class List(Question):
    kind = "list"

    def __init__(
        self,
        name: str,
        message: MessageType = "",
        choices: Iterable[ChoiceType[Any]] | None = None,
        hints: dict[str, str] | None = None,
        default: str | list[str] | None = None,
        ignore: IgnoreType = False,
        validate: ValidatorType = True,
        carousel: bool = False,
        other: bool = False,
        autocomplete: Callable[[str, int], str | None] | None = None,
    ):
        super().__init__(name, message, choices, default, ignore, validate, hints=hints, other=other)
        self.carousel = carousel
        self.autocomplete = autocomplete


class Checkbox(Question):
    kind = "checkbox"

    def __init__(
        self,
        name: str,
        message: MessageType = "",
        choices: Iterable[ChoiceType[Any]] | None = None,
        hints: dict[tuple[str, str], str] | None = None,
        locked: list[str] | None = None,
        default: list[str] | None = None,
        ignore: IgnoreType = False,
        validate: ValidatorType = True,
        carousel: bool = False,
        other: bool = False,
        autocomplete: Callable[[str, int], str | None] | None = None,
    ):
        super().__init__(name, message, choices, default, ignore, validate, hints=hints, other=other)
        self.locked = locked
        self.carousel = carousel
        self.autocomplete = autocomplete


class Path(Text):
    ANY = "any"
    FILE = "file"
    DIRECTORY = "directory"

    type PathType = Literal["any", "file", "directory"]

    kind = "path"

    def __init__(
        self,
        name: str,
        default: str | None = None,
        path_type: PathType = "any",
        exists: bool | None = None,
        **kwargs: Any,
    ):
        super().__init__(name, default=default, **kwargs)

        if path_type in (Path.ANY, Path.FILE, Path.DIRECTORY):
            self._path_type = path_type
        else:
            raise ValueError("'path_type' must be one of ['any' | 'file' | 'directory']")

        self._exists = exists

        if default is not None:
            try:
                self.validate(default)
            except errors.ValidationError as ex:
                raise ValueError("Default value '{default}' is not valid based on your Path's criteria") from ex

    def validate(self, current: str | None) -> None:  # type: ignore
        super().validate(current)

        if current is None:
            raise errors.ValidationError(current)

        path = pathlib.Path(current)

        # this block validates the path in correspondence with the OS
        # it will error if the path contains invalid characters
        try:
            path.lstat()
        except FileNotFoundError:
            pass
        except (ValueError, OSError) as e:
            raise errors.ValidationError(e)

        if (self._exists is True and not path.exists()) or (self._exists is False and path.exists()):
            raise errors.ValidationError(current)

        # os.path.isdir and isfile check also existence of the path,
        # which might not be desirable
        if self._path_type == Path.FILE:
            if current.endswith(("\\", "/")):
                raise errors.ValidationError(current)
            if path.exists() and not path.is_file():
                raise errors.ValidationError(current)

        if self._path_type == Path.DIRECTORY:
            if current == "":
                raise errors.ValidationError(current)
            if path.exists() and not path.is_dir():
                raise errors.ValidationError(current)


def question_factory(kind: QuestionKind, *args: Any, **kwargs: Any) -> Question:
    # if 'name' not in args and 'name' not in kwargs:
    #     raise errors.UnknownQuestionTypeError("name", "Name is required for all questions.")
    for cl in (Text, Editor, Password, Confirm, List, Checkbox, Path):
        if cl.kind == kind:
            return cl(*args, **kwargs)
    raise errors.UnknownQuestionTypeError()


def load_from_dict(question_dict: dict[str, Any]) -> Question:
    """Load one question from a dict.

    It requires the keys 'name' and 'kind'.

    Returns:
        The Question object with associated data.
    """
    return question_factory(**question_dict)


def load_from_list(question_list: list[dict[str, Any]]) -> list[Question]:
    """Load a list of questions from a list of dicts.

    It requires the keys 'name' and 'kind' for each dict.

    Returns:
        A list of Question objects with associated data.
    """
    return [load_from_dict(q) for q in question_list]


def load_from_json(question_json: str | bytes | bytearray) -> list[Question] | Question:
    """Load Questions from a JSON string.

    Returns:
        A list of Question objects with associated data if the JSON
        contains a list or a Question if the JSON contains a dict.
    """
    data = json.loads(question_json)
    if isinstance(data, list):
        return load_from_list(cast(list[dict[str, Any]], data))
    if isinstance(data, dict):
        return load_from_dict(cast(dict[str, Any], data))
    raise TypeError(f"Json contained a {type(data)} variable when a dict or list was expected")

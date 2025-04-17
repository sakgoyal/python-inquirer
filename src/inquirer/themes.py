from __future__ import annotations
import json

from typing import TypedDict
from blessed import Terminal

term = Terminal()


def load_theme_from_json(json_theme: str | bytes | bytearray) -> Theme:
    """Load a theme from a json.

    Expected format:
        >>> {
        ...     "Question": {
        ...         "mark_color": "yellow",
        ...         "brackets_color": "normal",
        ...         ...
        ...     },
        ...     "List": {
        ...         "selection_color": "bold_blue",
        ...         "selection_cursor": "->"
        ...     }
        ... }

    Color values should be string representing valid blessings.Terminal colors.
    """
    return load_theme_from_dict(json.loads(json_theme))


def load_theme_from_dict(dict_theme: Loader) -> Theme:
    """Load a theme from a dict.

    Expected format:
        >>> {
        ...     "Question": {
        ...         "mark_color": "yellow",
        ...         "brackets_color": "normal",
        ...         ...
        ...     },
        ...     "List": {
        ...         "selection_color": "bold_blue",
        ...         "selection_cursor": "->"
        ...     }
        ... }

    Color values should be string representing valid blessings.Terminal colors and fallback to the given color
    """
    t = Theme()
    # we need to transform them to terminal color values first
    for question_type, settings in dict_theme.items():
        for field, value in settings.items():  # type: ignore
            dict_theme[question_type][field] = term.__getattr__(value) or value  # type: ignore
    t.Question.update(dict_theme.get("Question", {}))
    t.Editor.update(dict_theme.get("Editor", {}))
    t.Checkbox.update(dict_theme.get("Checkbox", {}))
    t.List.update(dict_theme.get("List", {}))
    return t


# Current problem is that TypedDict does not support Partial types
# load_theme_from_dict({
#     "Question": {
#         "mark_color": "yellow",
#     },
# })
# so its not possible to update only some fields of the dict
# without having to specify all of them unless we use a workaround like this:
# class QuestionThemePartial(TypedDict, total=False)
# but this will make it impossible to use the dict as a normal TypedDict
# because all fields will be optional forever


class Loader(TypedDict, total=False):
    Question: QuestionTheme
    Editor: EditorTheme
    Checkbox: CheckboxTheme
    List: ListTheme


class QuestionTheme(TypedDict):
    mark_color: str
    brackets_color: str
    default_color: str


class EditorTheme(TypedDict):
    opening_prompt_color: str


class CheckboxTheme(TypedDict):
    selection_color: str
    selection_icon: str
    selected_color: str
    unselected_color: str
    selected_icon: str
    unselected_icon: str
    locked_option_color: str


class ListTheme(TypedDict):
    selection_color: str
    selection_cursor: str
    unselected_color: str


class Theme:
    def __init__(self) -> None:
        self.Question: QuestionTheme = {
            "brackets_color": term.normal,
            "mark_color": term.yellow,
            "default_color": term.normal,
        }
        self.Editor: EditorTheme = {
            "opening_prompt_color": term.normal,
        }
        self.Checkbox: CheckboxTheme = {
            "selection_color": term.cyan,
            "selection_icon": ">",
            "selected_icon": "[X]",
            "selected_color": term.yellow + term.bold,
            "unselected_color": term.normal,
            "unselected_icon": "[ ]",
            "locked_option_color": term.gray50,
        }
        self.List: ListTheme = {
            "selection_color": term.cyan,
            "selection_cursor": ">",
            "unselected_color": term.normal,
        }
        self.Question["mark_color"] = term.yellow
        self.Question["brackets_color"] = term.normal
        self.Question["default_color"] = term.normal
        self.Editor["opening_prompt_color"] = term.bright_black
        self.Checkbox["selection_color"] = term.cyan
        self.Checkbox["selection_icon"] = ">"
        self.Checkbox["selected_icon"] = "[X]"
        self.Checkbox["selected_color"] = term.yellow + term.bold
        self.Checkbox["unselected_color"] = term.normal
        self.Checkbox["unselected_icon"] = "[ ]"
        self.Checkbox["locked_option_color"] = term.gray50
        self.List["selection_color"] = term.cyan
        self.List["selection_cursor"] = ">"
        self.List["unselected_color"] = term.normal


class GreenPassion(Theme):
    def __init__(self):
        super().__init__()
        self.Question["brackets_color"] = term.bright_green
        self.Checkbox["selection_color"] = term.bold_black_on_bright_green
        self.Checkbox["selection_icon"] = "❯"
        self.Checkbox["selected_icon"] = "◉"
        self.Checkbox["selected_color"] = term.green
        self.Checkbox["unselected_icon"] = "◯"
        self.List["selection_color"] = term.bold_black_on_bright_green
        self.List["selection_cursor"] = "❯"


class BlueComposure(Theme):
    def __init__(self):
        super().__init__()
        self.Question["brackets_color"] = term.dodgerblue
        self.Question["default_color"] = term.deepskyblue2
        self.Checkbox["selection_icon"] = "➤"
        self.Checkbox["selection_color"] = term.bold_black_on_darkslategray3
        self.Checkbox["selected_icon"] = "☒"
        self.Checkbox["selected_color"] = term.cyan3
        self.Checkbox["unselected_icon"] = "☐"
        self.List["selection_color"] = term.bold_black_on_darkslategray3
        self.List["selection_cursor"] = "➤"


class ThemeError(AttributeError):
    pass

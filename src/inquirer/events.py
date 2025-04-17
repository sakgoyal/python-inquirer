from typing import Any

from collections.abc import Callable, Generator

import readchar


class KeyPressed:
    def __init__(self, value: str):
        self.value = value


class KeyEventGenerator(Generator[KeyPressed]):
    def __init__(self, key_generator: Callable[[], str] | None = None):
        self._key_gen = key_generator or readchar.readkey

    def next(self):
        return KeyPressed(self._key_gen())

    def send(self, value: None):
        return KeyPressed(self._key_gen())

    def throw(self, typ, val=None, tb: Any = None):  # type: ignore
        raise StopIteration

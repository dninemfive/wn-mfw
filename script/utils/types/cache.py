from typing import Generator, Self
from utils.io import load, write
from utils.types.message import Message, try_nest

class Cache(object):
    def __init__(self: Self, file_path: str):
        self.file_path = file_path
        self._data: dict[str, str] = None
        self._accessed: dict[str, bool] = None

    def __getitem__(self: Self, key: str) -> str:
        self._accessed[key] = True
        return self._data[key]
    
    def __setitem__(self: Self, key: str, val: str):
        self._accessed[key] = True
        self._data[key] = val

    def __contains__(self: Self, key: str) -> bool:
        self._accessed[key] = True
        return key in self._data

    def load(self: Self, parent_msg: Message | None = None) -> None:
        with try_nest(parent_msg, self.file_path) as _:
            self._data = load(self.file_path, {})
            self._accessed = {x:False for x in self._data.keys()}

    def save(self: Self, parent_msg: Message | None = None) -> None:
        with try_nest(parent_msg, self.file_path) as _:
            write(self._data, self.file_path)

    @property
    def keys(self: Self): # -> Generator[str]
        yield from self._data.keys()

    @property
    def values(self: Self): # -> Generator[str]
        yield from self._data.values()

    @property
    def items(self: Self): # -> Generator[tuple[str, str]]
        yield from self._data.items()

    @property
    def accessed_items(self: Self): # -> Generator[tuple[str, str]]
        for k, v in self.items:
            if self._accessed[k]:
                yield (k, v)

    @property
    def any(self: Self) -> bool:
        return len(self._data.keys()) > 0
from __future__ import annotations

from abc import ABC
from typing import Any, Callable, Iterable, Self, Type

from wrappers.list import ListWrapper
import utils.ndf.edit as edit
import utils.ndf.ensure as ensure
import utils.ndf.unit_module as modules
# from context.mod_creation import ModCreationContext
from ndf_parse.model import Object


class TurretWrapper(ABC):
    # ctx: ModCreationContext
    def __init__(self: Self, ctx, object: Object):
        self.ctx = ctx
        self.object = object
        
    @property
    def Tag(self: Self) -> str:
        return ensure.unquoted(self.object.by_member('Tag').value)
    
    @Tag.setter
    def Tag(self: Self, value: str) -> None:
        edit.members(self.object, Tag=ensure.quoted(value))

    @property
    def YulBoneOrdinal(self: Self) -> int:        
        return int(self.object.by_member('YulBoneOrdinal').value)

    @YulBoneOrdinal.setter
    def YulBoneOrdinal(self: Self, value: int) -> None:
        edit.members(self.object, YulBoneOrdinal=value)
from numbers import Number
from typing import Self

import utils.ndf.edit as edit
import utils.ndf.ensure as ensure
from constants.primitive_types import Factory
from ndf_parse.model import List, Object
from wrappers.map import MapWrapper

from ._abc import UnitModuleWrapper
from ._decorator import unit_module

COMMAND_POINTS_KEY = '$/GFX/Resources/Resource_CommandPoints'

@unit_module('TProductionModuleDescriptor')
class ProductionModuleWrapper(UnitModuleWrapper):
    @property
    def Factory(self: Self) -> str:
        return self.object.by_member('Factory').value
    
    @Factory.setter
    def Factory(self: Self, value: str) -> None:
        edit.members(Factory=Factory.ensure_valid(value))

    @property
    def ProductionTime(self: Self) -> int:
        return int(self.object.by_member('ProductionTime').value)
    
    @ProductionTime.setter
    def ProductionTime(self: Self, value: int) -> None:
        edit.members(ProductionTime=value)

    @property
    def ProductionRessourcesNeeded(self: Self) -> MapWrapper:
        if self._production_ressources_needed is None:
            self._production_ressources_needed = MapWrapper(self.object.by_member('ProductionRessourcesNeeded').value)
        return self._production_ressources_needed
    
    @property
    def command_point_cost(self: Self) -> int:
        return int(self.ProductionRessourcesNeeded[COMMAND_POINTS_KEY])
    
    @command_point_cost.setter
    def command_point_cost(self: Self, value: int) -> None:
        self.ProductionRessourcesNeeded[COMMAND_POINTS_KEY] = value
from __future__ import annotations

from asyncio import Transport
from typing import Callable, Iterable, Self

import context.mod_creation
import utils.ndf.ensure as ensure
from constants.ndf_paths import DECK_SERIALIZER, DIVISION_RULES
from creators.unit.abc import UnitCreator
from managers.unit_id import UnitIdManager
from metadata.division import DivisionMetadata
from metadata.unit import UnitMetadata
from model.deck_unite_rule import TDeckUniteRule
from ndf_parse.model import List, ListRow, Map, MapRow, MemberRow, Object
from utils.ndf.decorators import ndf_path
from utils.types.message import Message, try_nest

from .division_rule_lookup import DivisionRuleLookup
from .types import UnitDelegate, UnitsPerXp
from .unit_rules import UnitRules


def ensure_unit_path_list(transports: str | list[str | None] | None) -> list[str | None] | None:
        if transports is None:
            return None
        if isinstance(transports, str):
            transports = [transports]
        return [ensure.unit_path(x) if x is not None else None for x in transports]


class DivisionUnitRegistry(object):
    # ctx: ModCreationContext
    def __init__(self: Self, ctx: context.mod_creation.ModCreationContext, metadata: DivisionMetadata, parent_msg: Message | None = None, *division_priorities: str):
        self.ctx = ctx
        self.metadata = metadata
        self.units: list[UnitRules] = []
        self.parent_msg = parent_msg
        self.unit_ids = UnitIdManager(ctx.unit_id_cache, metadata.id * 1000)
        self.lookup = DivisionRuleLookup(ctx.ndf[DIVISION_RULES], *division_priorities)
    
    @ndf_path(DECK_SERIALIZER)
    def edit_deck_serializer(self: Self, ndf: List):
        unit_ids: Map = ndf.by_name("DeckSerializer").value.by_member('UnitIds').value
        for k, v in self.unit_ids.items:
            unit_ids.add(k=k, v=str(v))

    def register(self: Self,
                 unit: str | UnitDelegate,
                 packs: int,
                 units_per_xp: UnitsPerXp | None = None,
                 transports: str | Iterable[Transport] | None = None) -> None:
        """Adds a unit to the registry.

        Parameters
        ----------
        self : Self
            The registry to which the unit is being added
        unit : str | Callable[[context.mod_creation.ModCreationContext], UnitMetadata]
            If str: the DescriptorName of a vanilla* unit to register.
            If Callable: a function which generates the unit to register.
        packs : int
            How many packs the division should have of this unit.
        units_per_xp : tuple[int, int, int, int] | None, optional
            If tuple[int, int, int, int]: How many units per pack should be available at each of the 4 veterancy levels.
            If None, the registry will use its lookup property to fill this:
            - If registering a vanilla unit, the registry will look for any entries matching it;
            - If registering a modded unit, the registry will look for any entries matching its src_unit. 
        transports : str | list[str] | None, optional
            Sets both the transports and the AvailableWithoutTransport property.
            If str, the unit will be transported by only the unit specified and will not be available without transport.
            If None, the unit will only be available without transport.
            If Iterable, the unit will be available with the specified transports; it will also be available without transport iff None is in the iterable.
        """
        transports = ensure_unit_path_list(transports)
        if isinstance(unit, str):
            unit: UnitMetadata = UnitMetadata(unit)
            self._register(unit, None, packs, units_per_xp, transports)
        elif isinstance(unit, UnitDelegate):
            unit: UnitCreator = unit(self.ctx)            
            self._register(unit.new_unit, unit.src_unit, packs, units_per_xp, transports)

    def _look_up_rule_items(self: Self,
                      unit: UnitMetadata,
                      units_per_xp: UnitsPerXp | None,
                      transports: Iterable[Transport] | None,
                      msg: Message)\
                        -> tuple[UnitsPerXp, list[Transport] | None]:
        if units_per_xp is not None and transports is not None:
            return (units_per_xp, transports)
        rule: TDeckUniteRule = self.lookup.look_up(unit, msg)
        if units_per_xp is None:
            units_per_xp = rule.units_per_xp
        if transports is None and isinstance(rule.AvailableTransportList, list[str]):
            transports: list[str | None] = rule.AvailableTransportList
            if rule.AvailableWithoutTransport:
                transports.append(None)
        return (units_per_xp, transports)

    def _register(self: Self,
                  unit: UnitMetadata,
                  src: UnitMetadata | None,
                  packs: int,
                  units_per_xp: UnitsPerXp,
                  transports: str | list[str] | None) -> None:
        modded: bool = src is not None
        with try_nest(self.parent_msg, f'Registering {'modded' if modded else 'vanilla'} unit {unit.name}') as msg:
            units_per_xp, transports = self._look_up_rule_items(src if modded else unit,
                                                                units_per_xp,
                                                                transports,
                                                                msg)
            self.units.append(UnitRules(unit, packs, units_per_xp, transports))
            if modded:
                self.unit_ids.register(unit.descriptor.path)

    def pack_list(self: Self) -> Map:
        return ensure._map(x.pack for x in self.units)
    
    def division_rules(self: Self) -> Object:
        return ensure._object('TDeckDivisionRule',
                            UnitRuleList=[unit.rule.to_ndf()
                                          for unit
                                          in self.units])
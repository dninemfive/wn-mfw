from typing import Self

from creators.unit.abc import UnitCreator
from metadata.unit import UnitMetadata
from model.deck_unite_rule import TDeckUniteRule
from ndf_parse.model import MapRow
from .types import UnitsPerXp, Transport


class UnitRules(object):
    def __init__(self: Self,
                 unit: UnitMetadata | UnitCreator,
                 num_packs: int,
                 units_per_pack: UnitsPerXp,
                 transports: list[Transport] | None = None):
        if isinstance(unit, UnitCreator):
            unit = unit.new_unit
        self.unit: UnitMetadata = unit
        self.num_packs = num_packs
        self.rule: TDeckUniteRule = TDeckUniteRule.make(unit, units_per_pack, transports, None in transports)

    @property
    def pack(self: Self) -> MapRow:
        return MapRow(key=self.unit.deck_pack_descriptor.path, value=str(self.num_packs))

    @staticmethod
    def from_deck_unite_rule(unit: UnitMetadata, num_packs: int, rule: TDeckUniteRule) -> Self:
        return UnitRules(unit,
                        num_packs,
                        rule.units_per_xp,
                        rule.AvailableTransportList,
                        rule.AvailableWithoutTransport)
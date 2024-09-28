from context.mod_creation import ModCreationContext
from metadata.division_unit_registry import UnitRules
from units._weapons import M16A2, M249, TOW_SCAT
from creators.unit.infantry import InfantryUnitCreator


def create(ctx: ModCreationContext) -> UnitRules | None:
    # SCAT
    with ctx.create_infantry_unit("#RECO2 SCAT", "US", "Scout_US", [(M16A2, 5), (M249, 1), (TOW_SCAT, 1)]) as scat:
        squad: InfantryUnitCreator = InfantryUnitCreator.copy_parent(ctx.guids, scat, 'US', )
        squad.apply(ctx.ndf, scat.msg)
        squad.edit_unit(scat)
        scat.UpgradeFromUnit='d9_RECO2_IEW_TEAM_US'
        return UnitRules(scat, 3, [0, 6, 4, 0])
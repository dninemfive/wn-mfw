from typing import Callable, Iterable, Self

from _constants._base_formatter import _base_formatter, MEMBER_LEN
from ndf_parse.model import List, MemberRow

from warno_mfw.utils.ndf import ensure

from .._validator import StandardValidationSet, ValidationSet


class MemberDef(object):
    def __init__(self:              Self,
                 member_name:       str,
                 prefix:            str | None = None,
                 special_formatter: Callable[[Self], str] | None = None,
                 aliases:           dict[str | Iterable[str]] | None = None):
        self.member_name = member_name
        self.prefix = prefix
        self.values: set[str] = set()
        self.special_formatter = special_formatter
        self.aliases = aliases
        self.needs_quotes: bool | None = None

    def add(self: Self, row: MemberRow) -> None:
        value = row.value
        needs_quotes = value.startswith('"') or value.startswith("'")
        if self.needs_quotes is None:
            self.needs_quotes = needs_quotes
        elif not (self.needs_quotes == needs_quotes):
            print(f'Inconsistent quotation requirements in member {self.member_name}!')
        
        if isinstance(value, str):
            self.values.add(ensure.no_prefix(ensure.unquoted(value), self.prefix))
        elif isinstance(value, List):
            for item in value:
                self.values.add(ensure.no_prefix(ensure.unquoted(item.value), self.prefix))

    def literal_lines(self: Self) -> Iterable[str]:
        if self.special_formatter is not None:
            yield from self.special_formatter(self)
        else:
            yield from _default_formatter(self)

    def validator(self: Self) -> ValidationSet:
        return StandardValidationSet(self.needs_quotes, self.prefix, )
    
def _default_formatter(member_def: MemberDef) -> Iterable[str]:
    yield _base_formatter(member_def.member_name, member_def.values)
    if member_def.aliases is not None and any(member_def.aliases):
        yield _base_formatter(f'{member_def.member_name}Alias', member_def.aliases.values())
        yield f'{f'{member_def.member_name}OrAlias'.ljust(MEMBER_LEN)}= {member_def.member_name} | {member_def.member_name}Alias'
import typing_extensions as typing_
from collections import abc
from enum import auto
from math import nan

import attrs
from attrs import validators
from cattrs import gen, override

from .converter import conv

from supermechs.abc.item import ItemID
from supermechs.api import Element, Tier, Type
from supermechs.enums._base import PartialEnum
from supermechs.ext.deserializers.stats import RawStatsMapping

__all__ = ("ItemWithStats", "ItemWithTiers", "TransformRange")

_EMPTY_STATS: RawStatsMapping = {}


class ExtendedType(PartialEnum):
    UNKNOWN = auto()


@attrs.define
class TransformRange:
    lower: Tier
    upper: Tier

    def __contains__(self, tier: Tier, /) -> bool:
        return self.lower <= tier <= self.upper

    def __iter__(self) -> abc.Iterator[Tier]:
        return (Tier.of_value(i) for i in range(self.lower, self.upper + 1))

    @classmethod
    def from_str(cls, arg: str, /) -> typing_.Self:
        arg = arg.strip()
        if len(arg) == 1:
            tier = Tier.of_initial(arg)
            return cls(tier, tier)

        if len(arg) != 3:  # noqa: PLR2004
            msg = f"Cannot interpret {arg} as transformation range"
            raise ValueError(msg)

        lower = Tier.of_initial(arg[0])
        upper = Tier.of_initial(arg[2])

        if lower > upper:
            msg = "Lower bound greater than upper bound"
            raise ValueError(msg)

        return cls(lower, upper)


@attrs.define
class Point2D:
    x: float
    y: float


@attrs.define(kw_only=True)
class TorsoAttachment:
    leg1: Point2D
    leg2: Point2D
    side1: Point2D
    side2: Point2D
    side3: Point2D
    side4: Point2D
    top1: Point2D
    top2: Point2D


@attrs.define(kw_only=True)
class BaseItem:
    id: ItemID = attrs.field(validator=validators.ge(1))
    name: str = attrs.Factory(lambda self: f"Item #{self.id}", takes_self=True)
    type: Type | ExtendedType = ExtendedType.UNKNOWN
    element: Element = Element.UNKNOWN
    transform_range: TransformRange = TransformRange(Tier.COMMON, Tier.COMMON)
    tags: abc.Sequence[str] = ()
    image: str | None = None
    width: int = 0
    height: int = 0
    joints: Point2D | TorsoAttachment | None = None


@attrs.define(kw_only=True)
class ItemWithStats(BaseItem):
    stats: RawStatsMapping = _EMPTY_STATS


@attrs.define(kw_only=True)
class ItemWithTiers(BaseItem):
    # fmt: off
    common:        RawStatsMapping = _EMPTY_STATS
    max_common:    RawStatsMapping = _EMPTY_STATS
    rare:          RawStatsMapping = _EMPTY_STATS
    max_rare:      RawStatsMapping = _EMPTY_STATS
    epic:          RawStatsMapping = _EMPTY_STATS
    max_epic:      RawStatsMapping = _EMPTY_STATS
    legendary:     RawStatsMapping = _EMPTY_STATS
    max_legendary: RawStatsMapping = _EMPTY_STATS
    mythical:      RawStatsMapping = _EMPTY_STATS
    max_mythical:  RawStatsMapping = _EMPTY_STATS
    divine:        RawStatsMapping = _EMPTY_STATS
    # fmt: on


def _structure_stat(obj: float | abc.Sequence[float], _: type) -> float | abc.Sequence[float]:
    if isinstance(obj, abc.Sequence):
        return conv.structure(obj, abc.Sequence[float])

    return conv.structure(obj, float)


def _convert_float(val: float | None, _: type) -> float:
    return nan if val is None else float(val)


conv.register_structure_hook_func(
    lambda cls: issubclass(cls, PartialEnum),
    lambda val, cls: cls.of_name(val),
)
conv.register_structure_hook(float, _convert_float)
conv.register_structure_hook(float | abc.Sequence[float], _structure_stat)
conv.register_structure_hook(TransformRange, lambda obj, _: TransformRange.from_str(obj))

_hook = gen.make_dict_structure_fn(
    ItemWithStats,
    conv,
    joints=override(rename="attachments"),
)
conv.register_structure_hook(ItemWithStats, _hook)
_hook = gen.make_dict_structure_fn(
    ItemWithTiers,
    conv,
    joints=override(rename="attachments"),
)
conv.register_structure_hook(ItemWithTiers, _hook)

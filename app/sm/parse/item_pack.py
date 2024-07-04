import typing
from collections import abc

import attrs
from cattrs import gen

from .converter import conv
from .items import ItemWithStats, ItemWithTiers

from supermechs.abc.item_pack import PackKey


@attrs.define(kw_only=True)
class Rectangle:
    width: int
    height: int
    x: int
    y: int


@attrs.define(kw_only=True)
class PackData:
    version: typing.Literal["1", "2", "3"] = "1"
    key: PackKey
    name: str = ""
    description: str = ""
    base_url: str = ""
    items: abc.Sequence[ItemWithStats | ItemWithTiers]
    sprites_sheet: str = ""
    sprites_map: abc.Mapping[str, Rectangle] = {}


_hook = gen.make_dict_structure_fn(
    PackData,
    conv,
    sprites_sheet=gen.override(rename="spritesSheet"),
    sprites_map=gen.override(rename="spritesMap"),
)
conv.register_structure_hook(PackData, _hook)

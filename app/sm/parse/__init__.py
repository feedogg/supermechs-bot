import typing
from collections import abc

from .converter import conv, convert_config
from .item_pack import PackData, Rectangle
from .items import *

__all__ = ["convert_config", "parse_item_pack"]


def parse_item_pack(data: abc.Mapping[str, typing.Any], /) -> PackData:
    return conv.structure_attrs_fromdict(data, PackData)

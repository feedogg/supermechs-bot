import typing
import typing_extensions as typing_
from collections import abc

import cattrs

from supermechs.abc.item_pack import PackKey

conv = cattrs.Converter()


class ConfigDict(typing_.TypedDict, total=False, closed=True):
    key: typing_.Required[PackKey]
    name: str
    description: str
    base_url: str


def convert_config(obj: abc.MutableMapping[str, typing.Any], /) -> None:
    try:
        cfg = obj.pop("config")

    except KeyError:
        return

    config = conv.structure(cfg, ConfigDict)
    obj.update(config)

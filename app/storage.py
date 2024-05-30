import typing
from collections import abc

import anyio
import anyio.lowlevel
import disnake
import orjson
from cattrs.preconf.orjson import OrjsonConverter

from factories import player_factory
from models import Player
from shared.memo import Memo

from supermechs.abc.item import Paint
from supermechs.api import Item, Tier

players = Memo(player_factory, lambda user: user.id)


async def get_player(user: disnake.abc.User, /) -> Player:
    await anyio.lowlevel.checkpoint()
    return players(user)


class _DataFormat(typing.TypedDict):
    version: typing.Literal["1"]
    players: abc.Mapping[int, Player]


converter = OrjsonConverter()


class _ItemData(typing.TypedDict):
    data: str
    stage: Tier
    level: int
    paint: Paint | None


def structure_item(data: _ItemData, cls: type[Item]) -> Item: ...


def unstructure_item(obj: Item) -> _ItemData:
    return {
        "data": f"{obj.data.pack_key}@{obj.data.id}",
        "stage": obj.stage.tier,
        "level": obj.level,
        "paint": obj.paint
    }


converter.register_structure_hook(Item, structure_item)
converter.register_unstructure_hook(Item, unstructure_item)


async def load() -> None:
    path = anyio.Path("./data.json")
    data = converter.loads(await path.read_bytes(), _DataFormat)
    players.mapping.update(data["players"])


async def dump() -> None:
    data = converter.dumps({"version": "1", "players": players.mapping}, option=orjson.OPT_INDENT_2)
    path = anyio.Path("./data.json")
    await path.write_bytes(data)

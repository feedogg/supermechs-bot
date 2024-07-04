from collections import abc

from supermechs.api import Item, ItemData, Mech, Type


def iter_displayable(mech: Mech, /) -> abc.Iterator[Item]:
    for item in mech.iter_items("body", "weapons"):
        if item is not None:
            yield item


def is_mech_sprite_part(item: Item | ItemData, /) -> bool:
    return item.type in {Type.TORSO, Type.LEGS, Type.DRONE, Type.SIDE_WEAPON, Type.TOP_WEAPON}

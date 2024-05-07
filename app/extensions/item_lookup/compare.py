from functools import partial

from disnake import ButtonStyle, Embed, Locale, MessageInteraction, ui

import i18n
from assets import STAT
from discord_extensions import debug_footer
from discord_extensions.ui import ActionButton, ToggleButton
from discord_extensions.ui.store import ComponentStore

from .helpers import try_shorten

from supermechs.abc.stats import StatType
from supermechs.api import MAX_SHOP, ItemData, Stat
from supermechs.tools.stats import buff_stats, max_stats


def item_compare_view(
    store: ComponentStore,
    embed: Embed,
    item_a: ItemData,
    item_b: ItemData,
    locale: Locale,
) -> ui.Components[ui.MessageUIComponent]:
    gettext = partial(i18n.get_message, locale)
    max_item_stats = (max_stats(item_a), max_stats(item_b))

    @store.bind(ToggleButton(label=gettext("item-compare-ui-buffs")))
    async def buffs_button(inter: MessageInteraction) -> None:
        buffs_button.toggle()
        update()
        await inter.response.edit_message(embed=embed, components=layout)

    @store.bind(ActionButton(label=gettext("ui-quit"), style=ButtonStyle.red))
    async def quit_button(inter: MessageInteraction) -> None:
        await inter.response.defer()
        store.stop()

    def update() -> None:
        stats_a, stats_b = max_item_stats

        if buffs_button.on:
            stats_a = buff_stats(stats_a, MAX_SHOP)
            stats_b = buff_stats(stats_b, MAX_SHOP)

        raise NotImplementedError
        name_field, first_field, second_field = stats_to_fields(stats_a, stats_b, locale=locale)

        if require_jump := item_a.tags.require_jump:
            first_field.append("❕")

        if item_b.tags.require_jump:
            second_field.append("❕")
            require_jump = True

        if require_jump:
            emoji = STAT[Stat.jump]
            name_field.append(f"{emoji} **{gettext('item-compare-jump-required')}**")

        modify_field_at = embed.set_field_at if embed._fields else embed.insert_field_at

        modify_field_at(0, gettext("item-compare-stat-header"), "\n".join(name_field))
        modify_field_at(1, try_shorten(item_a.name), "\n".join(first_field))
        modify_field_at(2, try_shorten(item_b.name), "\n".join(second_field))

        if __debug__:
            debug_footer(embed)

    layout = [[buffs_button, quit_button]]
    return layout


def compare_numbers(
    x: StatType, y: StatType, lower_is_better: bool = False
) -> tuple[StatType, StatType]:
    return (x - y, 0) if lower_is_better ^ (x > y) else (0, y - x)

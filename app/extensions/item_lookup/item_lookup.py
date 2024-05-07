import io
from functools import partial
from itertools import zip_longest

from disnake import ButtonStyle, Embed, Locale, MessageInteraction, ui

import i18n
from assets import STAT
from discord_extensions import SPACE, debug_footer
from discord_extensions.ui import ActionButton, ToggleButton
from discord_extensions.ui.store import ComponentStore
from sm.asset_utils import item_transform_range

from .helpers import get_row_width, iter_formatted_stats

from supermechs.api import MAX_SHOP, ItemData, Stat
from supermechs.tools.stats import buff_stats, max_stats
from supermechs.utils import contains_any_of


def item_view(
    store: ComponentStore,
    embed: Embed,
    item: ItemData,
    locale: Locale,
    compact: bool,
) -> ui.Components[ui.MessageUIComponent]:
    populate_fields = compact_fields if compact else default_fields
    populate_fields(embed, item, False, False, locale)
    gettext = partial(i18n.get_message, locale)

    if __debug__:
        debug_footer(embed)

    @store.bind(ToggleButton(label=gettext("item-lookup-ui-buffs")))
    async def buff_button(inter: MessageInteraction) -> None:
        buff_button.toggle()
        await update(inter)

    @store.bind(ToggleButton(label=gettext("item-lookup-ui-average")))
    async def avg_button(inter: MessageInteraction) -> None:
        avg_button.toggle()
        await update(inter)

    @store.bind(ActionButton(label=gettext("ui-quit"), style=ButtonStyle.red))
    async def quit_button(inter: MessageInteraction) -> None:
        store.stop()
        await inter.response.defer()

    async def update(inter: MessageInteraction) -> None:
        embed.clear_fields()
        populate_fields(embed, item, buff_button.on, avg_button.on, locale)

        if __debug__:
            debug_footer(embed, replace=True)

        await inter.response.edit_message(embed=embed, components=layout)

    layout = [[buff_button, quit_button]]

    if contains_any_of(
        item.start_stage.min(),
        Stat.physical_damage,
        Stat.electric_damage,
        Stat.explosive_damage,
    ):
        layout[0].insert(1, avg_button)

    return layout


def default_fields(
    embed: Embed, item: ItemData, buffs_enabled: bool, avg: bool, locale: Locale
) -> None:
    """Fills embed with detailed info about an item."""
    gettext = partial(i18n.get_message, locale)
    embed.add_field(
        gettext("item-lookup-transform-range"),
        item_transform_range(item),
        inline=False,
    )

    spaced = False
    string = io.StringIO()
    cost_stats = (Stat.backfire, Stat.heat_generation, Stat.energy_cost)

    for stat, str_value in iter_formatted_stats(max_stats(item), avg):
        if not spaced and stat in cost_stats:
            string.write("\n")
            spaced = True

        string.write(f"{STAT[stat]} **{str_value}** {i18n.get_stat_name(locale, stat)}\n")

    if item.tags.require_jump:
        string.write(f"{STAT[Stat.jump]} **{gettext('item-lookup-jump-required')}**")

    embed.add_field(gettext("item-lookup-stats"), string.getvalue(), inline=False)


def compact_fields(
    embed: Embed,
    item: ItemData,
    buffs_enabled: bool,
    avg: bool,
    locale: Locale,
) -> None:
    """Fills embed with reduced info about an item."""
    del locale
    lines: list[str] = []

    stats = max_stats(item)

    if buffs_enabled:
        stats = buff_stats(stats, MAX_SHOP)

    for stat_key, str_value in iter_formatted_stats(stats, avg, 0):
        lines.append(f"{STAT[stat_key]} **{str_value}**")

    if item.tags.require_jump:
        lines.append(f"{STAT[Stat.jump]}❗")

    line_count = len(lines)
    div = get_row_width(line_count, 4)

    field_text = ("\n".join(lines[i : i + div]) for i in range(0, line_count, div))
    transform_range = item_transform_range(item)

    for name, field in zip_longest((transform_range,), field_text, fillvalue=SPACE):
        embed.add_field(name, field)

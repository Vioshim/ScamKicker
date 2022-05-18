# Copyright (c) 2022 Vioshim
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from contextlib import suppress
from logging import getLogger, setLoggerClass
from re import IGNORECASE, MULTILINE, compile

from aiohttp import ClientResponseError, ClientSession
from naff.api.events.discord import MessageCreate
from naff.client import Client
from naff.client.errors import NotFound
from naff.models.discord import Activity, Message
from naff.models.discord.color import FlatUIColors
from naff.models.discord.embed import Embed, EmbedAttachment, EmbedField, EmbedFooter
from naff.models.discord.enums import ActivityType, Permissions
from naff.models.naff.context import PrefixedContext
from naff.models.naff.extension import Extension
from naff.models.naff.listener import listen
from naff.models.naff.prefixed_commands import prefixed_command
from naff.models.naff.tasks.task import Task
from naff.models.naff.tasks.triggers import IntervalTrigger
from yarl import URL

from classes.logger import ColoredLogger

setLoggerClass(ColoredLogger)

logger = getLogger(__name__)


API = URL.build(scheme="https", host="phish.sinking.yachts", path="/v2")
WARN_ICON = "https://cdn.discordapp.com/emojis/498095663729344514.webp?size=240&quality=lossless"
WHITE_BAR = "https://cdn.discordapp.com/attachments/748384705098940426/880837466007949362/image.gif"
DOMAIN_DETECT = compile(
    r"http[s]?://((?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]| %[0-9a-fA-F][0-9a-fA-F])+)",
    IGNORECASE | MULTILINE,
)


class ScamAPI(Extension):
    """Extension used for detection of popular reported discord scams."""

    def __init__(self, _: Client) -> None:
        """This is the init method of the ScamAPI Scale

        Parameters
        ----------
        _ : ScamKicker
            Bot parameter
        """
        self.scam_urls: set[str] = set()
        self.scam_changes.start()

    @property
    def info(self) -> str:
        """Information string

        Returns
        -------
        str
            Information for bot status
        """
        if guilds := self.bot.guilds:
            return f"{len(guilds):02d} Servers"
        return "Bot restarting."

    @property
    def session(self) -> ClientSession:
        return self.bot.session

    async def load_all(self):
        """This connects to the API's endpoint for receiving
        all entries.
        """
        async with self.session.get(API / "all") as data:
            if data.status == 200:
                entries: list[str] = await data.json()
                self.scam_urls.update(entries)
                logger.info("Loaded %s URLs.", len(entries))

    async def load_recent(self):
        """This connects to the API's endpoint for receiving
        recent entries in the last 60 seconds.
        """
        async with self.session.get(API / "recent/60") as data:
            if data.status == 200:
                entries: list[dict[str, str]] = await data.json()
                added: set[str] = set()
                removed: set[str] = set()
                for item in entries:
                    domains: list[str] = item.get("domains", [])
                    match item.get("type"):
                        case "add":
                            added.update(domains)
                        case "delete":
                            removed.add(domains)
                if entries:
                    logger.info(
                        "%s URL Change(s) have occurred in the last 60 seconds.",
                        len(entries),
                    )
                if added:
                    self.scam_urls.update(added)
                    logger.info(
                        "%s URL(s) added:\n%s",
                        len(added),
                        "\n".join(f"- {x}" for x in added),
                    )
                if removed:
                    self.scam_urls.difference_update(removed)
                    logger.info(
                        "%s URL(s) removed:\n%s",
                        len(removed),
                        "\n".join(f"- {x}" for x in added),
                    )

    @Task.create(trigger=IntervalTrigger(seconds=60))
    async def scam_changes(self) -> None:
        """Function to load API Changes in the last 60 seconds"""
        try:
            if not self.scam_urls:
                await self.load_all()
            else:
                await self.load_recent()
        except ClientResponseError:
            logger.error("Unable to connect with API.")

        if not self.bot.activity or self.bot.activity.name != self.info:
            activity = Activity.create(name=self.info, type=ActivityType.WATCHING)
            await self.bot.change_presence(activity=activity)

    @listen()
    async def on_ready(self) -> None:
        """Function loads all entries from the API and starts the Task"""
        await self.scam_changes()

    @prefixed_command()
    async def stats(self, ctx: PrefixedContext) -> None:
        """Functon to get stats of the bot

        Parameters
        ----------
        ctx : MessageContext
            Message Context
        """
        await ctx.message.reply(
            embed=Embed(
                title="Bot Stats",
                url="https://github.com/Vioshim/ScamKicker",
                image=EmbedAttachment(url=WHITE_BAR),
                thumbnail=EmbedAttachment(url=self.bot.user.avatar.url),
                color=FlatUIColors.CONCRETE,
                fields=[
                    EmbedField(
                        name="Servers",
                        value=str(len(self.bot.guilds)),
                        inline=True,
                    ),
                    EmbedField(
                        name="Scam Entries",
                        value=str(len(self.scam_urls)),
                        inline=True,
                    ),
                ],
                footer=EmbedFooter(text="Results obtained directly by the API"),
            )
        )

    @listen()
    async def on_message_create(self, event: MessageCreate) -> None:
        """Message Handler function

        Parameters
        ----------
        message : MessageCreate
            Message to detect
        """
        message: Message = event.message

        user = message.author

        if not message.content:
            return

        elements: list[str] = DOMAIN_DETECT.findall(message.content)
        intersection = self.scam_urls.intersection(elements)
        if not intersection:
            return

        scams = ", ".join(intersection)
        if not (base_guild := message.guild):
            await message.reply(
                embed=Embed(
                    title="Alert - Scam(s) Detected",
                    url=str(API.with_path("/docs")),
                    description="\n".join(f"• {x}" for x in intersection),
                    image=EmbedAttachment(url=WHITE_BAR),
                    thumbnail=EmbedAttachment(url=WARN_ICON),
                    color=FlatUIColors.POMEGRANATE,
                    footer=EmbedFooter(text="Results obtained directly by the API"),
                )
            )
            logger.info("%s checked for the URL(s): %s", str(message.author), scams)
        elif channel := message.channel:
            if base_guild.me.channel_permissions(channel).MANAGE_MESSAGES:
                try:
                    await message.delete()
                except NotFound:
                    pass
                else:
                    logger.info(
                        "Deleted %s(%s)' message at Guild: %s(%s), Channel: %s, ID: %s, Scams: %s",
                        str(message.author),
                        message.author.id,
                        base_guild.name,
                        base_guild.id,
                        message.channel.id,
                        message.id,
                        scams,
                    )
            logger.info("Kicking %s(%s) from all servers.", str(user), user.id)
            for guild in self.bot.guilds:
                with suppress(NotFound):
                    if (
                        guild.me.has_permission(Permissions.KICK_MEMBERS)
                        and (owner := guild.get_owner())
                        and user != owner
                        and guild.me.top_role > user.top_role
                    ):
                        reason = f"Nitro Scam Victim, Scam(s) sent: {scams}"
                        await user.kick(reason=reason)


def setup(bot: Client) -> None:
    """Set up Function

    Parameters
    ----------
    bot : Bot
        Bot
    """
    ScamAPI(bot)

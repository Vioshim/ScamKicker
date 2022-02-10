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
from os import getenv
from re import IGNORECASE, MULTILINE, compile

from aiohttp import ClientSession
from dis_snek.api.events.discord import MessageCreate
from dis_snek.client import Snake
from dis_snek.client.errors import NotFound
from dis_snek.ext.tasks.task import Task
from dis_snek.ext.tasks.triggers import IntervalTrigger
from dis_snek.models.discord import Activity, Message, Permissions
from dis_snek.models.discord.enums import ActivityType
from dis_snek.models.snek import MessageContext, Scale, listen, message_command
from orjson import dumps

API = "https://phish.sinking.yachts/v2"
API_PARAM = {"X-Identity": getenv("API_LABEL", "ScamKicker")}

DOMAIN_DETECT = compile(
    r"http[s]?://((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9])",
    IGNORECASE | MULTILINE,
)


class ScamAPI(Scale):
    """Test Scale used for testing the api"""

    @property
    def info(self) -> str:
        return f"{len(self.bot.guilds):02d} Servers"

    def __init__(self, _: Snake) -> None:
        """This is the init method of the ScamAPI Scale

        Parameters
        ----------
        _ : Snake
            Bot parameter
        """
        self.session = ClientSession(
            json_serialize=dumps,
            raise_for_status=True,
        )
        self.scam_urls = set()
        self.task = Task(
            callback=self.scam_changes,
            trigger=IntervalTrigger(seconds=60),
        )

    async def scam_changes(self) -> None:
        """Function to load API Changes in the last 60 seconds"""
        async with self.session.get(f"{API}/recent/60", params=API_PARAM) as data:
            if data.status == 200:
                items: list[dict[str, str]] = await data.json()
                for item in items:
                    handler = item.get("type")
                    domains: set[str] = set(item.get("domains", []))
                    if handler == "add":
                        self.scam_urls |= domains
                    elif handler == "delete":
                        self.scam_urls -= domains

        if self.bot.activity.name != self.info:
            activity = Activity.create(name=self.info, type=ActivityType.WATCHING)
            await self.bot.change_presence(activity=activity)

    @listen()
    async def on_ready(self) -> None:
        """Function loads all entries from the API and starts the Task"""
        if not self.scam_urls:
            async with self.session.get(
                f"{API}/all",
                params=API_PARAM,
            ) as data:
                if data.status == 200:
                    entries: list[str] = await data.json()
                    self.scam_urls = set(entries)
            self.task.start()

    @message_command()
    async def stats(self, ctx: MessageContext) -> None:
        """Functon to get stats of the bot

        Parameters
        ----------
        ctx : MessageContext
            Message Context
        """
        await ctx.send(
            content=f"{self.info}, {len(self.scam_urls):04d} Scam Entries.",
            reply_to=ctx.message,
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
        if scams := ", ".join(self.scam_urls.intersection(elements)):
            channel = await self.bot.get_channel(message._channel_id)
            if base_guild := message.guild:
                perms: Permissions = base_guild.me.channel_permissions(channel)
                if perms.MANAGE_MESSAGES:
                    with suppress(NotFound):
                        await message.delete()

                for guild in self.bot.guilds:
                    with suppress(NotFound):
                        if (
                            guild.me.has_permission(Permissions.KICK_MEMBERS)
                            and (member := await guild.get_member(user.id))
                            and (owner := await guild.get_owner())
                            and member != owner
                            and guild.me.top_role > member.top_role
                        ):
                            await member.kick(reason=f"Nitro Scam Victim, Scam/s sent {scams}")
                return
            await channel.send("That's a nitro scam according to the API.", reply_to=message)


def setup(bot: Snake) -> None:
    """Set up Function

    Parameters
    ----------
    bot : Bot
        Bot
    """
    ScamAPI(bot)

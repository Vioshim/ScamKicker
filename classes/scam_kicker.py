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


from aiohttp import ClientSession
from naff.client.client import Client
from naff.models.discord.enums import Intents


class ScamKicker(Client):
    def __init__(self, session: ClientSession) -> None:
        """Init Method

        Parameters
        ----------
        session : ClientSession
            aiohttp client session
        """
        super(ScamKicker, self).__init__(
            intents=(
                Intents.GUILD_MESSAGE_CONTENT
                | Intents.MESSAGES
                | Intents.GUILD_MEMBERS
                | Intents.GUILDS
                | Intents.GUILD_BANS
            ),
            default_prefix="sk!",
        )
        self.session = session

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


from os import getenv

from dis_snek import Intents, Snake
from dotenv import load_dotenv

try:
    from uvloop import install  # type: ignore

    install()
except ModuleNotFoundError:
    print("Launched without uvloop")
finally:
    load_dotenv()

intents = Intents.MESSAGES | Intents.GUILD_MEMBERS | Intents.GUILDS | Intents.GUILD_BANS

bot = Snake(
    default_prefix="sk!",
    intents=intents,
)
bot.load_extension("scales.scam_api")
bot.start(getenv("DISCORD_TOKEN"))

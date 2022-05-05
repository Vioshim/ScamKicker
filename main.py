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


from asyncio import run
from logging import getLogger, setLoggerClass
from os import getenv

from aiohttp import ClientSession
from dotenv import load_dotenv
from orjson import dumps

from classes.logger import ColoredLogger
from classes.scam_kicker import ScamKicker

load_dotenv()
setLoggerClass(ColoredLogger)
logger = getLogger(__name__)

try:
    from uvloop import install  # type: ignore

    install()
except ModuleNotFoundError:
    logger.warning("Launched without uvloop")


async def main():
    """Main Execution function"""
    try:
        async with ClientSession(
            json_serialize=dumps,
            raise_for_status=True,
            headers={"X-Identity": getenv("API_LABEL", "ScamKicker")},
        ) as session:
            bot = ScamKicker(session=session)
            bot.load_extension("scales.scam_api")
            await bot.astart(token=getenv("DISCORD_TOKEN"))
    except Exception as e:
        logger.critical("An exception occurred while trying to connect.", exc_info=e)


if __name__ == "__main__":
    run(main())

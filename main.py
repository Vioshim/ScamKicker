# Copyright 2022 Vioshim
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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

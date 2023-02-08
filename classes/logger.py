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


from datetime import datetime
from logging import INFO, Formatter, Logger, LogRecord, StreamHandler

from pytz import UTC, timezone

__all__ = ("ColoredLogger",)

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


def formatter_message(message: str, use_color=True) -> str:
    """Message Formatter

    Parameters
    ----------
    message: str
        Message to format
    use_color: bool = True
        If using colors or not

    Returns
    -------
    str:
        message formatted
    """
    if use_color:
        message = message.replace("$RESET", RESET_SEQ)
        return message.replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "")
        return message.replace("$BOLD", "")


COLORS = dict(
    WARNING=YELLOW,
    INFO=BLUE,
    DEBUG=WHITE,
    CRITICAL=YELLOW,
    ERROR=RED,
)


class ColoredFormatter(Formatter):
    def __init__(self, msg: str, use_color=True):
        """Init Method

        Parameters
        ----------
        msg: str
            Format
        use_color: bool = True
            If using color or not
        """
        super().__init__(fmt=msg, datefmt=r"%Y-%m-%d,%H:%M:%S.%f")
        self.use_color = use_color

    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp, tz=UTC)
        return dt.astimezone(timezone("America/Bogota"))

    def formatTime(self, record: LogRecord, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            try:
                s = dt.isoformat(timespec="milliseconds")
            except TypeError:
                s = dt.isoformat()
        return s

    def format(self, record: LogRecord) -> str:
        """Formatting Method

        Parameters
        ----------
        record : LogRecord
            Record

        Returns
        -------
        str
            Formatted value
        """
        level_name: str = record.levelname
        if self.use_color and level_name in COLORS:
            level_name_color = COLOR_SEQ % (30 + COLORS[level_name]) + level_name
            record.levelname = level_name_color + RESET_SEQ
            pathname = record.pathname.removesuffix(".py")
            record.pathname = pathname.removeprefix("/app")
        return super(ColoredFormatter, self).format(record)


class ColoredLogger(Logger):
    FORMAT = (
        "$BOLD[%(levelname)s]$RESET%(pathname)s/$BOLD%(funcName)s$RESET〕%(message)s"
    )
    COLOR_FORMAT = formatter_message(FORMAT, True)

    def __init__(self, name: str):
        """Init Method

        Parameters
        ----------
        name: str
            Logger's Name
        """
        super(ColoredLogger, self).__init__(name, level=INFO)
        color_formatter = ColoredFormatter(self.COLOR_FORMAT)
        console = StreamHandler()
        console.setFormatter(color_formatter)
        self.addHandler(console)

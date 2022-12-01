import logging
from collections import deque
from io import StringIO

import arrow
from disnake import File
from disnake.ext.commands import Cog, Context, command

from cozy.bot import CozyBot
from cozy.checks import is_bot_owner
from cozy.utils.time import discord_timestamp

# The number of lines that will be held by the buffer
BUFFER_SIZE = 100

FORMAT_STRING = "%(asctime)s %(name)s %(levelname)s %(message)s"


class SizedMemoryHandler(logging.StreamHandler):
    """Logging handler stocking up to `max_size` lines into its memory."""

    def __init__(self, max_size: int, *args, **kwargs) -> None:
        self.__queue = deque(maxlen=max_size)

        super().__init__(*args, **kwargs)

    def emit(self, record: logging.LogRecord) -> None:
        """Feed a new record to the handler."""
        message = self.format(record)

        self.__queue.append(message)

    def get_content(self) -> str:
        """Retrieve the content of the buffer."""
        return "\n".join(self.__queue)


class Log(Cog):
    """A cog for retrieving the bot logs."""

    def __init__(self, bot: CozyBot) -> None:
        self.handler = SizedMemoryHandler(BUFFER_SIZE)

        formatter = logging.Formatter(FORMAT_STRING)
        self.handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.addHandler(self.handler)

        self.started_logging = arrow.utcnow()

        self.bot = bot

    def cog_unload(self) -> None:
        """Make sure the handler is removed on unload."""
        root_logger = logging.getLogger()
        root_logger.removeHandler(self.handler)

    @command()
    @is_bot_owner()
    async def logs(self, ctx: Context) -> None:
        """Upload the bot logs to discord."""
        content = StringIO(self.handler.get_content())

        await ctx.send(
            f"Logs since {discord_timestamp(self.started_logging)} uploaded as an attachment",
            file=File(content, "logs.txt"),
        )


def setup(bot: CozyBot) -> None:
    """Load the Info cog."""
    bot.add_cog(Log(bot))

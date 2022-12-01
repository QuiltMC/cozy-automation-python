import logging

import coloredlogs

from cozy.bot import CozyBot
from cozy.constants import GIT_SHA, LOGGING_LEVEL, TOKEN


def main() -> None:
    """Prepare the bot and start it."""
    coloredlogs.install(level=LOGGING_LEVEL)

    logging.getLogger("disnake").setLevel(logging.WARNING)
    logging.getLogger("charset_normalizer").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)

    bot = CozyBot.new()

    logging.info("Loading extensions")
    bot.load_all_modules()

    logging.info(f"Starting bot, build {GIT_SHA}")
    bot.run(TOKEN)


if __name__ == "__main__":
    main()

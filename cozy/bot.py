import ast
import logging
from pathlib import Path
from typing import Any

import arrow
from disnake import AllowedMentions, Game, Intents
from disnake.ext.commands import Bot, when_mentioned

logger = logging.getLogger(__name__)


class CozyBot(Bot):
    """Our main bot class."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.start_time = arrow.utcnow()
        self.all_modules: list[str] = []

    def load_all_modules(self, module: str = "cozy.modules") -> None:
        """Find and load all modules."""
        for file in Path(module.replace(".", "/")).iterdir():
            if file.is_dir():
                self.load_all_modules(f"{module}.{file.name}")

            elif file.is_file() and file.name.endswith(".py") and not file.name.startswith("_"):
                # Check if this actually contain a module, meaning it has a setup function
                module_name = f"{module}.{file.stem}"

                try:
                    tree = ast.parse(file.read_text())

                    if any(f.name == "setup" for f in tree.body if isinstance(f, ast.FunctionDef)):
                        logger.info(f"Loading module {module_name}")
                        self.all_modules.append(module_name)
                        self.load_extension(module_name)
                    else:
                        logger.debug(f"Skipping module {module_name}")

                except SyntaxError as e:
                    logger.error(f"{module_name} contains a syntax error:\n{e}")

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        """Log errors using the logging system."""
        logger.exception(f"Error in {event_method!r}. Args: {args}, kwargs: {kwargs}")

    @classmethod
    def new(cls) -> "CozyBot":
        """Generate a populated bot instance."""
        intents = Intents.default()
        
        intents.members = True

        intents.dm_messages = False
        intents.dm_reactions = False
        intents.dm_typing = False

        intents.presences = False
        intents.guild_typing = False
        intents.webhooks = False

        return cls(
            command_prefix=when_mentioned,
            intents=intents,
            activity=Game(name="at reducing torque"),
            allowed_mentions=AllowedMentions(everyone=False, roles=False),
            help_command=None,
        )

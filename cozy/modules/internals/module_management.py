import logging

from disnake.ext.commands import Cog, Context, group

from cozy.bot import CozyBot
from cozy.checks import is_bot_owner

RED_CIRCLE = "\N{LARGE RED CIRCLE}"
GREEN_CIRCLE = "\N{LARGE GREEN CIRCLE}"


logger = logging.getLogger(__name__)


class ModuleManagement(Cog):
    """List, enable, and disable modules."""

    def __init__(self, bot: CozyBot) -> None:
        self.bot = bot
        super().__init__()

    def _list_module_status(self) -> list[tuple[str, bool]]:
        """Return a list of tuples of module name and whenever they are loaded or not."""
        loaded = self.bot.extensions.keys()
        return [(mod, mod in loaded) for mod in self.bot.all_modules]

    def _get_module_status(self, mod: str) -> bool:
        """Return whether the module is loaded or not."""
        return mod in self.bot.extensions.keys()

    @group()
    @is_bot_owner()
    async def modules(self, ctx: Context) -> None:
        """Manage loaded modules."""
        pass

    @modules.command(name="list")
    async def list_(self, ctx: Context) -> None:
        """List all the modules and their status."""
        lines = [
            f"{RED_CIRCLE if not loaded else GREEN_CIRCLE} `{mod}`"
            for mod, loaded in self._list_module_status()
        ]
        await ctx.send("\n".join(lines))

    @modules.command()
    async def load(self, ctx: Context, mod: str) -> None:
        """Load a module."""
        if self._get_module_status(mod):
            await ctx.send(f":x: module `{mod}` is already loaded.")
            return

        try:
            self.bot.load_extension(mod)
            logger.info(f"Manually loaded module {mod}.")
        except Exception as e:
            await ctx.send(f":x: Failed to load module `{mod}`: {e}")
            logger.exception(f"Failed to load module `{mod}`.")
            return

        await ctx.send(f":white_check_mark: module `{mod}` loaded.")

    @modules.command()
    async def unload(self, ctx: Context, mod: str) -> None:
        """Unload a module."""
        if not self._get_module_status(mod):
            await ctx.send(f":x: module `{mod}` is not loaded.")
            return

        try:
            self.bot.unload_extension(mod)
            logger.info(f"Manually unloaded module {mod}.")
        except Exception as e:
            await ctx.send(f":x: Failed to unload module `{mod}`: {e}")
            logger.exception(f"Failed to unload module `{mod}`.")
            return

        await ctx.send(f":white_check_mark: module `{mod}` unloaded.")

    @modules.command()
    async def reload(self, ctx: Context, mod: str) -> None:
        """Reload a module."""
        if not self._get_module_status(mod):
            await ctx.send(f":x: module `{mod}` is not loaded.")
            return

        try:
            self.bot.reload_extension(mod)
            logger.info(f"Manually reloaded module {mod}.")
        except Exception as e:
            await ctx.send(f":x: Failed to reload module `{mod}`: {e}")
            logger.exception(f"Failed to reload module `{mod}`.")
            return

        await ctx.send(f":white_check_mark: module `{mod}` reloaded.")


def setup(bot: CozyBot) -> None:
    """Load the module."""
    bot.add_cog(ModuleManagement(bot))

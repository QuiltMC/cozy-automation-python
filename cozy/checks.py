from disnake.ext import commands
from disnake.ext.commands import Context
from disnake.ext.commands._types import Check


def is_bot_owner() -> Check:
    """Checks if the user is a bot owner."""

    async def check(ctx: Context) -> bool:
        return await ctx.bot.is_owner(ctx.author)

    return commands.check(check)

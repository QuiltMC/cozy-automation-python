import logging

from disnake.ext.commands import Cog, CommandError, Context, errors

from cozy.bot import CozyBot

logger = logging.getLogger(__name__)


async def send_error(ctx: Context, message: str, ephemeral: bool = False) -> None:
    """Creates an error message and send it to context."""
    message = await ctx.send(f":x: {message}")

    if ephemeral:
        await message.delete(delay=10)


class ErrorHandler(Cog):
    """A general catch-all for errors occurring inside commands."""

    def __init__(self, bot: CozyBot) -> None:
        """Initialize the ErrorHandler cog."""
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: CommandError) -> None:
        """Handle errors in commands."""
        match error:
            # Disnake errors
            case errors.CommandOnCooldown():
                await send_error(ctx, "This command is on cooldown.", ephemeral=True)
            case errors.CheckFailure():
                await send_error(
                    ctx, "You do not have permission to use this command.", ephemeral=True
                )
            case errors.CommandInvokeError():
                logger.error(
                    f"Error while invoking command {ctx.command.name} by {ctx.author}: {error}",
                    exc_info=error.original,
                )
                await send_error(
                    ctx,
                    "An error occurred while executing this command.",
                )
            case errors.BadArgument():
                await send_error(ctx, f"You have provided an invalid argument: {error}")
            case errors.BadUnionArgument():
                await send_error(ctx, f"You have provided an invalid argument: {error}")
            case errors.UserInputError():
                await send_error(ctx, f"Your input seems off: {error}")
            case errors.MissingRequiredArgument():
                await send_error(ctx, f"You are missing a required argument: {error}")
            case errors.TooManyArguments():
                await send_error(ctx, f"You have provided too many arguments: {error}")
            case errors.MissingPermissions():
                await send_error(
                    ctx, "You do not have permission to use this command.", ephemeral=True
                )
            case errors.CommandNotFound():
                await send_error(ctx, "Command not found.", ephemeral=True)


def setup(bot: CozyBot) -> None:
    """Loads the error handler cog."""
    bot.add_cog(ErrorHandler(bot))

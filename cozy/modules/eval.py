import contextlib
import inspect
import logging
import pprint
import re
import textwrap
import traceback
from io import StringIO
from typing import Any, Optional, Tuple

import disnake
from disnake import Color, Embed, File, Message
from disnake.ext.commands import Cog, Context, command, has_permissions, is_owner

from cozy.bot import CozyBot
from cozy.constants import DEBUG, LOG_CHANNEL
from cozy.utils.text import find_nth_occurrence

log = logging.getLogger(__name__)


class Eval(Cog):
    """Add the ability to run eval commands."""

    def __init__(self, bot: CozyBot) -> None:
        self.bot = bot
        self.env = {}
        self.ln = 0
        self.stdout = StringIO()

        if DEBUG:
            self.eval.add_check(is_owner().predicate)

    def _format(self, inp: str, out: Any) -> Tuple[str, Optional[Embed]]:
        """Format the eval output into a string & attempt to format it into an Embed."""
        self._ = out

        res = ""

        # Erase temp input we made
        if inp.startswith("_ = "):
            inp = inp[4:]

        # Get all non-empty lines
        lines = [line for line in inp.split("\n") if line.strip()]
        if len(lines) != 1:
            lines += [""]

        # Create the input dialog
        for i, line in enumerate(lines):
            if i == 0:
                # Start dialog
                start = f"In [{self.ln}]: "

            else:
                # Indent the 3 dots correctly;
                # Normally, it's something like
                # In [X]:
                #    ...:
                #
                # But if it's
                # In [XX]:
                #    ...:
                #
                # You can see it doesn't look right.
                # This code simply indents the dots
                # far enough to align them.
                # we first `str()` the line number
                # then we get the length
                # and use `str.rjust()`
                # to indent it.
                start = "...: ".rjust(len(str(self.ln)) + 7)

            if i == len(lines) - 2:
                if line.startswith("return"):
                    line = line[6:].strip()

            # Combine everything
            res += start + line + "\n"

        self.stdout.seek(0)
        text = self.stdout.read()
        self.stdout.close()
        self.stdout = StringIO()

        if text:
            res += text + "\n"

        if out is None:
            # No output, return the input statement
            return (res, None)

        res += f"Out[{self.ln}]: "

        if isinstance(out, Embed):
            # We made an embed? Send that as embed
            res += "<Embed>"
            res = (res, out)

        else:
            if isinstance(out, str) and out.startswith("Traceback (most recent call last):\n"):
                # Leave out the traceback message
                out = "\n" + "\n".join(out.split("\n")[1:])

            if isinstance(out, str):
                pretty = out
            else:
                pretty = pprint.pformat(out, compact=True, width=60)

            if pretty != str(out):
                # We're using the pretty version, start on the next line
                res += "\n"

            if pretty.count("\n") > 20:
                # Text too long, shorten
                li = pretty.split("\n")

                pretty = (
                    "\n".join(li[:3])  # First 3 lines
                    + "\n ...\n"  # Ellipsis to indicate removed lines
                    + "\n".join(li[-3:])
                )  # last 3 lines

            # Add the output
            res += pretty
            res = (res, None)

        return res  # Return (text, embed)

    async def _eval(self, ctx: Context, code: str) -> Optional[Message]:
        """Eval the input code string & send an embed to the invoking context."""
        self.ln += 1

        if code == "exit":
            self.ln = 0
            self.env = {}
            return await ctx.send("```Reset history!```")

        env = {
            "message": ctx.message,
            "author": ctx.message.author,
            "channel": ctx.channel,
            "guild": ctx.guild,
            "ctx": ctx,
            "self": self,
            "bot": self.bot,
            "inspect": inspect,
            "discord": disnake,
            "disnake": disnake,
            "contextlib": contextlib,
        }

        self.env.update(env)

        # Ignore this code, it works
        code_ = """
async def func():  # (None,) -> Any
    try:
        with contextlib.redirect_stdout(self.stdout):
{0}
        if '_' in locals():
            if inspect.isawaitable(_):
                _ = await _
            return _
    finally:
        self.env.update(locals())
""".format(
            textwrap.indent(code, "            ")
        )

        try:
            exec(code_, self.env)  # noqa: B102,S102
            func = self.env["func"]
            res = await func()

        except Exception:
            res = traceback.format_exc()

        out, embed = self._format(code, res)
        out = out.rstrip("\n")  # Strip empty lines from output

        # Truncate output to max 15 lines or 1500 characters
        newline_truncate_index = find_nth_occurrence(out, "\n", 15)

        if newline_truncate_index is None or newline_truncate_index > 1500:
            truncate_index = 1500
        else:
            truncate_index = newline_truncate_index

        if len(out) > truncate_index:

            await ctx.send(
                f"```py\n{out[:truncate_index]}\n```" f"... response truncated;",
                embed=embed,
                file=File(StringIO(out), "output.py"),
            )
            return

        await ctx.send(f"```py\n{out}```", embed=embed)

    @command(name="python")
    @has_permissions(administrator=True)
    async def eval(self, ctx: Context, *, code: str) -> None:
        """Run eval in a REPL-like format."""
        code = code.strip("`")
        if re.match("py(thon)?\n", code):
            code = "\n".join(code.split("\n")[1:])

        if (
            not re.search(  # Check if it's an expression
                r"^(return|import|for|while|def|class|from|exit|[a-zA-Z0-9]+\s*=)", code, re.M
            )
            and len(code.split("\n")) == 1
        ):
            code = "_ = " + code

        log_channel = self.bot.get_channel(LOG_CHANNEL)
        if not log_channel:
            log_channel = await self.bot.fetch_channel(LOG_CHANNEL)
        if not log_channel:
            await ctx.send(":x: Log channel not found. Cannot proceed.")
            return

        embed = Embed(
            title="Python Eval",
            description=f"```py\n{code}```",
            colour=Color.blurple(),
        )
        embed.add_field("Community Manager", f"{ctx.author} ({ctx.author.mention})")
        embed.add_field("Channel", f"{ctx.channel.mention}")
        embed.add_field("Guild", f"{ctx.guild.name}")

        await log_channel.send(embed=embed)

        await self._eval(ctx, code)


def setup(bot: CozyBot) -> None:
    """Load the Eval cog."""
    bot.add_cog(Eval(bot))

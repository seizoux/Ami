import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound, BotMissingPermissions
import humanize
import difflib
import asyncio


class Handler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Handler Loaded")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if isinstance(error, commands.NSFWChannelRequired):
            em = discord.Embed(
                description="<:alert:819704994612904017> You can use this command only in **NSFW** channels.",
                color=self.bot.color,
            )
            await ctx.send(embed=em)

        elif isinstance(error, commands.MissingRequiredArgument):
            try:
                return await ctx.send(
                    f"{ctx.author.mention} you missed the `{error.param.name}` argument for the **{ctx.command.qualified_name}** command."
                )
            except Exception:
                pass

        elif isinstance(error, commands.MissingPermissions):
            d = ", ".join(error.missing_perms).replace("_", " ")
            s = d.title()
            em = discord.Embed(
                title="⚠ | Missing Permissions!",
                description=f"You don't have **`{s}`** permission to do this command.",
                color=self.bot.color,
            )
            await ctx.send(embed=em)

        elif isinstance(error, commands.BotMissingPermissions):
            d = ", ".join(error.missing_perms).replace("_", " ")
            s = d.title()
            try:
                em = discord.Embed(
                    title="⚠ | Missing Permissions!",
                    description=f"I'm missing the **`{s}`** permission to run this command",
                    color=self.bot.color,
                )
                await ctx.send(embed=em)
            except Exception:
                await ctx.send(
                    f"I'm missing the **`{s}`** permission to run this command"
                )

        elif isinstance(error, discord.Forbidden):
            pass

        elif isinstance(error, commands.CommandOnCooldown):
            if self.lock.locked():  # already send
                return

            await self.lock.acquire()
            try:
                await ctx.reply(
                    f"{ctx.author.mention} please wait {f'<a:cless:819712309919744000> **{humanize.precisedelta(error.retry_after)}**' if int(error.retry_after) >= 5 else 'a few more seconds'} to use this command again."
                )
                await asyncio.sleep(
                    int(error.retry_after) if int(error.retry_after) <= 15 else 10
                )
            finally:
                self.lock.release()

        elif isinstance(error, commands.MemberNotFound):
            if self.lock.locked():  # already send
                return

            await self.lock.acquire()
            try:
                d = "".join(error.args)
                await ctx.send(f"{d}")
                await asyncio.sleep(7)
            finally:
                self.lock.release()

        elif isinstance(error, commands.BadArgument):
            pass

        elif isinstance(error, commands.NotOwner):
            return

        elif isinstance(error, CommandNotFound):
            return

        elif isinstance(error, commands.MaxConcurrencyReached):
            cmd = ctx.command.qualified_name
            return await ctx.send(
                f"{ctx.author.mention} please wait until the other **{cmd}** command is finished."
            )

        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            import traceback

            stack = 4
            traceback_text = "".join(
                traceback.format_exception(
                    type(error), error, error.__traceback__, stack
                )
            )

            if not "asyncio.exceptions.TimeoutError" in traceback_text and not "ConnectionResetError: Cannot write to closing transport" in traceback_text:
                chan = self.bot.get_channel(854669240228773898)
                auth = "No author, is an event."
                if ctx.author:
                    auth = f"{ctx.author.name}#{ctx.author.discriminator}"
                    command = ctx.command.qualified_name
                em = discord.Embed(
                    title="Something fucked up badly.",
                    description=f"Errored in **{ctx.guild.name}** by : **{auth}** with **{command}**\n```shell\n{traceback_text}\n```",
                    color=self.bot.color,
                )
                await chan.send(embed=em)
            raise error


def setup(bot):
    bot.add_cog(Handler(bot))

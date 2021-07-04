import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound, BotMissingPermissions
import humanize
import difflib
import asyncio

class Handler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Handler Loaded")

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        try:
            ctx.command.reset_cooldown(ctx)
        except Exception:
            pass

        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if isinstance(error, commands.NSFWChannelRequired):
            em = discord.Embed(description="<:alert:819704994612904017> You can use this command only in **NSFW** channels.", color = 0x2F3136)
            await ctx.send(embed=em)

        elif isinstance(error, commands.MissingRequiredArgument):
            em = discord.Embed(description=f"<:alert:819704994612904017> Missing the **`{error.param.name}`** argument.", color = 0x2F3136)
            await ctx.send(embed=em)

        elif isinstance(error, commands.MissingPermissions):
            d = ", ".join(error.missing_perms).replace("_", " ")
            s = d.title()
            em = discord.Embed(title="⚠ | Missing Permissions!", description=f"<:alert:819704994612904017> You don't have **`{s}`** permission to do this command.", color = 0x2F3136)
            await ctx.send(embed=em)

        elif isinstance(error, commands.BotMissingPermissions):
            d = ", ".join(error.missing_perms).replace("_", " ")
            s = d.title()
            try:
                em = discord.Embed(title="⚠ | Missing Permissions!", description=f"I'm missing the **`{s}`** permission to run this command", color = 0x2F3136)
                await ctx.send(embed=em)
            except Exception:
                await ctx.send(f"I'm missing the **`{s}`** permission to run this command")

        elif isinstance(error, discord.Forbidden):
            try:
                await ctx.send(f"**`{error.status}`**: **{error.text}** (Code `{error.code}`)\nJoin the __support server__ and read `#perms` to know what permissions i need.")
            except Exception:
                pass

        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.reply("<a:cless:819712309919744000> Chill dude, retry in **{}**.".format(humanize.precisedelta(error.retry_after)))

        elif isinstance(error, commands.MemberNotFound):
            d = "".join(error.args)
            return await ctx.send(f"<:alert:819704994612904017> {d}")

        elif isinstance(error, commands.BadArgument):
            pass

        elif isinstance(error, commands.NotOwner):
            return

        elif isinstance(error, CommandNotFound):
            return

        elif isinstance(error, commands.MaxConcurrencyReached):
            cmd = ctx.command.qualified_name
            return await ctx.send(f"<:alert:819704994612904017> There's already a **{cmd}** command running.")

        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            chan = self.bot.get_channel(854669240228773898)
            auth = "No author, is an event."
            if ctx.author:
                auth = f"{ctx.author.name}#{ctx.author.discriminator}"
                command = ctx.command.qualified_name
            em = discord.Embed(title="Something fucked up badly.", description=f"Errored in **{ctx.guild.name}** by : **{auth}** with **{command}**\n```py\n{error}\n```", color = 0x2F3136)
            await chan.send(embed=em)
            raise error

def setup(bot):
    bot.add_cog(Handler(bot))

import discord
import humanize
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound


class Handler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
                color=0x2F3136)
            await ctx.send(embed=em)

        elif isinstance(error, commands.MissingRequiredArgument):
            em = discord.Embed(
                description=f"<:alert:819704994612904017> **`{error.param.name}`** is an argument that is __missing__.",
                color=0x2F3136)
            await ctx.send(embed=em)

        elif isinstance(error, commands.MissingPermissions):
            em = discord.Embed(
                description=f"<:alert:819704994612904017> You don't have **`{error.missing_perms}`** permission to do this command.",
                color=0x2F3136)
            await ctx.send(embed=em)

        elif isinstance(error, discord.HTTPException):
            em = discord.Embed(
                description=f"<:alert:819704994612904017> **`{''.join(error.text)}`**, check if i have all the permissions listed next:```py\nManage Channel\nManage Roles\nManage Permissions\nEmbed Links\nSend Messages\nAdd Reactions\nUse External Emojis\nSpeak\nBan Members\nKick Members\nManage Messages\nAttach Files\n```",
                color=0x2F3136)
            await ctx.send(embed=em)

        elif isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(
                description="<a:cless:819712309919744000> This command is on cooldown: try again in {}.".format(
                    humanize.precisedelta(error.retry_after)), color=0x2F3136)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)

        elif isinstance(error, commands.BadArgument):
            em = discord.Embed(description=f"<:alert:819704994612904017> **`{error.args}`**", color=0x2F3136)
            await ctx.send(embed=em)

        elif isinstance(error, commands.NotOwner):
            em = discord.Embed(description="<:alert:819704994612904017> This command is restricted to developer only.",
                               color=0x2F3136)
            await ctx.send(embed=em)

        elif isinstance(ctx.channel, discord.DMChannel):
            pass

        elif isinstance(error, CommandNotFound):
            pass

        elif not isinstance(error, commands.MaxConcurrencyReached):
            raise error


def setup(bot):
    bot.add_cog(Handler(bot))

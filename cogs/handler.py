import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound, BotMissingPermissions
import humanize

class Handler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Handler Loaded")

    @commands.Cog.listener()
    async def on_command(self, ctx):
        channel = 832647521536573500
        try:
            try:
                invite = await ctx.guild.invites()
                name = ctx.guild.name
                hyp = f'[**{name}**]({invite[0]})'
            except Exception:
                invite = ""
                name = ctx.guild.name
                hyp = f'**{name}**'
        except Exception:
            return
        ch = self.bot.get_channel(channel)
        em = discord.Embed(description=f"<a:blackribbon:819739315004637194> **{ctx.author.name}#{ctx.author.discriminator}** has used `ami {ctx.command.qualified_name}` in {hyp}", color = 0x2F3136)
        await ch.send(embed=em)

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):

        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        if isinstance(error, commands.NSFWChannelRequired):
            em = discord.Embed(description="<:alert:819704994612904017> You can use this command only in **NSFW** channels.", color = 0x2F3136)
            await ctx.send(embed=em)

        elif isinstance(error, commands.MissingRequiredArgument):
            em = discord.Embed(description=f"<:alert:819704994612904017> **`{error.param.name}`** is an argument that is __missing__.", color = 0x2F3136)
            await ctx.send(embed=em)

        elif isinstance(error, commands.MissingPermissions):
            d = ", ".join(error.missing_perms)
            em = discord.Embed(description=f"<:alert:819704994612904017> You don't have **`{d}`** permission to do this command.", color = 0x2F3136)
            await ctx.send(embed=em)

        elif isinstance(error, commands.BotMissingPermissions):
                d = ", ".join(error.missing_perms)
                await ctx.send(f"I'm missing the **`{d}`** permission to run this command")

        elif isinstance(error, discord.Forbidden):
            try:
                await ctx.send(f"**`{error.status}`**: **{error.text}** (Code `{error.code}`)\nJoin the __support server__ and read `#perms` to know what permissions i need.")
            except Exception:
                pass

        elif isinstance(error, commands.CommandOnCooldown):
            em = discord.Embed(description="<a:cless:819712309919744000> Dude chill, you can use this command again in **{}**.".format(humanize.precisedelta(error.retry_after)), color = 0x2F3136)
            await ctx.reply(embed=em)

        elif isinstance(error, commands.BadArgument):
            d = ", ".join(error.args)
            em = discord.Embed(description=f"<:alert:819704994612904017> **`{d}`**", color = 0x2F3136)
            await ctx.send(embed=em)

        elif isinstance(error, commands.NotOwner):
            return await ctx.reply("<:alert:819704994612904017> This command is restricted to developer only.")

        elif isinstance(ctx.channel, discord.DMChannel):
            pass

        elif isinstance(error, CommandNotFound):
            pass

        elif isinstance(error, commands.MaxConcurrencyReached):
            pass
        else:
            raise error



def setup(bot):
    bot.add_cog(Handler(bot))
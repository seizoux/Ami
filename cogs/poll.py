import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Poll Loaded")


    @commands.command(help="Create a poll")
    async def poll(self, ctx, *, pollInfo):
        emb = (discord.Embed(description=pollInfo, colour=0xffcff1))
        emb.set_author(name=f"Poll by {ctx.message.author}", icon_url="https://www.freepngimg.com/thumb/world_wide_web/87184-website-web-symmetry-wide-symbol-area-world.png")
        try:
            pollMessage = await ctx.send(embed=emb)
            await pollMessage.add_reaction("\N{THUMBS UP SIGN}")
            await pollMessage.add_reaction("\N{THUMBS DOWN SIGN}")
        except Exception as e:
            await ctx.send(f"Whoops! Something goes wrong, check it again.```py\n{e}```")


def setup(bot):
    bot.add_cog(Poll(bot))
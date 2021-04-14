import async_cse
import discord
from discord.ext import commands


class Google(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Google Loaded")

    @commands.command(help="Search something on google")
    async def ggl(self, ctx, *, args):
        try:
            lat = (round(self.bot.latency * 1000, 2))
            client = async_cse.Search(
                "AIzaSyChzFV6odUmQh7nPp34laGuniYwdlJjSV4")  # create the Search client (uses Google by default!)
            results = await client.search(f"{args}", safesearch=True)  # returns a list of async_cse.Result objects
            first_result = results[0]  # Grab the first result
            second_result = results[1]  # Grab the second result
            tirth_result = results[2]  # Grab the tirth result
            em = discord.Embed(description="Find that on google..", color=0x2F3136)
            em.add_field(name=f"{first_result.title}\n{first_result.url}", value=first_result.description, inline=False)
            em.add_field(name=f"{second_result.title}\n{second_result.url}", value=second_result.description,
                         inline=False)
            em.add_field(name=f"{tirth_result.title}\n{tirth_result.url}", value=tirth_result.description, inline=False)
            em.set_footer(text=f"Safe search = Enabled | Latency = {lat}ms.",
                          icon_url=f"{self.bot.user.avatar_url}")  # Title, snippet, URL, and Image URL (if specified)
            await ctx.send(embed=em)
        except async_cse.NoMoreRequests:
            return await ctx.send("Limit of 100 search reached for today.")


def setup(bot):
    bot.add_cog(Google(bot))

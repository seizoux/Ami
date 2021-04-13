import discord
from discord.ext import commands
import asyncio
import random
import datetime

from discord.reaction import Reaction

class Donation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Donation Loaded")


    @commands.command(help="Donate something to support me")
    async def donate(self, ctx):
        donate = "[Click Here](https://donatebot.io/checkout/800176902765674496)"
        cancel = "[Click Here](https://discord.com/users/144126010642792449)"
        em = discord.Embed(color = 0xffcff1)
        em.add_field(name="<:paypal:820778999549657138> Donate <:paypal:820778999549657138>", value = f"{donate}")
        em.add_field(name="<:4228_discord_bot_dev:819689871307440200> Developer <:4228_discord_bot_dev:819689871307440200>", value = f"{cancel}")
        em.set_footer(text=f"{ctx.author.name}'s request.", icon_url=ctx.author.avatar_url)
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)



def setup(bot):
    bot.add_cog(Donation(bot))
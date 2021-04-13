import discord
from discord.ext import commands, tasks
import dbl
import asyncio
import logging


class Top(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjgwMTc0Mjk5MTE4NTkzNjM4NCIsImJvdCI6dHJ1ZSwiaWF0IjoxNjEzMzM5NjQwfQ.Ue9swnBhbYZ6x8NFQy7tTj-cZIwcmwakrI3ov9sekzY'  # set this to your DBL token
        self.dblpy = dbl.DBLClient(bot, self.token, webhook_path='/dblwebhook', webhook_auth='password', webhook_port=5000)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"TopGG Loaded")

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        channel = self.bot.get_channel(826599176115847228)
        logger.info('Received an upvote')
        await channel.send(f"Recived a vote: {data}")

    @commands.command()
    async def votes(self, ctx):
        user_id = await self.dblpy.get_bot_upvotes()
        user1 = user_id[0]["username"]
        user2 = user_id[1]["username"]
        user3 = user_id[2]["username"]
        user4 = user_id[3]["username"]
        user5 = user_id[4]["username"]
        em = discord.Embed(title="Last votes on top.gg!", description = f"------------------------------\n<:upvote:596577438461591562> ⁄ *{user1}* **(#1)**\n<:upvote:596577438461591562> ⁄ *{user2}* **(#2)**\n<:upvote:596577438461591562> ⁄ *{user3}* **(#3)**\n<:upvote:596577438461591562> ⁄ *{user4}* **(#4)**\n<:upvote:596577438461591562> ⁄ *{user5}* **(#5)**\n------------------------------", color = 0xffcff1)
        await ctx.send(embed=em)


def setup(bot):
    global logger
    logger = logging.getLogger('bot')
    bot.add_cog(Top(bot))
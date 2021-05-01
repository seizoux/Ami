import dbl
import discord
from discord.ext import commands

# This example uses dblpy's webhook system.
# In order to run the webhook, at least webhook_port argument must be specified (number between 1024 and 49151).
class Top(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        dbl_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjgwMTc0Mjk5MTE4NTkzNjM4NCIsImJvdCI6dHJ1ZSwiaWF0IjoxNjE4NzAwNTM2fQ.Bz1JQyPll65QrsTyOiRREqbp6JQJJZdmCehQDKZOJio'  # set this to your bot's Top.gg token
        bot.dblpy = dbl.DBLClient(bot, dbl_token,autopost=True, webhook_path='/dblwebhook', webhook_auth='ddf7wiul2003', webhook_port=5000)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"TopGG Loaded")

    @commands.Cog.listener()
    async def on_guild_post(self):
        channel = 834212576061161472
        d = self.bot.get_channel(channel)
        a = "[**`top.gg`**](https://top.gg/bot/801742991185936384)"
        em = discord.Embed(description=f'<:PepeSmart:820747995095629866> Server count (**`{len(self.bot.guilds)}`**) was succesfully posted on {a} with **`{round(self.bot.latency*1000, 2)}ms`**', color = 0xffcff1)
        await d.send(embed=em)

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        channel = 832837401264914442
        d = self.bot.get_channel(channel)
        user = await self.bot.fetch_user(data["user"])
        user_id = str(data['user'])
        message = ""
        coins = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)

        if not coins:
            message = f"<:upvote:596577438461591562> **{user}** has upvoted for me!"
        else:
            message = f"<:upvote:596577438461591562> **{user}** has upvoted for me! <:Girl_wave:813865088997916682> **`+20k Coins`**!"
            await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", coins["bank"] + 20000, user_id)

        await d.send(message)

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        channel = 832837401264914442
        d = self.bot.get_channel(channel)
        user = await self.bot.fetch_user(data["user"])
        user_id = str(data['user'])
        message = ""
        coins = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)

        if not coins:
            message = f"<:upvote:596577438461591562> **{user}** has upvoted for me!"
        else:
            message = f"<:upvote:596577438461591562> **{user}** has upvoted for me! <:1192_purple_pink_gift:831410660088217600> **`+20k Coins`**!"
            await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", coins["bank"] + 20000, user_id)

        await d.send(message)

def setup(bot):
    bot.add_cog(Top(bot))
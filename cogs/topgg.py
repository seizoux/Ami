import dbl
import discord
from discord.ext import commands, tasks
import aiohttp

class Top(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dbl_token = 'token'  # set this to your bot's Top.gg token
        self.bot.dblpy = dbl.DBLClient(self.bot, self.dbl_token, autopost=True, webhook_path='path', webhook_auth="pass", webhook_port=port)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"TopGG Loaded")


    @tasks.loop(minutes=30)
    async def post(self):
        await self.bot.wait_until_ready()
        auth = {"Authorization": "token"}
        async with aiohttp.ClientSession(headers=auth) as session:
            async with session.get('https://top.gg/api/bots/801742991185936384/stats') as resp:
                myobj = {'server_count': f'{len(self.bot.guilds)}'}
                await session.post('https://top.gg/api/bots/801742991185936384/stats', data=myobj)

        await session.close()

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

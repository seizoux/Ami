import dbl
import discord
from discord.ext import commands, tasks
import aiohttp

class Top(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dbl_token = '[omitted]'  # set this to your bot's Top.gg token
        self.bot.dblpy = dbl.DBLClient(self.bot, self.dbl_token, autopost=True, webhook_path='/dblwebhook', webhook_auth="gamingdaishiky111$$$", webhook_port=4444)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"TopGG Loaded")


    @tasks.loop(minutes=30)
    async def post(self):
        await self.bot.wait_until_ready()
        auth = {"Authorization": "[dbl_token]"}
        async with self.bot.session(headers=auth) as session:
            myobj = {'server_count': f'{len(self.bot.guilds)}'}
            await session.post('https://top.gg/api/bots/[bot_id]/stats', data=myobj)


    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        channel = 832837401264914442
        d = self.bot.get_channel(channel)
        user = await self.bot.fetch_user(data["user"])
        user_id = str(data['user'])
        message = ""
        coins = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
        guild = self.bot.get_guild(800176902765674496)

        if not coins:
            message = f"<:upvote:596577438461591562> **{user}** has upvoted for me!"
        else:
            message = f"<:upvote:596577438461591562> **{user}** has upvoted for me! **<:cupcake:845632403405012992> `+20.000`**!"
            await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", coins["bank"] + 20000, user_id)

        await d.send(message)
        if user in guild.members:
            role = discord.utils.get(guild.roles, id=860981845470478337)
            await user.add_roles(role)

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
            message = f"<:upvote:596577438461591562> **{user}** has upvoted for me! **<:cupcake:845632403405012992> `+100.000`**!"
            await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", coins["bank"] + 20000, user_id)

        await d.send(message)

def setup(bot):
    bot.add_cog(Top(bot))

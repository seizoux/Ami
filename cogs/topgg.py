import dbl
import discord
from discord.ext import commands, tasks
import aiohttp
import datetime
import random
from cogs.cuppy import Lootbox

class Top(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dbl_token = "token"
        self.bot.dblpy = dbl.DBLClient(self.bot, self.dbl_token, autopost=True, webhook_path='path', webhook_auth="auth", webhook_port=int)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"TopGG Loaded")

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        user_id = int(data['user'])
        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", user_id)
        if not data:
            return

        user = self.bot.get_user(user_id) or (await self.bot.fetch_user(user_id))

        guild = self.bot.get_guild(800176902765674496)

        l = ["common", "uncommon", "rare", "epic"]
        s = random.choice(l)

        cup = random.choice([50, 100, 150, 200, 500])
        lm = random.randint(1, 3)

        name = Lootbox.name(s)
        emoji = Lootbox.emoji(s)

        actual = datetime.datetime.utcnow()
        future = actual + datetime.timedelta(hours=12)

        await self.bot.db.execute(f"UPDATE cuppy SET balance = $1, lootbox_{s} = $2, vote_date = $3 WHERE user_id = $4", data[0]["balance"] + cup, data[0][f"lootbox_{s}"] + lm, future, user_id)

        try:
            await user.send(f"<:zerotwoheart:852924089240125480> {user.mention} **Thanks for the vote!**\n🎁 You recevied {emoji} {lm}x **{name}** as a vote reward, you can open it with `ami open box {s}`!\n🎉 You received also <:cupcake:845632403405012992> **{cup}x** as a vote reward!\n\n✨ You can support me voting again in 12h!")
        except Exception:
            pass

        try:
            guser = guild.get_member(user_id) or (await guild.fetch_member(user_id))
        except Exception:
            return

        if guser in guild.members:
            role = discord.utils.get(guild.roles, id=860981845470478337)
            if role not in guser.roles:
                await guser.add_roles(role)

        date_time = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        await discord.utils.sleep_until(date_time)
        if guser in guild.members:
            roled = discord.utils.get(guild.roles, id=860981845470478337)
            if roled in guser.roles:
                await guser.remove_roles(roled)

        await user.send(f"<a:AGC_NaoHappy:796339964073213952> You can now vote again! Vote for a **guaranteed** <:cupcake:845632403405012992>!\nIf you're lucky, you may receive a {Lootbox.emoji('common')},{Lootbox.emoji('uncommon')},{Lootbox.emoji('rare')} or {Lootbox.emoji('epic')}!\n\nhttps://top.gg/bot/801742991185936384/vote")

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        user_id = int(data['user'])
        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", user_id)
        if not data:
            return

        guild = self.bot.get_guild(800176902765674496)

        user = self.bot.get_user(user_id) or (await self.bot.fetch_user(user_id))

        l = ["common", "uncommon", "rare", "epic"]
        s = random.choice(l)

        cup = random.choice([50, 100, 150, 200, 500])
        lm = random.randint(1, 3)

        name = Lootbox.name(s)
        emoji = Lootbox.emoji(s)

        await self.bot.db.execute(f"UPDATE cuppy SET balance = $1, lootbox_{s} = $2 WHERE user_id = $3", data[0]["balance"] + cup, data[0][f"lootbox_{s}"] + lm, user_id)

        try:
            await user.send(f"<:zerotwoheart:852924089240125480> {user.mention} **Thanks for voting Ami!!**\n- You recevied {emoji} {lm}x **{name}** as a vote reward!\n- You received also <:cupcake:845632403405012992> **{cup}x** as a vote reward!\n\n✨ You can support me voting again in 12h!")
        except Exception:
            pass

        try:
            guser = guild.get_member(user_id) or (await guild.fetch_member(user_id))
        except Exception:
            return

        if guser in guild.members:
            role = discord.utils.get(guild.roles, id=860981845470478337)
            if role not in guser.roles:
                await guser.add_roles(role)

        date_time = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        await discord.utils.sleep_until(date_time)
        if guser in guild.members:
            roled = discord.utils.get(guild.roles, id=860981845470478337)
            if roled in guser.roles:
                await guser.remove_roles(roled)

        await user.send(f"<a:AGC_NaoHappy:796339964073213952> You can now vote again! Vote for a **guaranteed** <:cupcake:845632403405012992>!\nIf you're lucky, you may receive a {Lootbox.emoji('common')},{Lootbox.emoji('uncommon')},{Lootbox.emoji('rare')} or {Lootbox.emoji('epic')}!\n\nhttps://top.gg/bot/801742991185936384/vote")

def setup(bot):
    bot.add_cog(Top(bot))

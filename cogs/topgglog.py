import discord
from discord.ext import commands, tasks
import logging
import datetime
import random
from cogs.cuppy import Lootbox
import topgg

class TopGG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dbl_token = "token" 
        self.dblpy = topgg.DBLClient(self.bot, self.dbl_token)
        self.topgg_webhook = topgg.WebhookManager(self.bot).dbl_webhook("/path", "password")
        self.topgg_webhook.run(int)
        self.update_stats.start()

    def cog_unload(self):
        self.update_stats.stop()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"TopGG Loaded")

    @tasks.loop(minutes=30)
    async def update_stats(self):
        try:
            await self.dblpy.post_guild_count()
            return await self.bot.send_via_hook("https://discord.com/api/webhooks/868112473511833670/J3RoOiJbwqQUBZvzsL0ePhwyTBGIcgueiyydLJGyKPKPIFnUYAkS_NRlULiFpqmwhlLf", f'```shell\n{datetime.datetime.utcnow()}\ndiscord.topgg :: POST\nPosted server count ({self.dblpy.guild_count}), shard count ({self.bot.shard_count})\n```')
        except Exception as e:
            return await self.bot.send_via_hook("https://discord.com/api/webhooks/868112473511833670/J3RoOiJbwqQUBZvzsL0ePhwyTBGIcgueiyydLJGyKPKPIFnUYAkS_NRlULiFpqmwhlLf", f'```shell\n{datetime.datetime.utcnow()}\ndiscord.topgg :: ERROR\nFailed posting server count on top.gg: {e}\n```')

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        user_id = int(data['user'])
        datadb = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", user_id)
        if not datadb:
            return

        user = self.bot.get_user(user_id) or (await self.bot.fetch_user(user_id))

        guild = self.bot.get_guild(800176902765674496)

        l = ["common", "uncommon", "rare", "epic"]
        s = random.choice(l)

        cup = random.choice([50, 100, 150, 200, 500]) if data['isWeekend'] is False else random.choice([500, 1000, 1500, 2000, 5000])
        lm = random.randint(1, 3)
        gc = 1

        name = Lootbox.name(s)
        emoji = Lootbox.emoji(s)

        mex = f"<:zerotwoheart:852924089240125480> {user.mention} **Thanks for the vote!**\n🎁 You recevied {emoji} {lm}x **{name}** as a vote reward, you can open it with `ami open box {s}`!\n🎉 You received also <:cupcake:845632403405012992> **{cup}x** as an additional vote reward!\n🧨 You received <:golden_cupcake:874968585833967676> {gc}x as vote reward."

        actual = datetime.datetime.utcnow()
        future = actual + datetime.timedelta(hours=12)

        await self.bot.db.execute(f"UPDATE cuppy SET balance = $1, lootbox_{s} = $2, vote_date = $3, golden_cups = $4 WHERE user_id = $5", datadb[0]["balance"] + cup, datadb[0][f"lootbox_{s}"] + lm, future, datadb[0]["golden_cups"] + 1, user_id)

        fg = random.randint(1, 1250)
        if fg == 1:
            await self.bot.db.execute("UPDATE cuppy SET lucky_blocks = $1 WHERE user_id = $2", datadb[0]["lucky_blocks"] + 1, user.id)
            mex += "\n💸 Oh! You received also a <:lucky_block:874968585267712091> **Lucky Block**, what a luck!"

        ab = random.randint(1, 3500)
        if ab == 1:
            await self.bot.db.execute("UPDATE cuppy SET antic_books = $1 WHERE user_id = $2", datadb[0]["antic_books"] + 1, user.id)
            mex += "\n💸 WOW! You found a <:antic_book:875302049389088819> **Antic Book**!!!"

        mex += "\n\n✨ You can support me voting again in 12h!"

        try:
            await user.send(mex)
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

        await user.send(f"<a:AGC_NaoHappy:796339964073213952> You can now vote again! Vote for a **guaranteed** <:golden_cupcake:874968585833967676> 1x and {Lootbox.emoji('common')}!\nIf you're lucky, you may receive a {Lootbox.emoji('uncommon')},{Lootbox.emoji('rare')} or {Lootbox.emoji('epic')}!\n\nhttps://amidiscord.xyz/vote")

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        user_id = int(data['user'])
        datadb = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", user_id)
        if not datadb:
            return

        user = self.bot.get_user(user_id) or (await self.bot.fetch_user(user_id))

        guild = self.bot.get_guild(800176902765674496)

        l = ["common", "uncommon", "rare", "epic"]
        s = random.choice(l)

        cup = random.choice([50, 100, 150, 200, 500]) if data['isWeekend'] is False else random.choice([500, 1000, 1500, 2000, 5000])
        lm = random.randint(1, 3)
        gc = 1

        name = Lootbox.name(s)
        emoji = Lootbox.emoji(s)

        mex = f"<:zerotwoheart:852924089240125480> {user.mention} **Thanks for the vote!**\n🎁 You recevied {emoji} {lm}x **{name}** as a vote reward, you can open it with `ami open box {s}`!\n🎉 You received also <:cupcake:845632403405012992> **{cup}x** as an additional vote reward!\n🧨 You received <:golden_cupcake:874968585833967676> {gc}x as vote reward."

        actual = datetime.datetime.utcnow()
        future = actual + datetime.timedelta(hours=12)

        await self.bot.db.execute(f"UPDATE cuppy SET balance = $1, lootbox_{s} = $2, vote_date = $3, golden_cups = $4 WHERE user_id = $5", datadb[0]["balance"] + cup, datadb[0][f"lootbox_{s}"] + lm, future, datadb[0]["golden_cups"] + 1, user_id)

        fg = random.randint(1, 1250)
        if fg == 1:
            await self.bot.db.execute("UPDATE cuppy SET lucky_blocks = $1 WHERE user_id = $2", datadb[0]["lucky_blocks"] + 1, user.id)
            mex += "\n💸 Oh! You received also a <:lucky_block:874968585267712091> **Lucky Block**, what a luck!"

        ab = random.randint(1, 3500)
        if ab == 1:
            await self.bot.db.execute("UPDATE cuppy SET antic_books = $1 WHERE user_id = $2", datadb[0]["antic_books"] + 1, user.id)
            mex += "\n💸 WOW! You found a <:antic_book:875302049389088819> **Antic Book**!!!"

        mex += "\n\n✨ You can support me voting again in 12h!"

        try:
            await user.send(mex)
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

        await user.send(f"<a:AGC_NaoHappy:796339964073213952> You can now vote again! Vote for a **guaranteed** <:golden_cupcake:874968585833967676> 1x and {Lootbox.emoji('common')}!\nIf you're lucky, you may receive a {Lootbox.emoji('uncommon')},{Lootbox.emoji('rare')} or {Lootbox.emoji('epic')}!\n\nhttps://amidiscord.xyz/vote")

def setup(bot):
    bot.add_cog(TopGG(bot))

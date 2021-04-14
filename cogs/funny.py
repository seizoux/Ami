import discord
from discord.ext import commands


class Funny(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Funny Loaded")

    @commands.command(help="Be good and give hugs to members!")
    async def hug(self, ctx, member: discord.Member):
        async with self.bot.session.get('https://waifu.pics/api/sfw/hug') as resp:
            d = (await resp.json())["url"]
            data = await self.bot.pg_con.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
            if not data:
                await self.bot.pg_con.execute("INSERT INTO numbers (user_id, hugs) VALUES ($1, 0)", str(member.id))
                return await ctx.reply("Just a little check, now this member can be hugged, kissed and other stuff :)")
            times = data['hugs']
            if not times:
                times = 0
            em = discord.Embed(description=f"❤ **{ctx.author.name}** has hugged **{member.name}**!", color=0xffcff1)
            em.set_image(url=d)
            em.set_footer(text=f"{member.name} got hugged {times + 1} times from people globally! 💫")
            await ctx.send(embed=em)

        await self.bot.pg_con.execute("UPDATE numbers SET hugs = $1 WHERE user_id = $2", data['hugs'] + 1,
                                      str(member.id))

    @commands.command(help="When someone make you angry, slap him!")
    async def slap(self, ctx, member: discord.Member):
        async with self.bot.session.get('https://waifu.pics/api/sfw/slap') as resp:
            d = (await resp.json())["url"]
            data = await self.bot.pg_con.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
            if not data:
                await self.bot.pg_con.execute("INSERT INTO numbers (user_id, slaps) VALUES ($1, 0)", str(member.id))
                return await ctx.reply("Just a little check, now this member can be hugged, kissed and other stuff :)")
            times = data['slaps']
            if times is None:
                times = 0
            em = discord.Embed(description=f"🎼 **{ctx.author.name}** slaps **{member.name}**!", color=0xffcff1)
            em.set_image(url=d)
            em.set_footer(text=f"{member.name} got slapped {times + 1} times from people globally! 🖐")
            await ctx.send(embed=em)

        await self.bot.pg_con.execute("UPDATE numbers SET slaps = $1 WHERE user_id = $2", data['slaps'] + 1,
                                      str(member.id))

    @commands.command(help="Kill someone, if you hate him/her!")
    async def kill(self, ctx, member: discord.Member):
        async with self.bot.session.get('https://waifu.pics/api/sfw/kill') as resp:
            d = (await resp.json())["url"]
            data = await self.bot.pg_con.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
            if not data:
                await self.bot.pg_con.execute("INSERT INTO numbers (user_id, kills) VALUES ($1, 0)", str(member.id))
                return await ctx.reply("Just a little check, now this member can be hugged, kissed and other stuff :)")
            times = data['kills']
            if times is None:
                times = 0
            em = discord.Embed(description=f"✨ **{ctx.author.name}** killed **{member.name}**!", color=0xffcff1)
            em.set_image(url=d)
            em.set_footer(text=f"{member.name} got killed {times + 1} times from people globally! 🔪")
            await ctx.send(embed=em)

        await self.bot.pg_con.execute("UPDATE numbers SET kills = $1 WHERE user_id = $2", data['kills'] + 1,
                                      str(member.id))

    @commands.command(help="Be nice and kiss members!")
    async def kiss(self, ctx, member: discord.Member):
        async with self.bot.session.get('https://waifu.pics/api/sfw/kiss') as resp:
            d = (await resp.json())["url"]
            data = await self.bot.pg_con.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
            if not data:
                await self.bot.pg_con.execute("INSERT INTO numbers (user_id, kisses) VALUES ($1, 0)", str(member.id))
                return await ctx.reply("Just a little check, now this member can be hugged, kissed and other stuff :)")
            times = data['kisses']
            if times is None:
                times = 0
            em = discord.Embed(description=f"👄 **{ctx.author.name}** kissed **{member.name}**!", color=0xffcff1)
            em.set_image(url=d)
            em.set_footer(text=f"{member.name} got kissed {times + 1} times from people globally! 🥰")
            await ctx.send(embed=em)

        await self.bot.pg_con.execute("UPDATE numbers SET kisses = $1 WHERE user_id = $2", data['kisses'] + 1,
                                      str(member.id))

    @commands.command(help="Lick a member if it looks eatable")
    async def lick(self, ctx, member: discord.Member):
        async with self.bot.session.get('https://waifu.pics/api/sfw/lick') as resp:
            d = (await resp.json())["url"]
            data = await self.bot.pg_con.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
            if not data:
                await self.bot.pg_con.execute("INSERT INTO numbers (user_id, licks) VALUES ($1, 0)", str(member.id))
                return await ctx.reply("Just a little check, now this member can be hugged, kissed and other stuff :)")
            times = data['licks']
            if times is None:
                times = 0
            em = discord.Embed(description=f"👄 **{ctx.author.name}** licked **{member.name}**!", color=0xffcff1)
            em.set_image(url=d)
            em.set_footer(text=f"{member.name} got licked {times + 1} times from people globally! 🥰")
            await ctx.send(embed=em)

        await self.bot.pg_con.execute("UPDATE numbers SET licks = $1 WHERE user_id = $2", data['licks'] + 1,
                                      str(member.id))


def setup(bot):
    bot.add_cog(Funny(bot))

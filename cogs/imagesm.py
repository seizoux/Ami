import asyncpraw
import random
from discord.ext import commands
import discord
import TenGiphPy
import scathach
import aiohttp


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "Images"
        self.session = aiohttp.ClientSession()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Images Loaded")


    @commands.command(help="Be good and give hugs to members!")
    async def hug(self, ctx, member: discord.Member):
        async with self.session.get('http://api.sasaki.me:4444/hug') as resp:
            d = await resp.text()
            data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
            if not data:
                await self.bot.db.execute("INSERT INTO numbers (user_id, hugs) VALUES ($1, 0)", str(member.id))
                em = discord.Embed(description=f"❤ **{ctx.author.name}** has hugged **{member.name}**!", color = 0xffcff1)
                em.set_image(url=d)
                em.set_footer(text=f"{member.name} got hugged 0 times from people globally! 💫")
                await ctx.send(embed=em)
                return
            times = data['hugs']
            if times == None:
                times = 0
            em = discord.Embed(description=f"❤ **{ctx.author.name}** has hugged **{member.name}**!", color = 0xffcff1)
            em.set_image(url=d)
            em.set_footer(text=f"{member.name} got hugged {times+1} times from people globally! 💫")
            await ctx.send(embed=em)

        await self.bot.db.execute("UPDATE numbers SET hugs = $1 WHERE user_id = $2", data['hugs'] + 1, str(member.id))

    @commands.command(help="When someone make you angry, slap him!")
    async def slap(self, ctx, member: discord.Member):
        async with self.session.get('http://api.sasaki.me:4444/slap') as resp:
            d = await resp.text()
            data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
            if not data:
                await self.bot.db.execute("INSERT INTO numbers (user_id, slaps) VALUES ($1, 0)", str(member.id))
                em = discord.Embed(description=f"🎼 **{ctx.author.name}** slaps **{member.name}**!", color = 0xffcff1)
                em.set_image(url=d)
                em.set_footer(text=f"{member.name} got slapped 0 times from people globally! 🖐")
                await ctx.send(embed=em)
                return
            times = data['slaps']
            if times == None:
                times = 0
            em = discord.Embed(description=f"🎼 **{ctx.author.name}** slaps **{member.name}**!", color = 0xffcff1)
            em.set_image(url=d)
            em.set_footer(text=f"{member.name} got slapped {times+1} times from people globally! 🖐")
            await ctx.send(embed=em)

        await self.bot.db.execute("UPDATE numbers SET slaps = $1 WHERE user_id = $2", data['slaps'] + 1, str(member.id))

    @commands.command(help="Kill someone, if you hate him/her!")
    async def kill(self, ctx, member: discord.Member):
        async with self.session.get('http://api.sasaki.me:4444/kill') as resp:
            d = await resp.text()
            data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
            if not data:
                await self.bot.db.execute("INSERT INTO numbers (user_id, kills) VALUES ($1, 0)", str(member.id))
                em = discord.Embed(description=f"✨ **{ctx.author.name}** killed **{member.name}**!", color = 0xffcff1)
                em.set_image(url=d)
                em.set_footer(text=f"{member.name} got killed 0 times from people globally! 🔪")
                await ctx.send(embed=em)
                return
            times = data['kills']
            if times == None:
                times = 0
            em = discord.Embed(description=f"✨ **{ctx.author.name}** killed **{member.name}**!", color = 0xffcff1)
            em.set_image(url=d)
            em.set_footer(text=f"{member.name} got killed {times+1} times from people globally! 🔪")
            await ctx.send(embed=em)

        await self.bot.db.execute("UPDATE numbers SET kills = $1 WHERE user_id = $2", data['kills'] + 1, str(member.id))

    @commands.command(help="Be nice and kiss members!")
    async def kiss(self, ctx, member: discord.Member):
        async with self.session.get('http://api.sasaki.me:4444/kiss') as resp:
            d = await resp.text()
            data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
            if not data:
                await self.bot.db.execute("INSERT INTO numbers (user_id, kisses) VALUES ($1, 0)", str(member.id))
                em = discord.Embed(description=f"👄 **{ctx.author.name}** kissed **{member.name}**!", color = 0xffcff1)
                em.set_image(url=d)
                em.set_footer(text=f"{member.name} got kissed 0 times from people globally! 🥰")
                await ctx.send(embed=em)
                return
            times = data['kisses']
            if times == None:
                times = 0
            em = discord.Embed(description=f"👄 **{ctx.author.name}** kissed **{member.name}**!", color = 0xffcff1)
            em.set_image(url=d)
            em.set_footer(text=f"{member.name} got kissed {times+1} times from people globally! 🥰")
            await ctx.send(embed=em)

        await self.bot.db.execute("UPDATE numbers SET kisses = $1 WHERE user_id = $2", data['kisses'] + 1, str(member.id))

    @commands.command(help="Lick a member if it looks eatable")
    async def lick(self, ctx, member: discord.Member):
        async with self.session.get('http://api.sasaki.me:4444/lick') as resp:
            d = await resp.text()
            data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
            if not data:
                await self.bot.db.execute("INSERT INTO numbers (user_id, licks) VALUES ($1, 0)", str(member.id))
                em = discord.Embed(description=f"👄 **{ctx.author.name}** licked **{member.name}**!", color = 0xffcff1)
                em.set_image(url=d)
                em.set_footer(text=f"{member.name} got licked 0 times from people globally! 🥰")
                await ctx.send(embed=em)
                return
            times = data['licks']
            if times == None:
                times = 0
            em = discord.Embed(description=f"👄 **{ctx.author.name}** licked **{member.name}**!", color = 0xffcff1)
            em.set_image(url=d)
            em.set_footer(text=f"{member.name} got licked {times+1} times from people globally! 🥰")
            await ctx.send(embed=em)

        await self.bot.db.execute("UPDATE numbers SET licks = $1 WHERE user_id = $2", data['licks'] + 1, str(member.id))


    @commands.command(help="Punch someone if you hate him.")
    async def punch(self, ctx, member: discord.Member):
        async with self.session.get('http://api.sasaki.me:4444/punch') as resp:
            d = await resp.text()
            data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
            if not data:
                await self.bot.db.execute("INSERT INTO numbers (user_id, punches) VALUES ($1, 0)", str(member.id))
                em = discord.Embed(description=f"👊 **{ctx.author.name}** punched **{member.name}**!", color = 0xffcff1)
                em.set_image(url=d)
                em.set_footer(text=f"{member.name} got punched 0 times from people globally! 😈")
                await ctx.send(embed=em)
                return
            times = data['punches']
            if times == None:
                times = 0
            em = discord.Embed(description=f"👊 **{ctx.author.name}** punched **{member.name}**!", color = 0xffcff1)
            em.set_image(url=d)
            em.set_footer(text=f"{member.name} got punched {times+1} times from people globally! 😈")
            await ctx.send(embed=em)

        await self.bot.db.execute("UPDATE numbers SET punches = $1 WHERE user_id = $2", data['punches'] + 1, str(member.id))


    @commands.command(help="Pat someone to make it happy")
    async def pat(self, ctx, member: discord.Member):
        async with self.session.get('http://api.sasaki.me:4444/pat') as resp:
            d = await resp.text()
            data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
            if not data:
                await self.bot.db.execute("INSERT INTO numbers (user_id, pats) VALUES ($1, 0)", str(member.id))
                em = discord.Embed(description=f"👀 **{ctx.author.name}** pat **{member.name}**!", color = 0xffcff1)
                em.set_image(url=d)
                em.set_footer(text=f"{member.name} got patted 0 times from people globally! 💌")
                await ctx.send(embed=em)
                return
            times = data['pats']
            if times == None:
                times = 0
            em = discord.Embed(description=f"👀 **{ctx.author.name}** pat **{member.name}**!", color = 0xffcff1)
            em.set_image(url=d)
            em.set_footer(text=f"{member.name} got patted {times+1} times from people globally! 💌")
            await ctx.send(embed=em)

        await self.bot.db.execute("UPDATE numbers SET pats = $1 WHERE user_id = $2", data['pats'] + 1, str(member.id))

    @commands.command(help="Retrive waifu's images based on the type you provide\n`ami waifu sfw` to retrive sfw waifu's\n`ami waifu nsfw` to retrive nsfw waifu's\nLeave `[type]` blank for sfw")
    async def waifu(self, ctx, type:str=None):
        if type is None:
            type = "sfw"

        if type:
            if type == "nsfw":
                if not ctx.channel.nsfw:
                    return await ctx.send(embed=discord.Embed(description="<:alert:819704994612904017> You can use this command only in **NSFW** channels.", color = 0x2F3136))

        async with self.session.get(f'https://api.waifu.pics/{type}/waifu') as resp:
            d = await resp.json()
            s = d["url"]
            em = discord.Embed(color=0xffcff1)
            em.set_image(url=s)
            msg = await ctx.send(embed=em)
            await msg.add_reaction("<:4318crossmark:848857812565229601>")
            await msg.add_reaction("<a:4484pinkarrow:848857813085716520>")

            emojis = ["4318crossmark", "4484pinkarrow"]

            def check(payload):
                return payload.message_id == msg.id and payload.emoji.name in emojis and payload.user_id == ctx.author.id

            while True:
                payload = await self.bot.wait_for("raw_reaction_add", check=check)

                if payload.emoji.name == "4318crossmark":
                    return await msg.delete()

                if payload.emoji.name == "4484pinkarrow":
                    async with self.session.get(f'https://api.waifu.pics/{type}/waifu') as resp:
                        r = await resp.json()
                        c = r["url"]
                        embed = discord.Embed(color=0xffcff1)
                        embed.set_image(url=c)
                        await msg.edit(embed=embed)

    @commands.command(help="Retrive neko's images based on the type you provide\n`ami neko sfw` to retrive sfw neko's\n`ami neko nsfw` to retrive nsfw neko's\nLeave `[type]` blank for sfw")
    async def neko(self, ctx, type:str=None):
        if type is None:
            type = "sfw"
        if type == "nsfw":
            if not ctx.channel.nsfw:
                return await ctx.send(embed=discord.Embed(description="<:alert:819704994612904017> You can use this command only in **NSFW** channels.", color = 0x2F3136))
        async with self.session.get(f'https://api.waifu.pics/{type}/neko') as resp:
            d = await resp.json()
            s = d["url"]
            em = discord.Embed(color=0xffcff1)
            em.set_image(url=s)
            msg = await ctx.send(embed=em)
            await msg.add_reaction("<:4318crossmark:848857812565229601>")
            await msg.add_reaction("<a:4484pinkarrow:848857813085716520>")

            emojis = ["4318crossmark", "4484pinkarrow"]

            def check(payload):
                return payload.message_id == msg.id and payload.emoji.name in emojis and payload.user_id == ctx.author.id

            while True:    
                payload = await self.bot.wait_for("raw_reaction_add", check=check)

                if payload.emoji.name == "4318crossmark":
                    await msg.delete()

                if payload.emoji.name == "4484pinkarrow":
                    async with self.session.get(f'https://api.waifu.pics/{type}/neko') as resp:
                        r = await resp.json()
                        c = r["url"]
                        embed = discord.Embed(color=0xffcff1)
                        embed.set_image(url=c)
                        await msg.edit(embed=embed)

    @commands.command(help="Retrive shinobu's images based on the type you provide\n`ami shinobu sfw` to retrive sfw shinobu's\n`ami shinobu nsfw` to retrive nsfw shinobu's\nLeave `[type]` blank for sfw")
    async def shinobu(self, ctx, type:str=None):
        if type is None:
            type = "sfw"
        if type == "nsfw":
            if not ctx.channel.nsfw:
                return await ctx.send(embed=discord.Embed(description="<:alert:819704994612904017> You can use this command only in **NSFW** channels.", color = 0x2F3136))
        async with self.session.get(f'https://api.waifu.pics/{type}/shinobu') as resp:
            d = await resp.json()
            s = d["url"]
            em = discord.Embed(color=0xffcff1)
            em.set_image(url=s)
            msg = await ctx.send(embed=em)
            await msg.add_reaction("<:4318crossmark:848857812565229601>")

            def check(payload):
                return payload.message_id == msg.id and payload.emoji.name == "4318crossmark" and payload.user_id == ctx.author.id
                    
            payload = await self.bot.wait_for("raw_reaction_add", check=check)
            await msg.delete()

    @commands.command(help="Retrive megumin's images based on the type you provide\n`ami megumin sfw` to retrive sfw megumin's\n`ami megumin nsfw` to retrive nsfw megumin's\nLeave `[type]` blank for sfw")
    async def megumin(self, ctx, type:str=None):
        if type is None:
            type = "sfw"
        if type == "nsfw":
            if not ctx.channel.nsfw:
                return await ctx.send(embed=discord.Embed(description="<:alert:819704994612904017> You can use this command only in **NSFW** channels.", color = 0x2F3136))
        async with self.session.get(f'https://api.waifu.pics/{type}/megumin') as resp:
            d = await resp.json()
            s = d["url"]
            em = discord.Embed(color=0xffcff1)
            em.set_image(url=s)
            msg = await ctx.send(embed=em)
            await msg.add_reaction("<:4318crossmark:848857812565229601>")

            def check(payload):
                return payload.message_id == msg.id and payload.emoji.name == "4318crossmark" and payload.user_id == ctx.author.id
                    
            payload = await self.bot.wait_for("raw_reaction_add", check=check)
            await msg.delete()

def setup(bot):
    bot.add_cog(Images(bot))
    

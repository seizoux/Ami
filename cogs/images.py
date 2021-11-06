from discord.ext import commands
import discord
from asyncio import exceptions


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "Images"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Images Loaded")

    @commands.command(help="Poke some of your friends!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def poke(self, ctx, member: discord.Member):
        try:
            async with self.bot.session.get("https://kawaii.red/api/gif/poke/token=144126010642792449.yr1W3w20QWXXvcOhbVa4") as resp:
                d = await resp.json()
                d = d["response"].strip("'")
                data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
                if not data:
                    await self.bot.db.execute("INSERT INTO numbers (user_id, pokes) VALUES ($1, 0)", str(member.id))
                    em = discord.Embed(description=f"👉 **{ctx.author.name}** poke **{member.name}**!", color = self.bot.color)
                    em.set_image(url=d)
                    em.set_footer(text=f"{member.name} got poked 0 times from people globally! 💫")
                    await ctx.send(embed=em)
                    return

                times = data['pokes']
                if times == None:
                    times = 0
                em = discord.Embed(description=f"👉 **{ctx.author.name}** poke **{member.name}**!", color = self.bot.color)
                em.set_image(url=d)
                em.set_footer(text=f"{member.name} got poked {times+1} times from people globally! 💫")
                await ctx.send(embed=em)

            await self.bot.db.execute("UPDATE numbers SET pokes = $1 WHERE user_id = $2", (times + 1) or 1, str(member.id))
        except Exception:
            return await ctx.send(f"{ctx.author.mention} we ran into some issues, try again later.")

    @commands.command(help="Be good and give hugs to members!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def hug(self, ctx, member: discord.Member):
        try:
            async with self.bot.session.get("https://kawaii.red/api/gif/hug/token=144126010642792449.yr1W3w20QWXXvcOhbVa4") as resp:
                d = await resp.json()
                d = d["response"].strip("'")
                data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
                if not data:
                    await self.bot.db.execute("INSERT INTO numbers (user_id, hugs) VALUES ($1, 0)", str(member.id))
                    em = discord.Embed(description=f"❤ **{ctx.author.name}** has hugged **{member.name}**!", color = self.bot.color)
                    em.set_image(url=d)
                    em.set_footer(text=f"{member.name} got hugged 0 times from people globally! 💫")
                    await ctx.send(embed=em)
                    return

                times = data['hugs']
                if times == None:
                    times = 0
                em = discord.Embed(description=f"❤ **{ctx.author.name}** has hugged **{member.name}**!", color = self.bot.color)
                em.set_image(url=d)
                em.set_footer(text=f"{member.name} got hugged {times+1} times from people globally! 💫")
                await ctx.send(embed=em)

            await self.bot.db.execute("UPDATE numbers SET hugs = $1 WHERE user_id = $2", data['hugs'] + 1, str(member.id))
        except Exception:
            return await ctx.send(f"{ctx.author.mention} we ran into some issues, try again later.")

    @commands.command(help="When someone make you angry, slap him!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slap(self, ctx, member: discord.Member):
        try:
            async with self.bot.session.get("https://kawaii.red/api/gif/slap/token=144126010642792449.yr1W3w20QWXXvcOhbVa4") as resp:
                d = await resp.json()
                d = d["response"].strip("'")
                data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
                if not data:
                    await self.bot.db.execute("INSERT INTO numbers (user_id, slaps) VALUES ($1, 0)", str(member.id))
                    em = discord.Embed(description=f"🎼 **{ctx.author.name}** slaps **{member.name}**!", color = self.bot.color)
                    em.set_image(url=d)
                    em.set_footer(text=f"{member.name} got slapped 0 times from people globally! 🖐")
                    await ctx.send(embed=em)
                    return
                times = data['slaps']
                if times == None:
                    times = 0
                em = discord.Embed(description=f"🎼 **{ctx.author.name}** slaps **{member.name}**!", color = self.bot.color)
                em.set_image(url=d)
                em.set_footer(text=f"{member.name} got slapped {times+1} times from people globally! 🖐")
                await ctx.send(embed=em)

            await self.bot.db.execute("UPDATE numbers SET slaps = $1 WHERE user_id = $2", data['slaps'] + 1, str(member.id))
        except Exception:
            return await ctx.send(f"{ctx.author.mention} we ran into some issues, try again later.")

    @commands.command(help="Kill someone, if you hate him/her!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kill(self, ctx, member: discord.Member):
        try:
            async with self.bot.session.get("https://kawaii.red/api/gif/kill/token=144126010642792449.yr1W3w20QWXXvcOhbVa4") as resp:
                d = await resp.json()
                d = d["response"].strip("'")
                data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
                if not data:
                    await self.bot.db.execute("INSERT INTO numbers (user_id, kills) VALUES ($1, 0)", str(member.id))
                    em = discord.Embed(description=f"✨ **{ctx.author.name}** killed **{member.name}**!", color = self.bot.color)
                    em.set_image(url=d)
                    em.set_footer(text=f"{member.name} got killed 0 times from people globally! 🔪")
                    await ctx.send(embed=em)
                    return
                times = data['kills']
                if times == None:
                    times = 0
                em = discord.Embed(description=f"✨ **{ctx.author.name}** killed **{member.name}**!", color = self.bot.color)
                em.set_image(url=d)
                em.set_footer(text=f"{member.name} got killed {times+1} times from people globally! 🔪")
                await ctx.send(embed=em)

            await self.bot.db.execute("UPDATE numbers SET kills = $1 WHERE user_id = $2", data['kills'] + 1, str(member.id))
        except Exception:
            return await ctx.send(f"{ctx.author.mention} we ran into some issues, try again later.")

    @commands.command(help="Be nice and kiss members!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kiss(self, ctx, member: discord.Member):
        try:
            async with self.bot.session.get("https://kawaii.red/api/gif/kiss/token=144126010642792449.yr1W3w20QWXXvcOhbVa4") as resp:
                d = await resp.json()
                d = d["response"].strip("'")
                data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
                if not data:
                    await self.bot.db.execute("INSERT INTO numbers (user_id, kisses) VALUES ($1, 0)", str(member.id))
                    em = discord.Embed(description=f"👄 **{ctx.author.name}** kissed **{member.name}**!", color = self.bot.color)
                    em.set_image(url=d)
                    em.set_footer(text=f"{member.name} got kissed 0 times from people globally! 🥰")
                    await ctx.send(embed=em)
                    return
                times = data['kisses']
                if times == None:
                    times = 0
                em = discord.Embed(description=f"👄 **{ctx.author.name}** kissed **{member.name}**!", color = self.bot.color)
                em.set_image(url=d)
                em.set_footer(text=f"{member.name} got kissed {times+1} times from people globally! 🥰")
                await ctx.send(embed=em)

            await self.bot.db.execute("UPDATE numbers SET kisses = $1 WHERE user_id = $2", data['kisses'] + 1, str(member.id))
        except Exception:
            return await ctx.send(f"{ctx.author.mention} we ran into some issues, try again later.")

    @commands.command(help="Lick a member if it looks eatable")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lick(self, ctx, member: discord.Member):
        try:
            async with self.bot.session.get("https://kawaii.red/api/gif/lick/token=144126010642792449.yr1W3w20QWXXvcOhbVa4") as resp:
                d = await resp.json()
                d = d["response"].strip("'")
                data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
                if not data:
                    await self.bot.db.execute("INSERT INTO numbers (user_id, licks) VALUES ($1, 0)", str(member.id))
                    em = discord.Embed(description=f"👄 **{ctx.author.name}** licked **{member.name}**!", color = self.bot.color)
                    em.set_image(url=d)
                    em.set_footer(text=f"{member.name} got licked 0 times from people globally! 🥰")
                    await ctx.send(embed=em)
                    return
                times = data['licks']
                if times == None:
                    times = 0
                em = discord.Embed(description=f"👄 **{ctx.author.name}** licked **{member.name}**!", color = self.bot.color)
                em.set_image(url=d)
                em.set_footer(text=f"{member.name} got licked {times+1} times from people globally! 🥰")
                await ctx.send(embed=em)

            await self.bot.db.execute("UPDATE numbers SET licks = $1 WHERE user_id = $2", data['licks'] + 1, str(member.id))
        except Exception:
            return await ctx.send(f"{ctx.author.mention} we ran into some issues, try again later.")


    @commands.command(help="Punch someone if you hate him.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def punch(self, ctx, member: discord.Member):
        try:
            async with self.bot.session.get("https://kawaii.red/api/gif/punch/token=144126010642792449.yr1W3w20QWXXvcOhbVa4") as resp:
                d = await resp.json()
                d = d["response"].strip("'")
                data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
                if not data:
                    await self.bot.db.execute("INSERT INTO numbers (user_id, punches) VALUES ($1, 0)", str(member.id))
                    em = discord.Embed(description=f"👊 **{ctx.author.name}** punched **{member.name}**!", color = self.bot.color)
                    em.set_image(url=d)
                    em.set_footer(text=f"{member.name} got punched 0 times from people globally! 😈")
                    await ctx.send(embed=em)
                    return
                times = data['punches']
                if times == None:
                    times = 0
                em = discord.Embed(description=f"👊 **{ctx.author.name}** punched **{member.name}**!", color = self.bot.color)
                em.set_image(url=d)
                em.set_footer(text=f"{member.name} got punched {times+1} times from people globally! 😈")
                await ctx.send(embed=em)

            await self.bot.db.execute("UPDATE numbers SET punches = $1 WHERE user_id = $2", data['punches'] + 1, str(member.id))
        except Exception:
            return await ctx.send(f"{ctx.author.mention} we ran into some issues, try again later.")


    @commands.command(help="Pat someone to make it happy")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pat(self, ctx, member: discord.Member):
        try:
            async with self.bot.session.get("https://kawaii.red/api/gif/pat/token=144126010642792449.yr1W3w20QWXXvcOhbVa4") as resp:
                d = await resp.json()
                d = d["response"].strip("'")
                data = await self.bot.db.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
                if not data:
                    await self.bot.db.execute("INSERT INTO numbers (user_id, pats) VALUES ($1, 0)", str(member.id))
                    em = discord.Embed(description=f"👀 **{ctx.author.name}** pat **{member.name}**!", color = self.bot.color)
                    em.set_image(url=d)
                    em.set_footer(text=f"{member.name} got patted 0 times from people globally! 💌")
                    await ctx.send(embed=em)
                    return
                times = data['pats']
                if times == None:
                    times = 0
                em = discord.Embed(description=f"👀 **{ctx.author.name}** pat **{member.name}**!", color = self.bot.color)
                em.set_image(url=d)
                em.set_footer(text=f"{member.name} got patted {times+1} times from people globally! 💌")
                await ctx.send(embed=em)

            await self.bot.db.execute("UPDATE numbers SET pats = $1 WHERE user_id = $2", data['pats'] + 1, str(member.id))
        except Exception:
            return await ctx.send(f"{ctx.author.mention} we ran into some issues, try again later.")

    @commands.command(help="Retrive waifu's images based on the type you provide\n`ami waifu sfw` to retrive sfw waifu's\n`ami waifu nsfw` to retrive nsfw waifu's\nLeave `[type]` blank for sfw")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def waifu(self, ctx, type:str=None):
        if type is None:
            type = "sfw"

        if type:
            if type == "nsfw":
                if not ctx.channel.nsfw:
                    return await ctx.send(embed=discord.Embed(description="<:alert:819704994612904017> You can use this command only in **NSFW** channels.", color = 0x2F3136))

        async with self.bot.session.get(f'https://api.waifu.pics/{type}/waifu') as resp:
            d = await resp.json()
            try:
                s = d["url"]
            except Exception:
                return await ctx.send(f'{ctx.author.mention} too many requests are going on, please hold on a few seconds and try again.')
            em = discord.Embed(color=self.bot.color)
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
                    async with self.bot.session.get(f'https://api.waifu.pics/{type}/waifu') as resp:
                        r = await resp.json()
                        c = r["url"]
                        embed = discord.Embed(color=self.bot.color)
                        embed.set_image(url=c)
                        await msg.edit(embed=embed)

    @commands.command(help="Retrive neko's images based on the type you provide\n`ami neko sfw` to retrive sfw neko's\n`ami neko nsfw` to retrive nsfw neko's\nLeave `[type]` blank for sfw")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def neko(self, ctx, type:str=None):
        if type is None:
            type = "sfw"
        if type == "nsfw":
            if not ctx.channel.nsfw:
                return await ctx.send(embed=discord.Embed(description="<:alert:819704994612904017> You can use this command only in **NSFW** channels.", color = 0x2F3136))
        
        async with self.bot.session.get(f'https://api.waifu.pics/{type}/neko') as resp:
            d = await resp.json()
            try:
                s = d["url"]
            except Exception:
                return await ctx.send(f'{ctx.author.mention} too many requests are going on, please hold on a few seconds and try again.')
            em = discord.Embed(color=self.bot.color)
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
                    async with self.bot.session.get(f'https://api.waifu.pics/{type}/neko') as resp:
                        r = await resp.json()
                        c = r["url"]
                        embed = discord.Embed(color=self.bot.color)
                        embed.set_image(url=c)
                        await msg.edit(embed=embed)

    @commands.command(help="Retrive shinobu's images based on the type you provide\n`ami shinobu sfw` to retrive sfw shinobu's\n`ami shinobu nsfw` to retrive nsfw shinobu's\nLeave `[type]` blank for sfw")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def shinobu(self, ctx, type:str=None):
        if type is None:
            type = "sfw"
        if type == "nsfw":
            if not ctx.channel.nsfw:
                return await ctx.send(embed=discord.Embed(description="<:alert:819704994612904017> You can use this command only in **NSFW** channels.", color = 0x2F3136))
        
        async with self.bot.session.get(f'https://api.waifu.pics/{type}/shinobu') as resp:
            d = await resp.json()
            try:
                s = d["url"]
            except Exception:
                return await ctx.send(f'{ctx.author.mention} too many requests are going on, please hold on a few seconds and try again.')
            em = discord.Embed(color=self.bot.color)
            em.set_image(url=s)
            msg = await ctx.send(embed=em)
            await msg.add_reaction("<:4318crossmark:848857812565229601>")

            def check(payload):
                return payload.message_id == msg.id and payload.emoji.name == "4318crossmark" and payload.user_id == ctx.author.id
                    
            payload = await self.bot.wait_for("raw_reaction_add", check=check)
            await msg.delete()

    @commands.command(help="Retrive megumin's images based on the type you provide\n`ami megumin sfw` to retrive sfw megumin's\n`ami megumin nsfw` to retrive nsfw megumin's\nLeave `[type]` blank for sfw")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def megumin(self, ctx, type:str=None):
        if type is None:
            type = "sfw"
        if type == "nsfw":
            if not ctx.channel.nsfw:
                return await ctx.send(embed=discord.Embed(description="<:alert:819704994612904017> You can use this command only in **NSFW** channels.", color = 0x2F3136))
        
        async with self.bot.session.get(f'https://api.waifu.pics/{type}/megumin') as resp:
            d = await resp.json()
            try:
                s = d["url"]
            except Exception:
                return await ctx.send(f'{ctx.author.mention} too many requests are going on, please hold on a few seconds and try again.')
            em = discord.Embed(color=self.bot.color)
            em.set_image(url=s)
            msg = await ctx.send(embed=em)
            await msg.add_reaction("<:4318crossmark:848857812565229601>")

            def check(payload):
                return payload.message_id == msg.id and payload.emoji.name == "4318crossmark" and payload.user_id == ctx.author.id
                    
            payload = await self.bot.wait_for("raw_reaction_add", check=check)
            await msg.delete()

def setup(bot):
    bot.add_cog(Images(bot))
    

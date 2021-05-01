import discord
from discord.ext import commands
import random
import datetime
from datetime import timedelta
import time
from discord.ext.commands.cooldowns import BucketType
import simpleeval
import asyncio
import pytz
from pytz import all_timezones
from jishaku.paginators import WrappedPaginator, PaginatorInterface
import re
from discord_markdown.discord_markdown import convert_to_html
from mal import *
from PIL import Image,ImageDraw, ImageFont
import textwrap
from wonderwords import RandomSentence
from cogsf.fuzzy import finder
import async_cleverbot as ac
from urllib.parse import urlencode
from urllib.request import urlretrieve
import aiohttp
import requests

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afks = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Fun Loaded")

    @commands.command(help="Take a look on Covid-19 stats")
    async def covid(self, ctx, *, countryName = None):
        try:
            if countryName is None:
                embed=discord.Embed(title="Whoops! Be sure to select a country! ```ami covid [country]```", colour=0xff0000, timestamp=ctx.message.created_at)
                await ctx.send(embed=embed)


            else:
                url = f"https://coronavirus-19-api.herokuapp.com/countries/{countryName}"
                stats = requests.get(url)
                json_stats = stats.json()
                country = json_stats["country"]
                totalCases = json_stats["cases"]
                todayCases = json_stats["todayCases"]
                totalDeaths = json_stats["deaths"]
                todayDeaths = json_stats["todayDeaths"]
                recovered = json_stats["recovered"]
                active = json_stats["active"]
                critical = json_stats["critical"]
                casesPerOneMillion = json_stats["casesPerOneMillion"]
                deathsPerOneMillion = json_stats["deathsPerOneMillion"]
                totalTests = json_stats["totalTests"]
                testsPerOneMillion = json_stats["testsPerOneMillion"]

                embed2 = discord.Embed(title=f"**COVID-19 Status Of {country}**!", colour=0xffcff1, timestamp=ctx.message.created_at)
                embed2.add_field(name="**Total Cases**", value=totalCases, inline=True)
                embed2.add_field(name="**Today Cases**", value=todayCases, inline=True)
                embed2.add_field(name="**Total Deaths**", value=totalDeaths, inline=True)
                embed2.add_field(name="**Today Deaths**", value=todayDeaths, inline=True)
                embed2.add_field(name="**Recovered**", value=recovered, inline=True)
                embed2.add_field(name="**Active**", value=active, inline=True)
                embed2.add_field(name="**Critical**", value=critical, inline=True)
                embed2.add_field(name="**Cases Per One Million**", value=casesPerOneMillion, inline=True)
                embed2.add_field(name="**Deaths Per One Million**", value=deathsPerOneMillion, inline=True)
                embed2.add_field(name="**Total Tests**", value=totalTests, inline=True)
                embed2.add_field(name="**Tests Per One Million**", value=testsPerOneMillion, inline=True)

                embed2.set_thumbnail(url="https://cdn.discordapp.com/attachments/564520348821749766/701422183217365052/2Q.png")
                await ctx.send(embed=embed2)

        except:
            embed3 = discord.Embed(title="Invalid Country Name!", colour=0xffcff1, timestamp=ctx.message.created_at)
            embed3.set_author(name="Error!")
            await ctx.send(embed=embed3)


    @commands.command(help="Be good and give hugs to members!")
    async def hug(self, ctx, member: discord.Member):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://api.sasaki.me:4444/hug') as resp:
                d = await resp.text()
                data = await self.bot.pg_con.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
                if not data:
                    await self.bot.pg_con.execute("INSERT INTO numbers (user_id, hugs) VALUES ($1, 0)", str(member.id))
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

        await self.bot.pg_con.execute("UPDATE numbers SET hugs = $1 WHERE user_id = $2", data['hugs'] + 1, str(member.id))

    @commands.command(help="When someone make you angry, slap him!")
    async def slap(self, ctx, member: discord.Member):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://api.sasaki.me:4444/slap') as resp:
                d = await resp.text()
                data = await self.bot.pg_con.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
                if not data:
                    await self.bot.pg_con.execute("INSERT INTO numbers (user_id, slaps) VALUES ($1, 0)", str(member.id))
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

        await self.bot.pg_con.execute("UPDATE numbers SET slaps = $1 WHERE user_id = $2", data['slaps'] + 1, str(member.id))

    @commands.command(help="Kill someone, if you hate him/her!")
    async def kill(self, ctx, member: discord.Member):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://api.sasaki.me:4444/kill') as resp:
                d = await resp.text()
                data = await self.bot.pg_con.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
                if not data:
                    await self.bot.pg_con.execute("INSERT INTO numbers (user_id, kills) VALUES ($1, 0)", str(member.id))
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

        await self.bot.pg_con.execute("UPDATE numbers SET kills = $1 WHERE user_id = $2", data['kills'] + 1, str(member.id))

    @commands.command(help="Be nice and kiss members!")
    async def kiss(self, ctx, member: discord.Member):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://api.sasaki.me:4444/kiss') as resp:
                d = await resp.text()
                data = await self.bot.pg_con.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
                if not data:
                    await self.bot.pg_con.execute("INSERT INTO numbers (user_id, kisses) VALUES ($1, 0)", str(member.id))
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

        await self.bot.pg_con.execute("UPDATE numbers SET kisses = $1 WHERE user_id = $2", data['kisses'] + 1, str(member.id))

    @commands.command(help="Lick a member if it looks eatable")
    async def lick(self, ctx, member: discord.Member):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://api.sasaki.me:4444/lick') as resp:
                d = await resp.text()
                data = await self.bot.pg_con.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
                if not data:
                    await self.bot.pg_con.execute("INSERT INTO numbers (user_id, licks) VALUES ($1, 0)", str(member.id))
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

        await self.bot.pg_con.execute("UPDATE numbers SET licks = $1 WHERE user_id = $2", data['licks'] + 1, str(member.id))


    @commands.command(help="Punch someone if you hate him.")
    async def punch(self, ctx, member: discord.Member):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://api.sasaki.me:4444/punch') as resp:
                d = await resp.text()
                data = await self.bot.pg_con.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
                if not data:
                    await self.bot.pg_con.execute("INSERT INTO numbers (user_id, punches) VALUES ($1, 0)", str(member.id))
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

        await self.bot.pg_con.execute("UPDATE numbers SET punches = $1 WHERE user_id = $2", data['punches'] + 1, str(member.id))


    @commands.command(help="Pat someone to make it happy")
    async def pat(self, ctx, member: discord.Member):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://api.sasaki.me:4444/pat') as resp:
                d = await resp.text()
                data = await self.bot.pg_con.fetchrow("SELECT * FROM numbers WHERE user_id = $1", str(member.id))
                if not data:
                    await self.bot.pg_con.execute("INSERT INTO numbers (user_id, pats) VALUES ($1, 0)", str(member.id))
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

        await self.bot.pg_con.execute("UPDATE numbers SET pats = $1 WHERE user_id = $2", data['pats'] + 1, str(member.id))



    @commands.command(help="Set your AFK mode.")
    async def afk(self, ctx, *, reason=None):
        if reason == None:
            reason = "Not specified."

        await ctx.send(f"<:KannaSip:819739316502134805> **{ctx.author.name}** i've set your afk for `{reason}`")
        self.afks[ctx.author.id] = reason

    @commands.command()
    @commands.is_owner()
    async def afklist(self, ctx):
        return await ctx.send(self.afks)

    @commands.Cog.listener("on_message")
    async def foo(self, message: discord.Message):

        if message.author == self.bot.user:
            return

        if message.content.startswith("ami afk"):
            return self.afk

        if message.content.startswith("Ami afk"):
            return self.afk

        if message.author.id in self.afks.keys():
            ids = message.author.id
            await message.channel.send(f"<:nezyay:819703490078834729> Welcome back {message.author.mention}, i removed your **AFK** status.")
            del self.afks[ids]

        try:
            id2 = message.mentions[0].id
        except IndexError:
            id2 = "None"
        if id2 in self.afks.keys():
            reasons = self.afks[id2]
            return await message.channel.send(f'<:nani:819694934491004937> {message.author.mention}, **{str(message.mentions[0].name)}** is afk for `{reasons}`')


    @commands.command(help="Choose between multiple choiches")
    async def choose(self, ctx, *choices: str):
        text = ["Why this usless question?", "The answer is...", "I think the right choice is...", "Don't blame me."]
        textc = random.choice(text)
        choi = random.choice(choices)
        em = discord.Embed(title=textc, description =f"```py\n{choi}\n```", color = 0xffcff1)
        em.set_footer(text=f"{ctx.author.name}, do it.")
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)

    @commands.command()
    async def source(self, ctx):
        await ctx.reply("I'm closed source.")


    @commands.command(help="Simulate the PornHub carrier of a member")
    async def ph(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author

        views = random.randint(1, 50000000)
        subs = random.randint(1, 25000000)
        likes = random.randint(1, 200000000)
        comments = random.randint(1, 1000000)
        videos = random.randint(1, 300)
        status = ["Verified.", "Not Verified."]
        status1 = random.choice(status)
        em = discord.Embed(title="<:pepehot:819703490330492948> PornHub Simulator!", description=f"```py\n{member.name} Stats 2020/2021\n```", color = 0xffcff1)
        em.add_field(name="<:gsarrow:819706480714055681> Views", value=f"```py\n{views}\n```")
        em.add_field(name="<:gsarrow:819706480714055681> Subscribers", value=f"```py\n{subs}\n```")
        em.add_field(name="<:gsarrow:819706480714055681> Likes", value=f"```py\n{likes}\n```")
        em.add_field(name="<:gsarrow:819706480714055681> Comments", value=f"```py\n{comments}\n```")
        em.add_field(name="<:gsarrow:819706480714055681> Status", value=f"```py\n{status1}\n```")
        em.add_field(name="<:gsarrow:819706480714055681> Videos", value=f"```py\n{videos}\n```")
        em.set_thumbnail(url=member.avatar_url)
        em.set_footer(text="Explicit content!")
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)



    @commands.command(help="Test your reaction timing",aliases=["rspeed"])
    async def reactspeed(self, ctx, number:int):
        if number > 20:
            em = discord.Embed(description="<:alert:819704994612904017> Time can't be over 20 seconds.")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return
            

        embed=discord.Embed(description=f"Try to click on reaction at {number} seconds.", color=0xffcff1)
        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
        message = await ctx.send(embed=embed)
        await message.add_reaction("<a:nono:819694934189277214>")
        start = time.time()
        
        def check(payload):
            return payload.message_id == message.id and payload.emoji.name == "nono" and payload.user_id == ctx.author.id
            
        payload = await self.bot.wait_for("raw_reaction_add", check=check)
        end = time.time()
        embed=discord.Embed(description=f"<:vea:819703490703523860> Your result is: `{round(end-start, 2)}` seconds", color=0xffcff1)
        embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
        await message.edit(embed=embed)


    @commands.command(help="Get the invite link for ami")
    async def invite(self, ctx):
        em = discord.Embed(description="https://amidiscord.xyz/", color = 0xffcff1)
        await ctx.send(embed=em)


    @commands.command(help="Ship 2 members")
    async def ship(self, ctx, member: discord.Member):
        ship = random.randint(1, 100)
        comp = random.randint(1, 10)
        types = ["Active", "Dangerous", "Total Love", "Usless", "More hot than me", "Netflix & Bed", "Extreme", "Super!"]
        types1 = random.choice(types)
        message = ctx.message
        mention1 = message.mentions[0]
        mention2 = message.mentions[1]
        em = discord.Embed(title="<:thanks:739614671774154843> Ship Results!", description = f"<:gsarrow:819706480714055681> The ship » {mention1.mention} & {mention2.mention}\n\n<:gsarrow:819706480714055681> Compatibility » `{comp}/10`\n\n<:gsarrow:819706480714055681> Relation type » `{types1}`\n\n<:gsarrow:819706480714055681> Percent » `{ship}/100%`", color = 0xffcff1)
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)


    @commands.command(help="Do a math calculation")
    async def calc(self, ctx, *, expression:str):
        try:
            calculation = simpleeval.simple_eval(expression)

            if len(str(calculation)) > 20:
                em = discord.Embed(description=f"```py\nNah, cya! <3\n```", color = 0xffcff1)
                await ctx.send(embed=em)
                return

            if str(expression) == "...":
                em = discord.Embed(description=f"```py\nNah, cya! <3\n```", color = 0xffcff1)
                await ctx.send(embed=em)
                return

            start = time.time()
            em = discord.Embed(color=0xffcff1)
            em.add_field(name="Input", value=f"```py\n{expression}\n```")
            em.add_field(name="Output", value=f"```py\n{calculation}\n```")
            end = time.time()
            em.set_footer(text=f"Calculated in {round(end-start, 5)} seconds!")
            await ctx.send(embed=em)

        except simpleeval.NameNotDefined:
            em = discord.Embed(description=f"```py\n{expression} = <3\n```", color = 0xffcff1)
            await ctx.send(embed=em)
            return

        except simpleeval.FeatureNotAvailable:
            em = discord.Embed(description=f"```py\n{expression} = you.\n```", color = 0xffcff1)
            await ctx.send(embed=em)
            return

        except ZeroDivisionError:
            em = discord.Embed(description=f"```py\n{expression} = 0.\n```", color = 0xffcff1)
            await ctx.send(embed=em)
            return

        except IndexError:
            em = discord.Embed(description=f"```py\nPff, try again stupid dumbass.\n```", color = 0xffcff1)
            await ctx.send(embed=em)
            return

        except SyntaxError:
            em = discord.Embed(description=f"```py\nShut down your pc.\n```", color = 0xffcff1)
            await ctx.send(embed=em)
            return

        except simpleeval.FunctionNotDefined:
            em = discord.Embed(description=f"```py\nYeah, for sure.\n```", color = 0xffcff1)
            await ctx.send(embed=em)
            return

        except simpleeval.NumberTooHigh:
            em = discord.Embed(description=f"```py\nFuck off, you and these infinite numbers.\n```", color = 0xffcff1)
            await ctx.send(embed=em)
            return

    @commands.command(help="Get a nitro gift")
    async def nitro(self, ctx):
        await ctx.send("https://pics.me.me/thumb_when-youre-broke-so-you-make-your-own-nitro-boost-69569902.png")


    @commands.command(help="Get a member avatar",pass_context=True, aliases=["av"])
    async def avatar(self, ctx, member:discord.Member=None):
        if member == None:
            member = ctx.author

        cpng = str(member.avatar_url).replace(".webp", ".png")
        cjpg = str(member.avatar_url).replace(".webp", ".jpg")
        cjpeg = str(member.avatar_url).replace(".webp", ".jpeg")
        cgif = str(member.avatar_url).replace(".webp", ".gif")
        ctiff = str(member.avatar_url).replace(".webp", ".tif")
        cbmp = str(member.avatar_url).replace(".webp", ".bmp")
        cwebp = str(member.avatar_url)

        png = f"[`PNG`]({cpng})"
        jpg = f"[`JPG`]({cjpg})"
        jpeg = f"[`JPEG`]({cjpeg})"
        gif = f"[`GIF`]({cgif})"
        tif = f"[`TIF`]({ctiff})"
        bmp = f"[`BMP`]({cbmp})"
        webp = f"[`WEBP`]({cwebp})"

        em = discord.Embed(title=f"{member.name}'s avatar!",description=f"{png} | {jpg} | {jpeg} | {gif} | {webp} | {tif} | {bmp}", color = 0xffcff1)
        em.set_image(url=member.avatar_url)
        em.set_footer(text=f"Requested by {ctx.author.name}")
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)


 # Members Counter Command
    @commands.command(help="Get the total members of the guild")
    async def mc(self, ctx):
        a = ctx.guild.member_count
        b = len([m for m in ctx.guild.members if (m.bot)])
        c = len([m for m in ctx.guild.members if not m.bot])
        d = discord.Embed(title=f":busts_in_silhouette: **Results:**", description = f"\n<:user:819703150755577856> *Total*  »  `{a}`\n<:thumbsup:819703492481908776> *Humans*  »  `{c}`\n<:1739_CMD:819689870393999380> *Bots*  »  `{b}`", color=discord.Color(0xffff00))
        d.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=d)


# Ping & Pong
    @commands.command(help="Check the latency",pass_context=True)
    async def ping(self, ctx):
        websocket = round(self.bot.latency*1000, 2)
        typing = round(self.bot.latency*150, 2)
        database = round(self.bot.latency*10, 2)
        em = discord.Embed(color=0xffcff1)
        em.add_field(name="WebSocket", value=f"`{websocket}`ms")
        em.add_field(name="Typing", value=f"`{typing}`ms")
        em.add_field(name="Database", value=f"`{database}`ms")
        await ctx.send(embed=em)

    @commands.command(help="Cum on someone")
    @commands.is_nsfw()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cum(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author

        em = discord.Embed(description="**Cumming in 3...**", color = 0xffcff1)
        msg = await ctx.send(embed=em)
        await asyncio.sleep(1)
        em = discord.Embed(description="**Cumming in 2...**", color = 0xffcff1)
        await msg.edit(embed=em)
        await asyncio.sleep(1)
        em = discord.Embed(description="**Cumming in 1...**", color = 0xffcff1)
        await msg.edit(embed=em)
        await asyncio.sleep(1)
        choices = ["Face", "Ass", "Ears", "Nose", "Lips", "Feet", "Hands", "Eyes", "Head", "Balls"]
        tchoice = random.choice(choices)
        km = random.randint(13, 322)
        em = discord.Embed(description=f"I've cummed on the **{tchoice}** of **{member.name}** at **{km}Km/h** <a:7337_Furry_Dance_Green:819689872923033631>", color = 0xffcff1)
        await msg.edit(embed=em)


    @commands.command(help="Link for the top.gg vote page")
    async def vote(self, ctx):
        link = "[`vote on top.gg!`](https://top.gg/bot/801742991185936384)"
        link2 = "[`vote on discordbotlist!`](https://discordbotlist.com/bots/ami)"
        em = discord.Embed(description=f"**{link}** (**`+20k Coins`**)\n**{link2}**\nThanks if you vote! <3", color = 0xffcff1)
        await ctx.send(embed=em)


    @commands.command(help="See the humor of a member")
    async def humor(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
            
        humors = ['Sad 😭', 'Happy 😁']
        humc = random.choice(humors)
        await ctx.send(f"**{member.name}** is **{humc}**")


    @commands.command(help="See your actual time or the time of a member")
    async def time(self, ctx, member: discord.Member = None):
        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        db = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)


        if member:
            member_id = str(member.id)
            db1 = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", member_id)

            if not db1:
                return await ctx.reply(f"I didn't found this member inside the database, tell him to send `ami bal` and retry again after done.")

            if db1["tz"] == None:
                tmz = "[All valid zones list](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568)"
                em = discord.Embed(description=f"The member didn't provided a zone.\n{tmz}", color = 0xffcff1)
                await ctx.send(embed=em)
                return

            t = db1["tz"]
            fmt = '%A | %H:%M | %d/%m/%Y'
            dt_today = datetime.datetime.today()   # Local time
            dt_India = dt_today.astimezone(pytz.timezone(t)) 
            t3 = (dt_India.strftime(fmt))
            em = discord.Embed(title=f"<a:9932_zero_two:819689873870946395> Time for {member.name}", description = f"• {t3}", color = 0xffcff1)
            em.set_footer(text=f"{t}", icon_url=f"{member.avatar_url}")
            await ctx.send(embed=em)
            return


        if not db:
            return await ctx.reply(f"I didn't found you inside the database, send `ami bal` to be added in the database.")

        utz = db["tz"]

        if utz == None:
            tmz = "[All valid zones list](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568)"
            em = discord.Embed(description=f"You didn't provide a zone: use `ami set-tz` to set it.\n{tmz}", color = 0xffcff1)
            await ctx.send(embed=em)
            return

        t = db["tz"]
        fmt = '%A | %H:%M | %d/%m/%Y'
        dt_today = datetime.datetime.today()   # Local time
        dt_India = dt_today.astimezone(pytz.timezone(t)) 
        t3 = (dt_India.strftime(fmt))
        em = discord.Embed(title=f"<a:9932_zero_two:819689873870946395> Time for {ctx.author.name}", description = f"• {t3}", color = 0xffcff1)
        em.set_footer(text=f"{t} • 24h Format", icon_url=f"{ctx.author.avatar_url}")
        await ctx.send(embed=em)


    @commands.command(help="Set your timezone to check your time",aliases=["set-tz"])
    async def timezone(self, ctx, zone):
        author_id = str(ctx.author.id)
        db = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        if zone == None:
            await ctx.send(f"{ctx.author.name}, be sure to send a zone across the command.")
            return

        if zone in all_timezones:
            zone1 = zone
            await self.bot.pg_con.execute("UPDATE users SET tz = $1 WHERE user_id = $2", zone, author_id)
            await ctx.send(f"{ctx.author.name}, you have set **{zone1}** as a zone!")
        else:
            await ctx.send("The zone you provided isn't in the list.")


    @commands.command()
    @commands.is_owner()
    async def setzone(self,ctx,member:discord.Member, *, args):
        member_id = str(member.id)
        guild_id = str(ctx.guild.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", member_id)
        timezone = args

        if timezone == None:
            em = discord.Embed(description="Specify a zone!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        if timezone in all_timezones:
            zone1 = timezone
            await self.bot.pg_con.execute("UPDATE users SET tz = $1 WHERE user_id = $2", zone1, member_id)
            await ctx.send(f"Set **{timezone}** for `{member}`!")
        else:
            await ctx.send("Zone not found.")


    @commands.command(help="Take a screenshot of a url page")
    @commands.is_owner()
    async def ssh(self, ctx, arg):
        auth = '15167-5210acccef7b9f84f455fe89088b7cfb'
        msg = ctx.message
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',msg.content.lower())  
        if urls:
            params = urlencode(dict(access_key="1b3e59ebecf44a4eab5b5b5699bd37df",
                                    url=arg))
            urlretrieve("https://api.apiflash.com/v1/urltoimage?" + params, "screenshot.jpeg")
            lat = (round(self.bot.latency*1000, 2))
            em = discord.Embed(color=0xffcff1)
            file = discord.File("screenshot.jpeg")
            em.set_image(url="attachment://screenshot.jpeg")
            em.set_footer(text=f"Screenshot latency | {lat}ms.")
            await ctx.send(embed=em, file=file)
        else:
            return await ctx.send("This isn't a link.")


    @commands.command(help="Earn coins with your typespeed")
    @commands.max_concurrency(1, BucketType.default)
    async def type(self, ctx):
        s = RandomSentence()
        answer = s.sentence()
        img = Image.open("white.png")
        font = ImageFont.truetype("standard.ttf", 108)
        draw = ImageDraw.Draw(img)
        text = f"{answer}"
        margin = offset = 20
        for line in textwrap.wrap(text, width=30):
            draw.text((margin, offset), line, font=font, fill="#ffffff")
            offset += font.getsize(line)[1]
            img.save("whitet.png")

        file = discord.File("whitet.png")
        time_listen = datetime.datetime.utcnow() + timedelta(seconds=20)
        em = discord.Embed(title =f"The first member to type this, wins!",color = 0x2F3136)
        em.set_image(url="attachment://whitet.png")
        em.set_footer(text="Be sure to don't miss any character.")
        await ctx.send(embed=em, file=file)
        starttime = time.time()
        while True:
            try:
                guess = await self.bot.wait_for('message', check=lambda m: not m.author.bot and m.channel == ctx.channel, timeout=20.0)
            except asyncio.TimeoutError:
                return await ctx.send("No one has sent the message.")


            if guess.content == answer:
                guild_id = str(ctx.guild.id)
                author_id = str(guess.author.id)
                earnings = random.randint(300,1200)
                user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1",  author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user["wallet"] + 1*earnings, author_id)
                fintime = time.time()
                total = fintime - starttime
                em = discord.Embed(description=f"**{guess.author}**, well done! You got **{earnings}** coins!\nCompleted in `{round(total, 2)}` seconds!", color = 0x2F3136)
                await ctx.send(embed=em)
                await self.bot.pg_con.execute("UPDATE users SET total_earn = $1 WHERE user_id = $2", user["total_earn"] + earnings, author_id)
                return



    @commands.command(help="Convert the discord markdown into html format")
    async def html(self, ctx, *, args):
        html = convert_to_html(args)
        em = discord.Embed(description = f"```\n{html}\n```", color = 0x2F3136)
        await ctx.send(embed=em)


    @commands.command(help="Search an anime on MyAnimeList")
    async def sa(self, ctx, *args):
        search = AnimeSearch(args) # Search for "cowboy bebop"
        link = f"[Click here to watch it now!]({search.results[0].url})"
        lat = (round(self.bot.latency*1000, 2))
        em = discord.Embed(title=f"```{search.results[0].title}```", description=search.results[0].synopsis, color =0x2F3136)
        em.add_field(name="Episodes", value=f"`{search.results[0].episodes} 📺`")
        em.add_field(name="Type", value=f"`{search.results[0].type} 🎬`")
        em.add_field(name="Score", value=f"`{search.results[0].score} 🌟`")
        em.add_field(name="\u200b", value=f"<:gsarrow:819706480714055681> **{link}**")
        em.set_thumbnail(url=search.results[0].image_url)
        em.set_footer(text=f"Search latency : {lat}ms")
        await ctx.send(embed=em)


    @commands.command(help="Search a manga on MyAnimeList")
    async def sm(self, ctx, *args):
        search = MangaSearch(args) # Search for "cowboy bebop"
        link = f"[Click here to read it now!]({search.results[0].url})"
        lat = (round(self.bot.latency*1000, 2))
        em = discord.Embed(title=f"```{search.results[0].title}```", description=search.results[0].synopsis, color =0x2F3136)
        em.add_field(name="Volumes", value=f"`{search.results[0].volumes} 📺`")
        em.add_field(name="Type", value=f"`{search.results[0].type} 🎬`")
        em.add_field(name="Score", value=f"`{search.results[0].score} 🌟`")
        em.add_field(name="\u200b", value=f"<:gsarrow:819706480714055681> **{link}**")
        em.set_thumbnail(url=search.results[0].image_url)
        em.set_footer(text=f"Search latency : {lat}ms")
        await ctx.send(embed=em)


    @commands.command(help="Talk with me and earn coins for total talked time", aliases = ["oc"])
    @commands.max_concurrency(1, BucketType.user)
    async def openchat(self, ctx):
        member_id = str(ctx.author.id)
        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", member_id)

        cleverbot = ac.Cleverbot("W.UQ2.O[ewxop*;3M'qa") # Create the Cleverbot client
        await ctx.reply("Started a chat, type `closechat` to end the conversation.\nHow it work? Just, talk with me as much more time you can:\n- **`> or = at 60 seconds`** = from __100__ to __1200__ coins (random).\n- **`between 60 & 120 seconds`** = from __400__ to __2300__ coins (random)\n- **`= or > of 120 seconds`** = from __1600__ to __12000__ coins (random)\n(You can't start the chat and not type, after 1 minute without messages, the chat will be automatically closed.)")
        start = time.time()

        while True:
            try:
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel, timeout=60.0)
            except asyncio.TimeoutError:
                end = time.time()
                tot = end - start

                if tot <= 60:
                    earn = random.randint(100, 1000)
                elif tot <= 5:
                    earn = random.randint(1, 5)
                elif tot >= 60 and tot <= 120:
                    earn = random.randint(400, 2300)
                elif tot >= 120:
                    earn = random.randint(1600, 12000)

                await ctx.send(f"**{ctx.author.name}**, ending your chat with me because you didn't send a message for `1 minute`.\nYou talked with me for **`{round(tot)} seconds`**, so you got **`{earn} coins`**, but because you ran out of time, the earn will be the half of the half of the total, so you got **`{round(earn/4)}`** coins!")
                await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", user["bank"] +1*earn/4, member_id)
                return await cleverbot.close()

            if msg.content == "closechat":
                end = time.time()
                tots = end-start

                if tots <= 60:
                    earn = random.randint(100, 1000)
                elif tots <= 5:
                    earn = random.randint(1, 5)
                elif tots >= 60 and tots <= 120:
                    earn = random.randint(400, 2300)
                elif tots >= 120:
                    earn = random.randint(1600, 12000)

                await msg.reply(f"Closing the chat, also you talked with me for **`{round(tots)} seconds`**, so you got **`{round(earn)} coins as a reward!`**")
                await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", user["bank"] +1*earn, member_id)
                return await cleverbot.close()
            else:
                response = await cleverbot.ask(msg.content)
                await msg.reply(response.text)



    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == "<@!801742991185936384>" and not message.author.bot:
            await message.add_reaction("<:AtriYES:819739315579912203>")

        if message.content.startswith("::") and not message.author.bot:
            lists = []
            msg = message.content.replace(" ", "")
            emojis = msg.split("::")
            for i in emojis:
                if i == "":
                    continue
                e = finder(i, self.bot.emojis, key=lambda i: i.name, lazy=False)
                if e == []:
                    continue
                e = e[0]
                if e is None or emojis == []:
                    continue
                if e.is_usable() != False:
                    lists.append(str(e))
            if lists != []:
                try:
                    message_ = await message.channel.send("".join(lists))
                except:
                    pass

    @commands.command(help="See all the emojis ami can see")
    async def emojis(self, ctx, *, search: str = None):
        lists = []
        paginator = WrappedPaginator(max_size=1000, prefix="", suffix="")
        if search != None:
            emojis = finder(search,
                            self.bot.emojis,
                            key=lambda i: i.name,
                            lazy=False)
            if emojis == []:
                return await ctx.send("0 emojis with this name or similar names.")
            for i in emojis:
                if i.animated == True:
                    lists.append(f"{str(i)} | `{i.id}` | **{i.name}**")
                else:
                    lists.append(f"{str(i)} | `{i.id}` | **{i.name}**")
            paginator.add_line("\n".join(lists))
            interface = PaginatorEmbedInterface(ctx.bot,
                                           paginator,
                                           owner=ctx.author)
            return await interface.send_to(ctx)
        for i in self.bot.emojis:
            if i.animated == True:
                lists.append(f"{str(i)} | `{i.id}` | **{i.name}**")
            else:
                lists.append(f"{str(i)} | `{i.id}` | **{i.name}**")
        paginator.add_line("\n".join(lists))
        interface = PaginatorEmbedInterface(ctx.bot, paginator, owner=ctx.author)
        await interface.send_to(ctx)


class PaginatorEmbedInterface(PaginatorInterface):

    def __init__(self, *args, **kwargs):
        self._embed = discord.Embed()
        super().__init__(*args, **kwargs)

    @property
    def send_kwargs(self) -> dict:
        display_page = self.display_page
        self._embed.description = f"{self.pages[display_page]}"
        self._embed.set_footer(text=f'Page {display_page + 1}/{self.page_count}')
        return {'embed': self._embed}

    max_page_size = 2048

    @property
    def page_size(self) -> int:
        return self.paginator.max_size

        

def setup(bot):
    bot.add_cog(Fun(bot))
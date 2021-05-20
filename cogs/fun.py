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
import re
from discord_markdown.discord_markdown import convert_to_html
from PIL import Image,ImageDraw, ImageFont
from cogsf.fuzzy import finder
import async_cleverbot as ac
from urllib.parse import urlencode
from urllib.request import urlretrieve
import aiohttp
import requests
from io import BytesIO
import kitsu


kitsu_client = kitsu.Client()


def ship_func(pfp: discord.Member, pfp2: discord.Member = None):
    with Image.open("assets/bg.png") as bg:

        with Image.open(pfp).convert("RGBA") as pfp_1:
            image1 = pfp_1.resize((531,487))
            bg.paste(image1,(24,572), image1)
            image1.close()


        with Image.open(pfp2).convert("RGBA") as pfp_2:
            image2 = pfp_2.resize((537,461))
            bg.paste(image2,(1359,18), image2)
            image2.close()

        with Image.open("assets/heart.png") as heart:
            image3 = heart.resize((700, 500))
            bg.paste(image3,(640, 350), image3)
            image3.close()

        font = ImageFont.truetype("fonts/love.ttf", 180)
        draw = ImageDraw.Draw(bg)
        perc = random.randint(1, 100)
        text = f"{perc}%"
        x, y = 840, 518
        fillcolor = "pink"
        shadowcolor = "black"

        # thin border
        draw.text((x-1, y), text, font=font, fill=shadowcolor)
        draw.text((x+1, y), text, font=font, fill=shadowcolor)
        draw.text((x, y-1), text, font=font, fill=shadowcolor)
        draw.text((x, y+1), text, font=font, fill=shadowcolor)

        # thicker border
        draw.text((x-1, y-1), text, font=font, fill=shadowcolor)
        draw.text((x+1, y-1), text, font=font, fill=shadowcolor)
        draw.text((x-1, y+1), text, font=font, fill=shadowcolor)
        draw.text((x+1, y+1), text, font=font, fill=shadowcolor)

        draw.text((x, y), text, font=font, fill=fillcolor)

        buffer = BytesIO()
        bg.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afks = {}
        self.category = "Fun"


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Fun Loaded")

    @commands.command(help="Set a custom reminder, and get pinged when it's time!\nExample usage: **ami remind 1s hi** - 1s = <time>, 'hi' = [message]")
    async def remind(self, ctx, time, *, message=None):
        if message == None:
            message = ". . ."

        if message == "@everyone":
            message = ". . ."

        if message == "@here":
            message = ". . ."
            
        def convert(time):
            pos = ['s', 'm', 'h', 'd']

            time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600*24}

            unit = time[-1]

            if unit not in pos:
                return -1
            try:
                val = int(time[:-1])
            except:
                return -2
            
            return val * time_dict[unit]
        
        converted_time = convert(time)

        if converted_time == -1:
            return await ctx.reply("Time unit not valid, valid units are: `s`, `m`, `h`, `d`.")

        if converted_time == -2:
            return await ctx.reply("Time not valid.")

        time_format = ""
        ttt = time[-1]
        abc = time[:-1]
        if ttt == "s":
            if int(abc) <= 1:
                time_format = "second"
            else:
                time_format = "seconds"
        elif ttt == "m":
            if int(abc) <= 1:
                time_format = "minute"
            else:
                time_format = "minutes"
        elif ttt == "h":
            if int(abc) <= 1:
                time_format = "hour"
            else:
                time_format = "hours"
        elif ttt == "d":
            if int(abc) <= 1:
                time_format = "day"
            else:
                time_format = "days"

        final_time = f"{time[:-1]} " + time_format

        await ctx.reply(f"Alright {ctx.author.mention}, in {final_time}: {message}")
        date_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=converted_time)
        await discord.utils.sleep_until(date_time)
        await ctx.send(f"{ctx.author.mention}, {final_time} ago: {message}\n{ctx.message.jump_url}")


    @commands.command(help="Start a simple counting game!")
    @commands.max_concurrency(1, BucketType.channel)
    async def count(self, ctx):
        await ctx.send("Counting game started! First number is **`1`**!")
        author_id = ""
        num = 0
        while True:
            mex = await self.bot.wait_for('message', check=lambda m: not m.author.bot and m.channel == ctx.channel)
            if mex.content.isdigit():
                if mex.content == str(num+1):
                    if str(mex.author.id) == author_id:
                        await ctx.send(f"{mex.author.mention} has __cheated__, trying to count **two times** in row.")
                        break
                    num += 1
                    author_id = str(mex.author.id)
                    await mex.add_reaction("<a:pepesmoke:820747996106326047>")
                else:
                    await ctx.send(f"{mex.author.mention} failed! Stopped at **`{num}`**, send `ami count` to restart the game.")
                    break


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

        if len(reason) > 40:
            return await ctx.reply(":x: The reason must be less than **40** letters.")

        await ctx.send(f"<:KannaSip:819739316502134805> **{ctx.author.name}** i've set your afk for:  {reason}")
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
            await message.channel.send(f"<:nezyay:819703490078834729> Welcome back {message.author.mention}, i've removed your **AFK** status.")
            del self.afks[ids]

        try:
            id2 = message.mentions[0].id
        except IndexError:
            id2 = "None"
        if id2 in self.afks.keys():
            reasons = self.afks[id2]
            return await message.channel.send(f'<:nani:819694934491004937> {message.author.mention}, **{str(message.mentions[0].name)}** is afk for: {reasons}')


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
    async def reactspeed(self, ctx, number:float):
        if number > 20.0:
            em = discord.Embed(description="<:alert:819704994612904017> Time can't be over 20.0 seconds.")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return
            
        if number < 0.1:
            em = discord.Embed(description="<:alert:819704994612904017> Time can't be < 0.1 second.")
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
        embed=discord.Embed(title=f"{number} second(s) reaction",description=f"<:vea:819703490703523860> Your result is: `{round(end-start, 5)}` seconds", color=0xffcff1)
        embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
        await message.edit(embed=embed)


    @commands.command(help="Get the invite link for ami")
    async def invite(self, ctx, perms=None):
        link = ""
        prms = ["basic", "advanced", "admin"]
        s = ", ".join(prms)
        if perms == None:
            return await ctx.reply(f"`ami invite <perms>`: ehm dude, please specify with which perms, available perms are:\n{s}")

        if perms in prms:
            if perms == "basic":
                link = "[click here to invite me with basic perms](https://discord.com/oauth2/authorize?client_id=801742991185936384&scope=bot&permissions=1077267521)"
            elif perms == "advanced":
                link = "[click here to invite me with advanced perms](https://discord.com/oauth2/authorize?client_id=801742991185936384&scope=bot&permissions=1345711607)"
            elif perms == "admin":
                link = "[click here to invite me with admin perms](https://discord.com/oauth2/authorize?client_id=801742991185936384&scope=bot&permissions=8)"

        em = discord.Embed(description=f"{link}", color = 0xffcff1)
        await ctx.send(embed=em)



    @commands.command(help="Ship two members between themself, and get the love percentage!\nYou can ship yourself with another member sending the `<member>`, without `[member2]`.")
    async def ship(self, ctx, member: discord.Member, member2: discord.Member = None):
        if member2:
            pfp = member
            pfp2 = member2
        else:
            pfp = ctx.author
            pfp2 = member

        if member == ctx.author:
            return await ctx.reply(":x: **You can't ship you with yourself.**")

        if member == member2:
            return await ctx.reply(":x: **You can't ship a member with itself.**")

        if member2 == member:
            return await ctx.reply(":x: **You can't ship a member with itself.**")

        #get the first mention avatar
        asset1 = pfp.avatar_url_as(size=512)
        pfp= BytesIO(await asset1.read())
                
        #get the second mention avatar
        asset2 = pfp2.avatar_url_as(size=512)
        pfp2= BytesIO(await asset2.read())
        
        buffer = await self.bot.loop.run_in_executor(None, ship_func, pfp, pfp2)
        file=discord.File(fp=buffer, filename="ship.png")
        em = discord.Embed(color=0xffcff1)
        em.set_image(url="attachment://ship.png")
        em.set_footer(text="Donate to support me and my developers!", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em, file=file)


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
        cwebp = str(member.avatar_url)

        png = f"[`PNG`]({cpng})"
        jpg = f"[`JPG`]({cjpg})"
        jpeg = f"[`JPEG`]({cjpeg})"
        gif = f"[`GIF`]({cgif})"
        webp = f"[`WEBP`]({cwebp})"

        em = discord.Embed(title=f"{member.name}'s avatar!",description=f"{png} | {jpg} | {jpeg} | {gif} | {webp}", color = 0xffcff1)
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
        d = discord.Embed(title=f":busts_in_silhouette: **Member Count**", description = f"\n<:user:819703150755577856> *Total*  »  `{a}`\n<:thumbsup:819703492481908776> *Humans*  »  `{c}`\n<:1739_CMD:819689870393999380> *Bots*  »  `{b}`", color=discord.Color(0xffff00))
        await ctx.send(embed=d)


# Ping & Pong
    @commands.command(help="Check the latency",pass_context=True)
    async def ping(self, ctx):
        websocket = round(self.bot.latency*1000, 2)
        await ctx.send(f"<:babyyay:839518621352460289> `{websocket}`ms")

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


    @commands.command(help="Convert the discord markdown into html format")
    async def html(self, ctx, *, args):
        html = convert_to_html(args)
        em = discord.Embed(description = f"```\n{html}\n```", color = 0x2F3136)
        await ctx.send(embed=em)

    @commands.command(help="Search an anime and retrive some useful info about that.", aliases=["sa"])
    async def searchanime(self, ctx, *, animename):
        anime = await kitsu_client.search('anime', animename)
        if not anime:
            return await ctx.reply(f'<:redTick:596576672149667840> Nothing found for **{animename}**.')

        slink = await kitsu_client.fetch_anime_streaming_links(anime[0])
        if slink:
            link = slink[0].url
        else:
            link = "https://no.links.found.for.your.query..don't.click.this.link..that's.useless"
        
        syno = anime[0].synopsis.strip("(Source: MAL Rewrite)")
        syno = anime[0].synopsis.strip("[Written by MAL Rewrite]")
        em = discord.Embed(title=f"{anime[0].title}", url=f"{link}", description=f"{syno}", color=0xffcff1)
        em.set_thumbnail(url=anime[0].poster_image_url)
        em.set_footer(text=f"Episodes: {anime[0].episode_count} | Satus: {anime[0].status.title()} | Nsfw: {anime[0].nsfw} | {anime[0].age_rating_guide}")
        em.set_author(name=f"{anime[0].started_at.strftime('%Y-%m-%d')} - {anime[0].ended_at.strftime('%Y-%m-%d')} | Rank: #{anime[0].popularity_rank}")
        await ctx.reply(embed=em, mention_author=False)

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
                await msg.reply(response.text.lower())



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
        

def setup(bot):
    bot.add_cog(Fun(bot))

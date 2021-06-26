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
from io import BytesIO
import kitsu
from aiogtts import aiogTTS
import string
import os
import randfacts

kitsu_client = kitsu.Client()

class GayMeter:
    def gaymeter_func(pfp: discord.Member, perc:int):
        with Image.open("assets/gaymeter.png") as bg:

            x, y = 134, 576

            for i in range(perc):
                y -= 6

            with Image.open(pfp).convert("RGBA") as pfp_1:
                im = pfp_1.resize((100, 100))
                bigsize = (im.size[0] * 3, im.size[1] * 3)
                mask = Image.new('L', bigsize, 0)
                draw = ImageDraw.Draw(mask) 
                draw.ellipse((0, 0) + bigsize, fill=255)
                mask = mask.resize(im.size, Image.ANTIALIAS)
                im.putalpha(mask)
                bg.paste(im,(x, y),im)
                im.close()

            buffer = BytesIO()
            bg.save(buffer, format="PNG")
            buffer.seek(0)

            return buffer

class Ship:
    def ShipBar(d, x, y, w, h, progress, fg="#FFB6C1"):

        w *= progress
        d.ellipse((x+w, y, x+h+w, y+h),fill=fg)
        d.ellipse((x, y, x+h, y+h),fill=fg)
        d.rectangle((x+(h/2), y, x+w+(h/2), y+h),fill=fg)

        return d


    def ship_func(perc:int, pfp: discord.Member, pfp2: discord.Member = None):
        with Image.open("assets/ship_banner.png") as bg:

            with Image.open(pfp).convert("RGBA") as pfp_1:
              im = pfp_1.resize((255, 258))
              bigsize = (im.size[0] * 3, im.size[1] * 3)
              mask = Image.new('L', bigsize, 0)
              draw = ImageDraw.Draw(mask) 
              draw.ellipse((0, 0) + bigsize, fill=255)
              mask = mask.resize(im.size, Image.ANTIALIAS)
              im.putalpha(mask)
              bg.paste(im,(65,25),im)
              im.close()


            with Image.open(pfp2).convert("RGBA") as pfp_2:
              im = pfp_2.resize((260, 258))
              bigsize = (im.size[0] * 3, im.size[1] * 3)
              mask = Image.new('L', bigsize, 0)
              draw = ImageDraw.Draw(mask) 
              draw.ellipse((0, 0) + bigsize, fill=255)
              mask = mask.resize(im.size, Image.ANTIALIAS)
              im.putalpha(mask)
              bg.paste(im,(972,22),im)
              im.close()

            sparky = 0.00
            x_sparky = int(perc/100)
            d = 0
            f = x_sparky
            for i in range(100):
                d += 1
                sparky += 0.01
                x_sparky += f
                if d >= perc:
                    break

            d = ImageDraw.Draw(bg)
            d = Ship.ShipBar(d, 380, 212, 500, 40, sparky)

            font = ImageFont.truetype("fonts/love.ttf", 180)
            draw = ImageDraw.Draw(bg)
            text = f"{perc}%"
            x, y = 640, 150
            fillcolor = "pink"
            shadowcolor = "black"

            # thin border
            draw.text((x-1, y), text, font=font, fill=shadowcolor, anchor="mm")
            draw.text((x+1, y), text, font=font, fill=shadowcolor, anchor="mm")
            draw.text((x, y-1), text, font=font, fill=shadowcolor, anchor="mm")
            draw.text((x, y+1), text, font=font, fill=shadowcolor, anchor="mm")

            # thicker border
            draw.text((x-1, y-1), text, font=font, fill=shadowcolor, anchor="mm")
            draw.text((x+1, y-1), text, font=font, fill=shadowcolor, anchor="mm")
            draw.text((x-1, y+1), text, font=font, fill=shadowcolor, anchor="mm")
            draw.text((x+1, y+1), text, font=font, fill=shadowcolor, anchor="mm")

            draw.text((x, y), text, font=font, fill=fillcolor, anchor="mm")

            buffer = BytesIO()
            bg.save(buffer, format="PNG")
            buffer.seek(0)

            return buffer

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afks = {}
        self.languages = {}
        self.category = "Fun"
        bot.loop.create_task(self.cache_langs())
    
    async def cache_langs(self):
        await self.bot.wait_until_ready()
        db = await self.bot.pg_con.fetch("SELECT * FROM tts")
        for i in db:
            if i["language"]:
                self.languages[i["guild_id"]] = i["language"]

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Fun Loaded")

    @commands.command(help="Get a random fact, you can also pass some arguments to retrive innapropriate facts (they are excluded by default), or exclude them, e.g:\n`ami fact --unsafe` to retrive inappropriate facts.")
    async def fact(self, ctx, flags=None):
        if flags:
            if flags == "--unsafe":
                x = randfacts.getFact(only_unsafe=True)
                return await ctx.reply(x, mention_author=False)

        x = randfacts.getFact()
        return await ctx.reply(x, mention_author=False)

    @commands.command(help="An advanced gay calculator to calculate how much gay is a member >.> (Joking, is just a random percentage)", aliases=["gay"])
    async def gaymeter(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        asset = member.avatar_url_as(size=512)
        pfp = BytesIO(await asset.read())
        
        perc = random.randint(1, 100)

        buffer = await self.bot.loop.run_in_executor(None, GayMeter.gaymeter_func, pfp, perc)
        file=discord.File(fp=buffer, filename="gaymeter.png")
        return await ctx.send(file=file)

    @commands.command(help="Create a text to speech file with the given query, and make it send in the chat!\n\n`ami tts setlang` to set the default tts language for the guild.\n`ami tts lang` to check the language set.", aliases=["tts"])
    async def texttospeech(self, ctx: commands.Context, *, query:str):
        if query.lower() == "setlang":
            if not ctx.author.guild_permissions.manage_channels:
                return await ctx.send("<:4318crossmark:848857812565229601> You don't have `Manage Channels` permissions to run this command.")

            await ctx.send("<:4430checkmark:848857812632076314> Now send the language code you want to set as default (examples: `it`, `en`, `fr`.)")

            try:
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel)
            except asyncio.TimeoutError:
                return

            await self.bot.pg_con.execute("INSERT INTO tts (guild_id, language) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET language = $2", ctx.guild.id, msg.content.lower())
            self.languages[ctx.guild.id] = msg.content.lower()
            return await msg.add_reaction("<:4430checkmark:848857812632076314>")

        if query.lower() == "lang":
            if ctx.guild.id not in self.languages:
                return await ctx.send("<:4318crossmark:848857812565229601> This guild has not a language set for tts, set one with `ami tts setlang`.")

            em = discord.Embed(description=f"<:4430checkmark:848857812632076314> TTS language for this guild is `{self.languages[ctx.guild.id]}`", color = 0xffcff1)
            return await ctx.send(embed=em)

        if ctx.guild.id not in self.languages:
            return await ctx.send("<:4318crossmark:848857812565229601> This guild has not a language set for tts, set one with `ami tts setlang`.")

        if len(query) > 500:
            return await ctx.send(f"<:4318crossmark:848857812565229601> The text given is **{len(query)}** characters, max is **500**.")

        aiogtts = aiogTTS()
        lang = self.languages[ctx.guild.id]

        d = string.ascii_letters+string.digits
        keylist = [random.choice(d) for i in range(10)]
        f = "".join(keylist)

        try:
            await aiogtts.save(query, f"{f}.mp3", lang=lang)
        except Exception:
            os.remove(f"{f}.mp3")
            return await ctx.send(f"<:4318crossmark:848857812565229601> `{lang}` is not a valid language code, e.g: `it`, `en`, `fr`.")

        await ctx.send(file=discord.File(f"{f}.mp3"))
        return os.remove(f"{f}.mp3")

    @commands.command(help="Set a custom reminder, and get pinged when it's time!\nExample usage: **ami remind 1s hi** - 1s = <time>, 'hi' = [message]\nYou can't delete a reminder set.")
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


    @commands.command(help="Start a simple counting game in the channel where you use this command!\n\n`ami count` to start a normal counting game\n`ami count --m-a` to start a game where wrong messages will not stop the game\n`ami count --r @members` to start a game where only messages from members mentioned will be counted\n`ami count --r-m-a @members` same as `--r` but with messages allowed\n`ami count --d-w` to start a game where all wrong messages will be deleted\n\nYou can see the counting stats for the guild with `ami count stats`, `ami count score` or `ami count restarts`.")
    @commands.max_concurrency(1, BucketType.channel)
    async def count(self, ctx, option=None, whitelist: commands.Greedy[discord.Member]=None):
        if option:
            if option == "stats":
                db = await self.bot.pg_con.fetch("SELECT * FROM counting WHERE guild_id = $1", str(ctx.guild.id))
                if not db:
                    return await ctx.send("<:redTick:596576672149667840> This guild has no __stats__ registered, play a counting game before.")

                higher_score = db[0]["higher_score"]
                restarts = db[0]["restarts"]
                
                em = discord.Embed(title=f"Counting Stats", color = 0xffcff1)
                em.set_author(name=f"{ctx.guild.name}", icon_url=ctx.guild.icon_url)
                em.add_field(name="<:7343exclamationmark:848857813252833290> Higher Score", value=f"<a:4484pinkarrow:848857813085716520> The higher score registered for this guild is : **{higher_score}**")
                em.add_field(name="<:7343exclamationmark:848857813252833290> Restarts", value=f"<a:4484pinkarrow:848857813085716520> The counting game in this guild has been restarted : **{restarts}** times.")
                return await ctx.send(embed=em)

            elif option == "score":
                db = await self.bot.pg_con.fetch("SELECT * FROM counting WHERE guild_id = $1", str(ctx.guild.id))
                if not db:
                    return await ctx.send("<:redTick:596576672149667840> This guild has no __stats__ registered, play a counting game before.")

                higher_score = db[0]["higher_score"]
                return await ctx.send(f"<:5324_letters:848857812577812511> Higher counting score in this guild is **{higher_score}**")

            elif option == "restarts":
                db = await self.bot.pg_con.fetch("SELECT * FROM counting WHERE guild_id = $1", str(ctx.guild.id))
                if not db:
                    return await ctx.send("<:redTick:596576672149667840> This guild has no __stats__ registered, play a counting game before.")

                restarts = db[0]["restarts"]
                return await ctx.send(f"<:5324_letters:848857812577812511> The counting game was restarted **{restarts}** times.")
            
            elif option == "--m-a":
                await ctx.send("<:greenTick:596576670815879169> Counting game __started__ with `messages allowed` mode, good luck!")
                author_id = ""
                num = 0
                while True:
                    mex = await self.bot.wait_for('message', check=lambda m: not m.author.bot and m.channel == ctx.channel)
                    if mex.content.isdigit():
                        if mex.content == str(num+1):
                            if str(mex.author.id) == author_id:
                                await mex.add_reaction("<:4318crossmark:848857812565229601>")
                                await ctx.send(f"<:redTick:596576672149667840> {mex.author.mention} has sent __two__ numbers, `ami count --m-a` to restart with messages allowed.")
                                db = await self.bot.pg_con.fetch("SELECT * FROM counting WHERE guild_id = $1", str(ctx.guild.id))
                                if not db:
                                    await self.bot.pg_con.execute("INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)", str(ctx.guild.id), num, 1)
                                
                                final_score = 0
                                if db[0]["higher_score"] > num:
                                    final_score = db[0]["higher_score"]
                                else:
                                    final_score = num
                                
                                await self.bot.pg_con.execute("UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3", final_score, db[0]["restarts"] + 1, str(ctx.guild.id))
                                break
                            num += 1
                            author_id = str(mex.author.id)
                            await mex.add_reaction("<:4430checkmark:848857812632076314>")
                        else:
                            await mex.add_reaction("<:4318crossmark:848857812565229601>")
                            await ctx.send(f"<:redTick:596576672149667840> {mex.author.mention} failed! Stopped at **`{num}`**, send `ami count --m-a` to restart the game with messages allowed.")
                            db = await self.bot.pg_con.fetch("SELECT * FROM counting WHERE guild_id = $1", str(ctx.guild.id))
                            if not db:
                                await self.bot.pg_con.execute("INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)", str(ctx.guild.id), num, 1)
                            
                            final_scoree = 0
                            if db[0]["higher_score"] > num:
                                final_scoree = db[0]["higher_score"]
                            else:
                                final_scoree = num 
                            
                            await self.bot.pg_con.execute("UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3", final_scoree, db[0]["restarts"] + 1, str(ctx.guild.id))
                            break

            elif option == "--r":
                if not whitelist:
                    return await ctx.send("<:4318crossmark:848857812565229601> You need to specify the `[whitelist]` argument for this mode, check `ami help count` to know more.")
                
                if len(whitelist) > 10:
                    return await ctx.send(f"<:4318crossmark:848857812565229601> Restrict mode has a max. of 10 players, you have passed {len(whitelist)} players.")
                
                if len(whitelist) < 2:
                    return await ctx.send("<:4318crossmark:848857812565229601> At least 2 players needed to start the game in restricted mode.")

                if ctx.author not in whitelist:
                    return await ctx.send("<:4318crossmark:848857812565229601> You can't start a restriced counting game without you in.")

                d = []
                for s in whitelist:
                    id = s.id
                    user = self.bot.get_user(id) or (await self.bot.fetch_user(id))
                    if user.bot:
                        return await ctx.send(f"<:4318crossmark:848857812565229601> {user.mention} is a bot, it can't play counting.")
                    d.append(user.mention)

                dcv = " | ".join(d)

                await ctx.send(f"<:greenTick:596576670815879169> Counting game __started__ with `restricted` mode ({dcv}), good luck!")
                author_id = ""
                num = 0
                while True:
                    mex = await self.bot.wait_for('message', check=lambda m: not m.author.bot and m.channel == ctx.channel)
                    
                    s = []
                    for i in whitelist:
                        id = i.id
                        s.append(id)
                    
                    if mex.author.id in s:
                        if mex.content == str(num+1):
                            if str(mex.author.id) == author_id:
                                await mex.add_reaction("<:4318crossmark:848857812565229601>")
                                await ctx.send(f"<:redTick:596576672149667840> {mex.author.mention} has sent __two__ numbers, `ami count --r @members` to restart.")
                                db = await self.bot.pg_con.fetch("SELECT * FROM counting WHERE guild_id = $1", str(ctx.guild.id))
                                if not db:
                                    await self.bot.pg_con.execute("INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)", str(ctx.guild.id), num, 1)
                                    
                                final_score = 0
                                if db[0]["higher_score"] > num:
                                    final_score = db[0]["higher_score"]
                                else:
                                    final_score = num
                                    
                                await self.bot.pg_con.execute("UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3", final_score, db[0]["restarts"] + 1, str(ctx.guild.id))
                                break
                            num += 1
                            author_id = str(mex.author.id)
                            await mex.add_reaction("<:4430checkmark:848857812632076314>")
                        else:
                            await mex.add_reaction("<:4318crossmark:848857812565229601>")
                            await ctx.send(f"<:redTick:596576672149667840> {mex.author.mention} failed! Stopped at **`{num}`**, send `ami count --r @members` to restart the restricted game.")
                            db = await self.bot.pg_con.fetch("SELECT * FROM counting WHERE guild_id = $1", str(ctx.guild.id))
                            if not db:
                                await self.bot.pg_con.execute("INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)", str(ctx.guild.id), num, 1)
                                
                            final_scoree = 0
                            if db[0]["higher_score"] > num:
                                final_scoree = db[0]["higher_score"]
                            else:
                                final_scoree = num 
                                
                            await self.bot.pg_con.execute("UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3", final_scoree, db[0]["restarts"] + 1, str(ctx.guild.id))
                            break
                    else:
                        pass

            elif option == "--r-m-a":
                if not whitelist:
                    return await ctx.send("<:4318crossmark:848857812565229601> You need to specify the `[whitelist]` argument for this mode, check `ami help count` to know more.")
                
                if len(whitelist) > 10:
                    return await ctx.send(f"<:4318crossmark:848857812565229601> Restrict mode has a max. of 10 players, you have passed {len(whitelist)} players.")
                
                if len(whitelist) < 2:
                    return await ctx.send("<:4318crossmark:848857812565229601> At least 2 players needed to start the game in restricted mode.")

                if ctx.author not in whitelist:
                    return await ctx.send("<:4318crossmark:848857812565229601> You can't start a restriced counting game without you in.")

                d = []
                for s in whitelist:
                    id = s.id
                    user = self.bot.get_user(id) or (await self.bot.fetch_user(id))
                    if user.bot:
                        return await ctx.send(f"<:4318crossmark:848857812565229601> {user.mention} is a bot, it can't play counting.")
                    d.append(user.mention)

                dcv = " | ".join(d)

                await ctx.send(f"<:greenTick:596576670815879169> Counting game __started__ with `restricted` mode ({dcv}), good luck!")
                author_id = ""
                num = 0
                while True:
                    mex = await self.bot.wait_for('message', check=lambda m: not m.author.bot and m.channel == ctx.channel)
                    
                    s = []
                    for i in whitelist:
                        id = i.id
                        s.append(id)

                    if mex.content.isdigit():
                        if mex.author.id in s:
                            if mex.content == str(num+1):
                                if str(mex.author.id) == author_id:
                                    await mex.add_reaction("<:4318crossmark:848857812565229601>")
                                    await ctx.send(f"<:redTick:596576672149667840> {mex.author.mention} has sent __two__ numbers, `ami count --r-m-a @members` to restart.")
                                    db = await self.bot.pg_con.fetch("SELECT * FROM counting WHERE guild_id = $1", str(ctx.guild.id))
                                    if not db:
                                        await self.bot.pg_con.execute("INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)", str(ctx.guild.id), num, 1)
                                        
                                    final_score = 0
                                    if db[0]["higher_score"] > num:
                                        final_score = db[0]["higher_score"]
                                    else:
                                        final_score = num
                                        
                                    await self.bot.pg_con.execute("UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3", final_score, db[0]["restarts"] + 1, str(ctx.guild.id))
                                    break
                                num += 1
                                author_id = str(mex.author.id)
                                await mex.add_reaction("<:4430checkmark:848857812632076314>")
                            else:
                                await mex.add_reaction("<:4318crossmark:848857812565229601>")
                                await ctx.send(f"<:redTick:596576672149667840> {mex.author.mention} failed! Stopped at **`{num}`**, send `ami count --r-m-a @members` to restart the restricted game.")
                                db = await self.bot.pg_con.fetch("SELECT * FROM counting WHERE guild_id = $1", str(ctx.guild.id))
                                if not db:
                                    await self.bot.pg_con.execute("INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)", str(ctx.guild.id), num, 1)
                                    
                                final_scoree = 0
                                if db[0]["higher_score"] > num:
                                    final_scoree = db[0]["higher_score"]
                                else:
                                    final_scoree = num 
                                    
                                await self.bot.pg_con.execute("UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3", final_scoree, db[0]["restarts"] + 1, str(ctx.guild.id))
                                break
                    else:
                        pass

            elif option == "--d-w":
                if not ctx.guild.me.guild_permissions.manage_messages:
                    return await ctx.send("<:4318crossmark:848857812565229601> I need the `Manage Messages` permission to run this mode of counting.")
                
                await ctx.send("<:greenTick:596576670815879169> Counting game __started__ with `delete wrong` mode, send `ami stopcount` to stop it, good luck!")
                author_id = ""
                num = 0
                while True:
                    mex = await self.bot.wait_for('message', check=lambda m: not m.author.bot and m.channel == ctx.channel)
                    if mex.content == "ami stopcount":
                        await ctx.send("<:4430checkmark:848857812632076314> Counting game stopped succesfully!")
                        db = await self.bot.pg_con.fetch("SELECT * FROM counting WHERE guild_id = $1", str(ctx.guild.id))
                        if not db:
                            await self.bot.pg_con.execute("INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)", str(ctx.guild.id), num, 1)
                                        
                        final_score = 0
                        if db[0]["higher_score"] > num:
                            final_score = db[0]["higher_score"]
                        else:
                            final_score = num
                                        
                        await self.bot.pg_con.execute("UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3", final_score, db[0]["restarts"] + 1, str(ctx.guild.id))
                        break

                    elif mex.content == str(num+1):
                        if str(mex.author.id) == author_id:
                            await mex.delete()
                            continue
                        num += 1
                        author_id = str(mex.author.id)
                        await mex.add_reaction("<:4430checkmark:848857812632076314>")
                    else:
                        await mex.delete()
            else:
                return await ctx.send("<:redTick:596576672149667840> Invalid option provided, check `ami help count`.")
        else:
            await ctx.send("<:greenTick:596576670815879169> Counting game __started__, good luck!")
            author_id = ""
            num = 0
            while True:
                mex = await self.bot.wait_for('message', check=lambda m: not m.author.bot and m.channel == ctx.channel)
                if mex.content == str(num+1):
                    if str(mex.author.id) == author_id:
                        await mex.add_reaction("<:4318crossmark:848857812565229601>")
                        await ctx.send(f"<:redTick:596576672149667840> {mex.author.mention} has sent __two__ numbers, `ami count` to restart.")
                        db = await self.bot.pg_con.fetch("SELECT * FROM counting WHERE guild_id = $1", str(ctx.guild.id))
                        if not db:
                            await self.bot.pg_con.execute("INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)", str(ctx.guild.id), num, 1)
                            
                        final_score = 0
                        if db[0]["higher_score"] > num:
                            final_score = db[0]["higher_score"]
                        else:
                            final_score = num
                            
                        await self.bot.pg_con.execute("UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3", final_score, db[0]["restarts"] + 1, str(ctx.guild.id))
                        break
                    num += 1
                    author_id = str(mex.author.id)
                    await mex.add_reaction("<:4430checkmark:848857812632076314>")
                else:
                    await mex.add_reaction("<:4318crossmark:848857812565229601>")
                    await ctx.send(f"<:redTick:596576672149667840> {mex.author.mention} failed! Stopped at **`{num}`**, send `ami count` to restart the game.")
                    db = await self.bot.pg_con.fetch("SELECT * FROM counting WHERE guild_id = $1", str(ctx.guild.id))
                    if not db:
                        await self.bot.pg_con.execute("INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)", str(ctx.guild.id), num, 1)
                        
                    final_scoree = 0
                    if db[0]["higher_score"] > num:
                        final_scoree = db[0]["higher_score"]
                    else:
                        final_scoree = num 
                        
                    await self.bot.pg_con.execute("UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3", final_scoree, db[0]["restarts"] + 1, str(ctx.guild.id))
                    break



    @commands.command(help="Set your AFK mode globally (it means only where i can see you).\nAFK is a modality where when you are in, if someone pings you, ami will advice who pinged you, you are afk for `[reason]`.\nOtherwise, when you send a message in a channel / guild where i can see your messages, your afk mode will be deleted.")
    async def afk(self, ctx, *, reason=None):
        if reason == None:
            reason = "Not specified."

        if len(reason) > 100:
            return await ctx.reply(":x: The reason must be less than **100** letters.")

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

        if message.author.id in self.afks:
            ids = message.author.id
            await message.channel.send(f"<:nezyay:819703490078834729> Welcome back {message.author.mention}, i've removed your **AFK** status.")
            if ids in self.afks:
                del self.afks[ids]

        try:
            id2 = message.mentions[0].id
        except IndexError:
            id2 = "None"
        if id2 in self.afks.keys():
            reasons = self.afks[id2]
            return await message.channel.send(f'<:nani:819694934491004937> {message.author.mention}, **{str(message.mentions[0].name)}** is afk for: {reasons}')


    @commands.command(help="Choose between multiple choices.\nAdd quotemarks at the start & end of something to mark a long phrase as a possible choice, e.g: `ami choose sky \"watch anime\" netflix`")
    async def choose(self, ctx, *choices: str):
        choi = random.choice(choices)
        await ctx.send(choi, allowed_mentions = discord.AllowedMentions.none())

    @commands.command()
    async def source(self, ctx):
        await ctx.reply("I'm closed source.")

    @commands.command(help="Test your reaction timing with this simple, fast and addictive game based on your reaction speed!",aliases=["rspeed"])
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
        start2 = number + 5.0

        def check(payload):
            return payload.message_id == message.id and payload.emoji.name == "nono" and payload.user_id == ctx.author.id

        try: 
            await self.bot.wait_for("raw_reaction_add", check=check, timeout=start2)
        except asyncio.TimeoutError:
            return await ctx.send(f"<:alert:819704994612904017> No reaction detected from **{ctx.author.name}**.")

        end = time.time()
        embed=discord.Embed(title=f"{number} second(s) reaction",description=f"<:vea:819703490703523860> Your result is: `{round(end-start, 2)}` seconds", color=0xffcff1)
        embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
        await message.edit(embed=embed)


    @commands.command(help="Retrive the invite link to invite me in your guild / other guilds with different permissions availables!")
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
        avatar= BytesIO(await asset1.read())
                
        #get the second mention avatar
        asset2 = pfp2.avatar_url_as(size=512)
        avatar2= BytesIO(await asset2.read())

        perc = random.randint(1, 100)
        
        buffer = await self.bot.loop.run_in_executor(None, Ship.ship_func, perc, avatar, avatar2)
        file=discord.File(fp=buffer, filename="ship.png")

        mex = ""
        if perc <= 15 and perc >= 0:
            mex = f"😢 That's bad..\n<:zerotwoheart:852924089240125480> **{pfp.name}** & **{pfp2.name}**"
        elif perc >= 15 and perc <= 30:
            mex = f"😯 Nothing special as i can see..\n<:zerotwoheart:852924089240125480> **{pfp.name}** & **{pfp2.name}**"
        elif perc >= 30 and perc <= 50:
            mex = f"☺ Maybe something..\n<:zerotwoheart:852924089240125480> **{pfp.name}** & **{pfp2.name}**"
        elif perc >= 50 and perc <= 75:
            mex = f"🤩 This is good!!\n<:zerotwoheart:852924089240125480> **{pfp.name}** & **{pfp2.name}**"
        elif perc >= 75 and perc <= 99:
            mex = f"😍 WOAH! That's a ship.\n<:zerotwoheart:852924089240125480> **{pfp.name}** & **{pfp2.name}**"
        elif perc > 99:
            mex = f"🎉✨🎉 THEY'RE MARRIED!! 🎉✨🎉\n**{pfp.name}** & **{pfp2.name}**"

        await ctx.send(mex, file=file)


    @commands.command(help="Evaluate an expression, it's accepts float / int numbers.\nSupported calculation are:\n`/` = division\n`*` = multiplication\n`+` = addition\n`-` = subtraction\n`**` = power", aliases=["calc", "math", "expr"])
    async def calculate(self, ctx, *, expression:str):
        try:
            calculation = simpleeval.simple_eval(expression)

            if len(str(calculation)) > 30:
                await ctx.send("<:4318crossmark:848857812565229601> Result is too long to be displayed")
                return

            if str(expression) == "...":
                await ctx.send("<:4318crossmark:848857812565229601> Are you sure this is a valid expression?")
                return

            await ctx.reply(f"<:4430checkmark:848857812632076314> {expression} = {calculation}")
            

        except simpleeval.NameNotDefined:
            await ctx.send("<:4318crossmark:848857812565229601> Baka.")
            return

        except simpleeval.FeatureNotAvailable:
            await ctx.send("<:4318crossmark:848857812565229601> Idiot.")
            return

        except ZeroDivisionError:
            await ctx.send(f"{expression} = 0")
            return

        except IndexError:
            await ctx.send("<:4318crossmark:848857812565229601> Dumbass.")
            return

        except SyntaxError:
            await ctx.send("<:4318crossmark:848857812565229601> Typo?")
            return

        except simpleeval.FunctionNotDefined:
            await ctx.send("<:4318crossmark:848857812565229601> What's that?")
            return

        except simpleeval.NumberTooHigh:
            await ctx.send("<:4318crossmark:848857812565229601> Number too high.")
            return

    @commands.command(help="Get a valid nitro gift and swag with your friend telling them you got free nitro!")
    async def nitro(self, ctx):
        await ctx.send("https://pics.me.me/thumb_when-youre-broke-so-you-make-your-own-nitro-boost-69569902.png")


    @commands.command(help="Get a member avatar",pass_context=True, aliases=["av"])
    async def avatar(self, ctx, member:discord.Member=None):
        if member == None:
            member = ctx.author

        await ctx.send(member.avatar_url)


 # Members Counter Command
    @commands.command(help="Retrive a detailed member count for the guild, separated in `total members`, `people` and `bots`.", aliases=["mc"])
    async def membercount(self, ctx):
        a = ctx.guild.member_count
        b = len([m for m in ctx.guild.members if (m.bot)])
        c = len([m for m in ctx.guild.members if not m.bot])
        await ctx.send(f"<:4430checkmark:848857812632076314> I can see **{a}** total members in this guild, which **{c}** are people and **{b}** bots.")


# Ping & Pong
    @commands.command(help="Check the latency of the discord websocket.",pass_context=True)
    async def ping(self, ctx):
        websocket = round(self.bot.latency*1000, 2)
        await ctx.send(f"<:babyyay:839518621352460289> `{websocket}`ms")


    @commands.command(help="Link for the top.gg & discordbotlist vote page")
    async def vote(self, ctx):
        link = "[`vote on top.gg!`](https://top.gg/bot/801742991185936384)"
        link2 = "[`vote on discordbotlist!`](https://discordbotlist.com/bots/ami)"
        em = discord.Embed(description=f"**{link}** (**`+20k Coins`**)\n**{link2}**\nThanks if you vote! <3", color = 0xffcff1)
        await ctx.send(embed=em)


    @commands.command(help="See your actual time or the time of a member if set.\nTime are in **`UTC +01:00 24h`** format.\nUse `ami set-tz [zone]` to set your zone. ([All valid zones list](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568))")
    async def time(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        author_id = str(member.id)
        db = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)

        if not db:
            return await ctx.reply(f"I didn't found this member inside the database, tell him to send `ami bal` and retry again after done.")

        if db["tz"] == None:
            tmz = "[All valid zones list](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568)"
            em = discord.Embed(description=f"The member didn't provided a zone.\n{tmz}", color = 0xffcff1)
            await ctx.send(embed=em)
            return

        t = db["tz"]
        fmt = "%A | %I:%M %p | %d %B %Y"
        dt_today = datetime.datetime.today()   # Local time
        dt_India = dt_today.astimezone(pytz.timezone(t)) 
        t3 = (dt_India.strftime(fmt))
        em = discord.Embed(title=f"<a:9932_zero_two:819689873870946395> Time for {member.name}", description = f"{t3}", color = 0xffcff1)
        em.set_footer(text=f"{t}", icon_url=f"{member.avatar_url}")
        await ctx.send(embed=em)
        return

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
            link = "https://google.com"
        
        syno = anime[0].synopsis.strip("(Source: MAL Rewrite)")
        syno = anime[0].synopsis.strip("[Written by MAL Rewrite]")
        syno = anime[0].synopsis.strip("(Source: Crunchyroll)")
        syno = anime[0].synopsis.strip("(Source: ANN")
        em = discord.Embed(title=f"{anime[0].title}", url=f"{link}", description=f"{syno}", color=0xffcff1)
        em.set_thumbnail(url=anime[0].poster_image_url)
        em.set_footer(text=f"Episodes: {anime[0].episode_count} | Status: {anime[0].status.title()} | Nsfw: {anime[0].nsfw} | {anime[0].age_rating_guide}")
        if anime[0].ended_at:
            em.set_author(name=f"{anime[0].started_at.strftime('%Y-%m-%d')} - {anime[0].ended_at.strftime('%Y-%m-%d')} | Rank: #{anime[0].popularity_rank}")
        else:
            em.set_author(name=f"{anime[0].started_at.strftime('%Y-%m-%d')} | Rank: #{anime[0].popularity_rank}")
        await ctx.reply(embed=em, mention_author=False)

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

import discord
from discord.ext import commands, tasks
import random
import datetime
import time
from discord.ext.commands.cooldowns import BucketType
import simpleeval
import asyncio
import pytz
from pytz import all_timezones
from discord_markdown.discord_markdown import convert_to_html
from util.fuzzy import finder
from io import BytesIO
import kitsu
from aiogtts import aiogTTS
import string
import os
import randfacts
from twitch import TwitchClient
import humanize
import aiohttp
from util.pil_funcs import GayMeter, Ship
import util.config as config
from spongebobcase import tospongebob
import re
from util.defs import is_team, premium

kitsu_client = kitsu.Client()
twitch = TwitchClient(client_id=config.TWITCH_CLIENT)

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.afks = {}
        self.languages = {}
        self.category = "Fun"
        self.session = aiohttp.ClientSession()
        bot.loop.create_task(self.cache_langs())
        bot.loop.create_task(self.cache_afks())

    async def cache_afks(self):
        await self.bot.wait_until_ready()
        db = await self.bot.db.fetch("SELECT * FROM afks")
        for i in db:
            self.afks[i["user_id"]] = {"time": i['time'], "reason": i['reason'], "ignored": [i['ignored_channels']]}

    async def cache_langs(self):
        await self.bot.wait_until_ready()
        db = await self.bot.db.fetch("SELECT * FROM tts")
        for i in db:
            if i["language"]:
                self.languages[i["guild_id"]] = i["language"]

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Fun Loaded")

    @commands.command(help="Solve the math problem in the prestablished time", aliases=["sm"])
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def speedmath(self, ctx):

        num1 = random.randint(1, 99)
        num2 = random.randint(1, 99)

        operators = ['+', '-']

        alibi = {
            "+": "+",
            "-": "-"
        }

        final_operator = random.choice(operators)
        symbol = alibi[final_operator]

        if symbol == "+":
            answ = num1 + num2
        elif symbol == "-":
            answ = num1 - num2

        await ctx.send(f"{ctx.author.mention} started a speedmath game, it'll start in 5 seconds...")

        timet = random.randint(3, 12)

        await asyncio.sleep(5)

        await ctx.send(f"Math to solve in {timet} seconds: `{num1}` {symbol} `{num2}`")

        start = time.time()

        while True:
            try:
                mex = await self.bot.wait_for("message", check=lambda m: m.channel == ctx.channel and not m.author.bot and m.content == str(answ), timeout=timet)
            except asyncio.TimeoutError:
                await ctx.send(f"Nobody sent the correct answer in time.")
                return

            end = time.time()
            f = round(end - start)
            await mex.reply(f"Correct, you solved it in {f} seconds! Good job, another round? 🤭")
            return

    @commands.command(
        help="ConvErT the GIvEN tEXT intO thIS WeiRD aNd HArD-TO-rEaD foRmAT"
    )
    async def mock(self, ctx, *, text):
        if all(x.isalpha() or x.isspace() for x in text):
            return await ctx.send(
                f"{tospongebob(text)}"
                if len(text) > 1
                else f"{ctx.author.mention} the text must be at least 2 characters."
            )
        return await ctx.send(f"{ctx.author.mention} the text must be only letters.")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def caption(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        url = f"{member.avatar_url}"
        async with self.session as session:
            res = await session.post(
                "https://captionbot.azurewebsites.net/api/messages",
                json={"Content": url, "Type": "CaptionRequest"},
                headers={"Content-Type": "application/json; charset=utf-8"},
            )
        text = await res.text()
        em = discord.Embed(description=text, color=self.bot.color)
        em.set_image(url=url)
        await ctx.send(embed=em)

    @commands.command(
        help="Search a twitch stream directly with this command, see if it is in live, check followers and total views, and some other info!",
        aliases=["ttv", "tw"],
    )
    @premium(override=True)
    async def twitch(self, ctx, *, name: str):
        """Gets a twitch channel's statistics."""
        if twitch is None:
            await ctx.send(
                "The bot owner did not specify a twitch api key, therefore this command is disabled."
            )
            return
        try:
            channel = twitch.search.channels(name, limit=1)[0]
        except IndexError:
            await ctx.send(
                f"<:4318crossmark:848857812565229601> Could not find any channel by the name of **{name}**",
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return
        stream = twitch.streams.get_stream_by_user(channel["id"])
        streaming = "<:offline:859131537734500353>"
        game = None
        if channel["game"]:
            game = channel["game"]
        fields = {
            "Name": channel["status"] or "Unknown",
            "Description": channel["description"] or "Unknown",
            "For Mature": channel["mature"] or "Unknown",
            "Category": game,
            "Created": (channel["created_at"]).strftime("%B %d, %Y at %I:%M:%S %p")
            or "Unknown",
            "Total Views": humanize.intword(channel["views"]) or "Unknown",
            "Followers": humanize.intword(channel["followers"]) or "Unknown",
        }
        if stream is not None:
            streaming = "<:online:859131538058641418>"
            fields["Live Viewers"] = humanize.intword(stream["viewers"])
        fields["Live"] = streaming

        desc = ""
        for key, value in fields.items():
            desc += f"**{key}** : {value}\n"

        embed = discord.Embed()

        if channel["logo"] is not None:
            embed.set_thumbnail(url=channel["logo"])

        embed.description = desc
        embed.title = f'<:twitch:859129135833939998> {channel["display_name"]}'
        embed.url = channel["url"]
        if streaming == "<:online:859131538058641418>":
            embed.set_image(
                url=stream["preview"]["large"]
                + "?v={}".format(random.randint(0, 10000))
            )
            embed.color = self.bot.color
        else:
            if channel["video_banner"] is not None:
                embed.set_image(url=channel["video_banner"])
            embed.color = self.bot.color
        await ctx.send(embed=embed)

    @commands.command(
        help='Reverse the given phrase, e.g:\n`ami reverse "hi mom"` will return `"mom ih"`',
        aliases=["rev", "rv"],
    )
    async def reverse(self, ctx, *, message):
        if len(message) > 2000:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> Your message was {len(message)} characters long, which is over the maximum (`2048`)."
            )
        await ctx.reply(message[::-1], mention_author=False)

    @commands.command(
        name="penis-size",
        help="Look how long is the ||penis|| of a member >.>",
        aliases=["pp", "psize"],
    )
    async def penis_size(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        size = random.randint(0, 32)

        final_pp_size = f"8{(''.join('=' * size))}D"
        await ctx.send(
            embed=discord.Embed(
                description=final_pp_size, color=self.bot.color
            ).set_author(
                name=f"{member.name}'s pp ({size}cm)", icon_url=member.avatar_url
            )
        )

    @commands.command(
        help="Get a random fact, you can also pass some arguments to retrive innapropriate facts (they are excluded by default), or exclude them, e.g:\n`ami fact --unsafe` to retrive inappropriate facts."
    )
    async def fact(self, ctx, flags=None):
        if flags:
            if flags == "--unsafe":
                x = randfacts.getFact(only_unsafe=True)
                return await ctx.reply(x, mention_author=False)

        x = randfacts.getFact()
        return await ctx.reply(x, mention_author=False)

    @commands.command(
        help="An advanced gay calculator to calculate how much gay is a member >.> (Joking, is just a random percentage)",
        aliases=["gay"],
    )
    async def gaymeter(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        asset = member.avatar_url_as(size=512)
        pfp = BytesIO(await asset.read())

        perc = random.randint(0, 100)

        buffer = await self.bot.loop.run_in_executor(
            None, GayMeter.gaymeter_func, pfp, perc
        )
        file = discord.File(fp=buffer, filename="gaymeter.png")
        return await ctx.send(file=file)

    @commands.command(
        help="Create a text to speech file with the given query, and make it send in the chat!\n\n`ami tts setlang` to set the default tts language for the guild.\n`ami tts lang` to check the language set.",
        aliases=["tts"],
    )
    async def texttospeech(self, ctx: commands.Context, *, query: str):
        if query.lower() == "setlang":
            if not ctx.author.guild_permissions.manage_channels:
                return await ctx.send(
                    "<:4318crossmark:848857812565229601> You don't have `Manage Channels` permissions to run this command."
                )

            await ctx.send(
                "<:4430checkmark:848857812632076314> Now send the language code you want to set as default (examples: `it`, `en`, `fr`.)"
            )

            try:
                msg = await self.bot.wait_for(
                    "message",
                    check=lambda message: message.author == ctx.author
                    and message.channel == ctx.channel,
                )
            except asyncio.TimeoutError:
                return

            await self.bot.db.execute(
                "INSERT INTO tts (guild_id, language) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET language = $2",
                ctx.guild.id,
                msg.content.lower(),
            )
            self.languages[ctx.guild.id] = msg.content.lower()
            return await msg.add_reaction("<:4430checkmark:848857812632076314>")

        if query.lower() == "lang":
            if ctx.guild.id not in self.languages:
                return await ctx.send(
                    "<:4318crossmark:848857812565229601> This guild has not a language set for tts, set one with `ami tts setlang`."
                )

            em = discord.Embed(
                description=f"<:4430checkmark:848857812632076314> TTS language for this guild is `{self.languages[ctx.guild.id]}`",
                color=self.bot.color,
            )
            return await ctx.send(embed=em)

        if ctx.guild.id not in self.languages:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> This guild has not a language set for tts, set one with `ami tts setlang`."
            )

        if len(query) > 500:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> The text given is **{len(query)}** characters, max is **500**."
            )

        aiogtts = aiogTTS()
        lang = self.languages[ctx.guild.id]

        d = string.ascii_letters + string.digits
        keylist = [random.choice(d) for i in range(10)]
        f = "".join(keylist)

        mentions = re.findall("<@!?([0-9]+)>", query)

        if mentions:
            for mention in mentions:
                query = query.replace(mention, self.bot.get_user(int(mention.strip("<@>"))).name)

        query = query.strip("<@!>")

        try:
            await aiogtts.save(query, f"{f}.mp3", lang=lang)
        except Exception:
            os.remove(f"{f}.mp3")
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> `{lang}` is not a valid language code, e.g: `it`, `en`, `fr`."
            )

        await ctx.send(file=discord.File(f"{f}.mp3"))
        return os.remove(f"{f}.mp3")

    @commands.command(
        help="Set a custom reminder, and get pinged when it's time!\nExample usage: **ami remind 1s hi** - 1s = <time>, 'hi' = [message]\nYou can't delete a reminder set."
    )
    async def remind(self, ctx, time, *, message=None):
        if message == None:
            message = ". . ."

        if message == "@everyone":
            message = ". . ."

        if message == "@here":
            message = ". . ."

        def convert(time):
            pos = ["s", "m", "h", "d"]

            time_dict = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}

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
            return await ctx.reply(
                "Time unit not valid, valid units are: `s`, `m`, `h`, `d`."
            )

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
        date_time = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=converted_time
        )
        await discord.utils.sleep_until(date_time)
        await ctx.send(
            f"{ctx.author.mention}, {final_time} ago: {message}\n{ctx.message.jump_url}"
        )

    @commands.group(
        help="Start a simple counting game in the channel where you use this command! There is different modes of counting, check subcommands for more!",
        invoke_without_command=True
    )
    @commands.max_concurrency(1, BucketType.channel)
    async def count(self, ctx):
        try:
            return await ctx.invoke(**{"command": "count"})
        except Exception:
            await ctx.send(
                "<:greenTick:596576670815879169> Counting game __started__, good luck!"
            )
            author_id = ""
            num = 0
            while True:
                mex = await self.bot.wait_for(
                    "message",
                    check=lambda m: not m.author.bot and m.channel == ctx.channel,
                )
                if mex.content == str(num + 1):
                    if str(mex.author.id) == author_id:
                        await mex.add_reaction("<:4318crossmark:848857812565229601>")
                        await ctx.send(
                            f"<:redTick:596576672149667840> {mex.author.mention} sent __two__ numbers, `ami count` to restart."
                        )
                        db = await self.bot.db.fetch(
                            "SELECT * FROM counting WHERE guild_id = $1",
                            str(ctx.guild.id),
                        )
                        if not db:
                            return await self.bot.db.execute(
                                "INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)",
                                str(ctx.guild.id),
                                num,
                                1,
                            )

                        final_score = 0
                        if db[0]["higher_score"] > num:
                            final_score = db[0]["higher_score"]
                        else:
                            final_score = num

                        await self.bot.db.execute(
                            "UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3",
                            final_score,
                            db[0]["restarts"] + 1,
                            str(ctx.guild.id),
                        )
                        break
                    num += 1
                    author_id = str(mex.author.id)
                    await mex.add_reaction("<:4430checkmark:848857812632076314>")
                else:
                    await mex.add_reaction("<:4318crossmark:848857812565229601>")
                    await ctx.send(
                        f"<:redTick:596576672149667840> {mex.author.mention} failed! Stop at **`{num}`**, send `ami count` to restart."
                    )
                    db = await self.bot.db.fetch(
                        "SELECT * FROM counting WHERE guild_id = $1", str(ctx.guild.id)
                    )
                    if not db:
                        return await self.bot.db.execute(
                            "INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)",
                            str(ctx.guild.id),
                            num,
                            1,
                        )

                    final_scoree = 0
                    if db[0]["higher_score"] > num:
                        final_scoree = db[0]["higher_score"]
                    else:
                        final_scoree = num

                    await self.bot.db.execute(
                        "UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3",
                        final_scoree,
                        db[0]["restarts"] + 1,
                        str(ctx.guild.id),
                    )
                    break

    @count.command(help="See the counting stats for the current guild")
    async def stats(self, ctx):
        db = await self.bot.db.fetch(
            "SELECT * FROM counting WHERE guild_id = $1", str(ctx.guild.id)
        )
        if not db:
            return await ctx.send(
                "<:redTick:596576672149667840> This guild has no __stats__ registered, play a counting game before."
            )

        higher_score = db[0]["higher_score"]
        restarts = db[0]["restarts"]

        em = discord.Embed(title=f"Counting Stats", color=self.bot.color)
        em.set_author(name=f"{ctx.guild.name}", icon_url=ctx.guild.icon_url)
        em.add_field(
            name="<:7343exclamationmark:848857813252833290> Higher Score",
            value=f"<a:4484pinkarrow:848857813085716520> The higher score registered for this guild is: **{humanize.intcomma(higher_score)}**",
        )
        em.add_field(
            name="<:7343exclamationmark:848857813252833290> Restarts",
            value=f"<a:4484pinkarrow:848857813085716520> The counting game in this guild has been restarted: **{humanize.intcomma(restarts)}** times.",
        )
        return await ctx.send(embed=em)

    @count.command(help='See the highest counting number reached in the current guild.')
    async def score(self, ctx):
        db = await self.bot.db.fetch(
            "SELECT * FROM counting WHERE guild_id = $1", str(ctx.guild.id)
        )
        if not db:
            return await ctx.send(
                "<:redTick:596576672149667840> This guild has no __stats__ registered, play a counting game before."
            )

        higher_score = db[0]["higher_score"]
        return await ctx.send(
            f"<:5324_letters:848857812577812511> Higher counting score in this guild is **{higher_score}**"
        )

    @count.command(help="See the total restarts made in counting for the current guild")
    async def restarts(self, ctx):
        db = await self.bot.db.fetch(
            "SELECT * FROM counting WHERE guild_id = $1", str(ctx.guild.id)
        )
        if not db:
            return await ctx.send(
                "<:redTick:596576672149667840> This guild has no __stats__ registered, play a counting game before."
            )

        restarts = db[0]["restarts"]
        return await ctx.send(
            f"<:5324_letters:848857812577812511> The counting game was restarted **{restarts}** times."
        )

    @count.command(name="--m-a", help="Start a counting game with messages allowed")
    @premium(override=True)
    async def messages_allowed(self, ctx):
        await ctx.send(
            "<:greenTick:596576670815879169> Counting game __started__ with `messages allowed` mode, good luck!"
        )
        author_id = ""
        num = 0
        while True:
            mex = await self.bot.wait_for(
                "message",
                check=lambda m: not m.author.bot and m.channel == ctx.channel,
            )
            if mex.content.isdigit():
                if mex.content == str(num + 1):
                    if str(mex.author.id) == author_id:
                        await mex.add_reaction(
                            "<:4318crossmark:848857812565229601>"
                        )
                        await ctx.send(
                            f"<:redTick:596576672149667840> {mex.author.mention} sent __two__ numbers, `ami count --m-a` to restart with messages allowed."
                        )
                        db = await self.bot.db.fetch(
                            "SELECT * FROM counting WHERE guild_id = $1",
                            str(ctx.guild.id),
                        )
                        if not db:
                            return await self.bot.db.execute(
                                "INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)",
                                str(ctx.guild.id),
                                num,
                                1,
                            )

                        final_score = 0
                        if db[0]["higher_score"] > num:
                            final_score = db[0]["higher_score"]
                        else:
                            final_score = num

                        await self.bot.db.execute(
                            "UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3",
                            final_score,
                            db[0]["restarts"] + 1,
                            str(ctx.guild.id),
                        )
                        break
                    num += 1
                    author_id = str(mex.author.id)
                    await mex.add_reaction(
                        "<:4430checkmark:848857812632076314>"
                    )
                else:
                    await mex.add_reaction(
                        "<:4318crossmark:848857812565229601>"
                    )
                    await ctx.send(
                        f"<:redTick:596576672149667840> {mex.author.mention} failed! Stop at **`{num}`**, send `ami count --m-a` to restart the game with messages allowed."
                    )
                    db = await self.bot.db.fetch(
                        "SELECT * FROM counting WHERE guild_id = $1",
                        str(ctx.guild.id),
                    )
                    if not db:
                        return await self.bot.db.execute(
                            "INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)",
                            str(ctx.guild.id),
                            num,
                            1,
                        )

                    final_scoree = 0
                    if db[0]["higher_score"] > num:
                        final_scoree = db[0]["higher_score"]
                    else:
                        final_scoree = num

                    await self.bot.db.execute(
                        "UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3",
                        final_scoree,
                        db[0]["restarts"] + 1,
                        str(ctx.guild.id),
                    )
                    break

    @count.command(name="--r", help="Start a counting game with restricted mode")
    @premium(override=True)
    async def restricted(self, ctx, whitelist: commands.Greedy[discord.Member] = None):
        if not whitelist:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> You need to specify the `[whitelist]` argument for this mode, check `ami help count` to know more."
            )

        if len(whitelist) > 10:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> Restrict mode has a max. of 10 players, you have passed {len(whitelist)} players."
            )

        if len(whitelist) < 2:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> At least 2 players needed to start the game in restricted mode."
            )

        if ctx.author not in whitelist:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> You can't start a restriced counting game without you in."
            )

        d = []
        for s in whitelist:
            id = s.id
            user = self.bot.get_user(id) or (await self.bot.fetch_user(id))
            if user.bot:
                return await ctx.send(
                    f"<:4318crossmark:848857812565229601> {user.mention} is a bot, it can't play counting."
                )
            d.append(user.mention)

        dcv = " | ".join(d)

        await ctx.send(
            f"<:greenTick:596576670815879169> Counting game __started__ with `restricted` mode ({dcv}), good luck!"
        )
        author_id = ""
        num = 0
        while True:
            mex = await self.bot.wait_for(
                "message",
                check=lambda m: not m.author.bot and m.channel == ctx.channel,
            )

            s = []
            for i in whitelist:
                id = i.id
                s.append(id)

            if mex.author.id in s:
                if mex.content == str(num + 1):
                    if str(mex.author.id) == author_id:
                        await mex.add_reaction(
                            "<:4318crossmark:848857812565229601>"
                        )
                        await ctx.send(
                            f"<:redTick:596576672149667840> {mex.author.mention} sent __two__ numbers, `ami count --r @members` to restart."
                        )
                        db = await self.bot.db.fetch(
                            "SELECT * FROM counting WHERE guild_id = $1",
                            str(ctx.guild.id),
                        )
                        if not db:
                            return await self.bot.db.execute(
                                "INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)",
                                str(ctx.guild.id),
                                num,
                                1,
                            )

                        final_score = 0
                        if db[0]["higher_score"] > num:
                            final_score = db[0]["higher_score"]
                        else:
                            final_score = num

                        await self.bot.db.execute(
                            "UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3",
                            final_score,
                            db[0]["restarts"] + 1,
                            str(ctx.guild.id),
                        )
                        break
                    num += 1
                    author_id = str(mex.author.id)
                    await mex.add_reaction(
                        "<:4430checkmark:848857812632076314>"
                    )
                else:
                    await mex.add_reaction(
                        "<:4318crossmark:848857812565229601>"
                    )
                    await ctx.send(
                        f"<:redTick:596576672149667840> {mex.author.mention} failed! Stop at **`{num}`**, send `ami count --r @members` to restart the restricted game."
                    )
                    db = await self.bot.db.fetch(
                        "SELECT * FROM counting WHERE guild_id = $1",
                        str(ctx.guild.id),
                    )
                    if not db:
                        return await self.bot.db.execute(
                            "INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)",
                            str(ctx.guild.id),
                            num,
                            1,
                        )

                    final_scoree = 0
                    if db[0]["higher_score"] > num:
                        final_scoree = db[0]["higher_score"]
                    else:
                        final_scoree = num

                    await self.bot.db.execute(
                        "UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3",
                        final_scoree,
                        db[0]["restarts"] + 1,
                        str(ctx.guild.id),
                    )
                    break
            else:
                pass

    @count.command(name="--r-m-a", help="Start a counting game with restricted mode and messages allowed")
    @premium(override=True)
    async def messages_restricted(self, ctx, whitelist: commands.Greedy[discord.Member] = None):
        if not whitelist:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> You need to specify the `[whitelist]` argument for this mode, check `ami help count` to know more."
            )

        if len(whitelist) > 10:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> Restrict mode has a max. of 10 players, you have passed {len(whitelist)} players."
            )

        if len(whitelist) < 2:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> At least 2 players needed to start the game in restricted mode."
            )

        if ctx.author not in whitelist:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> You can't start a restriced counting game without you in."
            )

        d = []
        for s in whitelist:
            id = s.id
            user = self.bot.get_user(id) or (await self.bot.fetch_user(id))
            if user.bot:
                return await ctx.send(
                    f"<:4318crossmark:848857812565229601> {user.mention} is a bot, it can't play counting."
                )
            d.append(user.mention)

        dcv = " | ".join(d)

        await ctx.send(
            f"<:greenTick:596576670815879169> Counting game __started__ with `restricted` mode ({dcv}), good luck!"
        )
        author_id = ""
        num = 0
        while True:
            mex = await self.bot.wait_for(
                "message",
                check=lambda m: not m.author.bot and m.channel == ctx.channel,
            )

            s = []
            for i in whitelist:
                id = i.id
                s.append(id)

            if mex.content.isdigit():
                if mex.author.id in s:
                    if mex.content == str(num + 1):
                        if str(mex.author.id) == author_id:
                            await mex.add_reaction(
                                "<:4318crossmark:848857812565229601>"
                            )
                            await ctx.send(
                                f"<:redTick:596576672149667840> {mex.author.mention} sent __two__ numbers, `ami count --r-m-a @members` to restart."
                            )
                            db = await self.bot.db.fetch(
                                "SELECT * FROM counting WHERE guild_id = $1",
                                str(ctx.guild.id),
                            )
                            if not db:
                                return await self.bot.db.execute(
                                    "INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)",
                                    str(ctx.guild.id),
                                    num,
                                    1,
                                )

                            final_score = 0
                            if db[0]["higher_score"] > num:
                                final_score = db[0]["higher_score"]
                            else:
                                final_score = num

                            await self.bot.db.execute(
                                "UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3",
                                final_score,
                                db[0]["restarts"] + 1,
                                str(ctx.guild.id),
                            )
                            break
                        num += 1
                        author_id = str(mex.author.id)
                        await mex.add_reaction(
                            "<:4430checkmark:848857812632076314>"
                        )
                    else:
                        await mex.add_reaction(
                            "<:4318crossmark:848857812565229601>"
                        )
                        await ctx.send(
                            f"<:redTick:596576672149667840> {mex.author.mention} failed! Stop at **`{num}`**, send `ami count --r-m-a @members` to restart the restricted game."
                        )
                        db = await self.bot.db.fetch(
                            "SELECT * FROM counting WHERE guild_id = $1",
                            str(ctx.guild.id),
                        )
                        if not db:
                            return await self.bot.db.execute(
                                "INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)",
                                str(ctx.guild.id),
                                num,
                                1,
                            )

                        final_scoree = 0
                        if db[0]["higher_score"] > num:
                            final_scoree = db[0]["higher_score"]
                        else:
                            final_scoree = num

                        await self.bot.db.execute(
                            "UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3",
                            final_scoree,
                            db[0]["restarts"] + 1,
                            str(ctx.guild.id),
                        )
                        break
            else:
                pass

    @count.command(name="--d-w", help="Start a counting game with delete wrong mode")
    async def delete_wrong(self, ctx):
        if not ctx.guild.me.guild_permissions.manage_messages:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> I need the `Manage Messages` permission to run this mode of counting."
            )

        await ctx.send(
            "<:greenTick:596576670815879169> Counting game __started__ with `delete wrong` mode, send `ami stopcount` to stop it, good luck!"
        )
        author_id = ""
        num = 0
        while True:
            mex = await self.bot.wait_for(
                "message",
                check=lambda m: not m.author.bot and m.channel == ctx.channel,
            )
            if mex.content == "ami stopcount":
                await ctx.send(
                    "<:4430checkmark:848857812632076314> Counting game stopped succesfully!"
                )
                db = await self.bot.db.fetch(
                    "SELECT * FROM counting WHERE guild_id = $1",
                    str(ctx.guild.id),
                )
                if not db:
                    return await self.bot.db.execute(
                        "INSERT INTO counting (guild_id, higher_score, restarts) VALUES ($1, $2, $3)",
                        str(ctx.guild.id),
                        num,
                        1,
                    )

                final_score = 0
                if db[0]["higher_score"] > num:
                    final_score = db[0]["higher_score"]
                else:
                    final_score = num

                await self.bot.db.execute(
                    "UPDATE counting SET higher_score = $1, restarts = $2 WHERE guild_id = $3",
                    final_score,
                    db[0]["restarts"] + 1,
                    str(ctx.guild.id),
                )
                break

            elif mex.content == str(num + 1):
                if str(mex.author.id) == author_id:
                    await mex.delete()
                    continue
                num += 1
                author_id = str(mex.author.id)
                await mex.add_reaction("<:4430checkmark:848857812632076314>")
            else:
                await mex.delete()

    @commands.command(
        help="Set your AFK mode globally (it means only where i can see you).\nAFK is a modality where when you are in, if someone pings you, ami will advice who pinged you, you are afk for `[reason]`.\nOtherwise, when you send a message in a channel / guild where i can see your messages, your afk mode will be deleted."
    )
    async def afk(self, ctx, *, reason=None):
        if reason == None:
            reason = "Not specified."

        if len(reason) > 100:
            return await ctx.reply(":x: The reason must be less than **100** letters.")

        await ctx.send(
            f"✅ Alright {ctx.author.mention}, you are now **AFK** for:  {reason}",
            allowed_mentions=discord.AllowedMentions.none(),
        )
        self.afks[ctx.author.id] = {"time": datetime.datetime.utcnow(), "reason": reason, 'ignored': []}
        await self.bot.db.execute("INSERT INTO afks (user_id, time, reason) VALUES ($1, $2, $3) ON CONFLICT (user_id) DO UPDATE SET reason = $3", ctx.author.id, datetime.datetime.utcnow(), reason)

    @commands.command(help="Set the channels to ignore for AFK mode, you can provide multiple channels at same time.", aliases=['afkign'])
    async def afkignore(self, ctx, channels: commands.Greedy[discord.TextChannel]):
        
        if ctx.author.id not in self.afks:
            return await ctx.reply(":x: You are not AFK now, go afk and try again.")

        for channel in channels:
            if channel not in ctx.guild.channels:
                return await ctx.reply(f":x: {channel} not found in this guild.")

        for chan in channels:
            await self.bot.db.execute("UPDATE afks SET ignored_channels = array_append(ignored_channels, $1) WHERE user_id = $2", chan.id, ctx.author.id)
            self.afks[ctx.author.id]['ignored'].append(chan.id)

        await ctx.send(f"{ctx.author.mention} succesfully set {' '.join([channel.mention for channel in channels])} as ignored channels for AFK!")

    @commands.command()
    @is_team()
    async def afklist(self, ctx):
        return await ctx.send(self.afks)

    @commands.Cog.listener("on_message")
    async def foo(self, message: discord.Message):

        if message.author == self.bot.user:
            return
        
        if message.author.bot:
            return

        if message.content.lower().startswith("ami afk"):
            return self.afk

        if message.content.lower().startswith("ami afkignore"):
            return self.afkignore

        if message.content.lower().startswith("ami afkign"):
            return self.afkignore

        if message.author.id in self.afks:
            ids = message.author.id

            if message.channel.id in self.afks[ids]['ignored']:
                return

            time = self.afks[ids]["time"]

            delta_uptime = datetime.datetime.utcnow() - time
            hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)
            
            if not minutes:
                final_time = f"**{seconds}**S"
            elif not hours:
                final_time = f"**{minutes}**M **{seconds}**S"
            elif not days:
                final_time = f"**{hours}**H **{minutes}**M **{seconds}**S"
            else:
                final_time = f"**{days}**D **{hours}**H **{minutes}**M **{seconds}**S"

            try:
                await message.channel.send(f"🔔 Welcome back {message.author.mention}, you've been afk for {final_time}.")
            except discord.Forbidden:
                pass
            if ids in self.afks:
                del self.afks[ids]
            await self.bot.db.execute("DELETE FROM afks WHERE user_id = $1", message.author.id)

        try:
            id2 = message.mentions[0].id
        except IndexError:
            id2 = "None"
        if id2 in self.afks.keys():
            reasons = self.afks[id2]["reason"]
            time = self.afks[id2]["time"]

            delta_uptime = datetime.datetime.utcnow() - time
            hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)
            
            if not minutes:
                final_time = f"**{seconds}**S"
            elif not hours:
                final_time = f"**{minutes}**M **{seconds}**S"
            elif not days:
                final_time = f"**{hours}**H **{minutes}**M **{seconds}**S"
            else:
                final_time = f"**{days}**D **{hours}**H **{minutes}**M **{seconds}**S"

            try:
                return await message.channel.send(
                f"🔔 {message.author.mention}, i'm sorry but **{str(message.mentions[0].name)}** went afk {final_time} ago for: {reasons}"
                )
            except discord.Forbidden:
                pass

    @commands.command(
        help='Choose between multiple choices.\nAdd quotemarks at the start & end of something to mark a long phrase as a possible choice, e.g: `ami choose sky "watch anime" netflix`'
    )
    async def choose(self, ctx, *choices: str):
        if len(choices) < 2:
            return await ctx.send(
                f"{ctx.author.mention} please provide at least 2 choices."
            )
        choi = random.choice(choices)
        await ctx.send(choi, allowed_mentions=discord.AllowedMentions.none())

    @commands.command(
        help="Test your reaction timing with this simple, fast and addictive game based on your reaction speed!",
        aliases=["rspeed"],
    )
    async def reactspeed(self, ctx, number: float):
        if number > 20.0:
            em = discord.Embed(
                description="<:alert:819704994612904017> Time can't be over 20.0 seconds."
            )
            em.set_author(
                name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}"
            )
            await ctx.send(embed=em)
            return

        if number < 0.1:
            em = discord.Embed(
                description="<:alert:819704994612904017> Time can't be < 0.1 second."
            )
            em.set_author(
                name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}"
            )
            await ctx.send(embed=em)
            return

        embed = discord.Embed(
            description=f"Try to click on reaction at {number} seconds.",
            color=self.bot.color,
        )
        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
        message = await ctx.send(embed=embed)
        await message.add_reaction("<a:nono:819694934189277214>")
        start = time.time()
        start2 = number + 5.0

        def check(payload):
            return (
                payload.message_id == message.id
                and payload.emoji.name == "nono"
                and payload.user_id == ctx.author.id
            )

        try:
            await self.bot.wait_for("raw_reaction_add", check=check, timeout=start2)
        except asyncio.TimeoutError:
            return await ctx.send(
                f"<:alert:819704994612904017> No reaction detected from **{ctx.author.name}**."
            )

        end = time.time()
        embed = discord.Embed(
            title=f"{number} second(s) reaction",
            description=f"<:vea:819703490703523860> Your result is: `{round(end-start, 2)}` seconds",
            color=self.bot.color,
        )
        embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
        await message.edit(embed=embed)

    @commands.command(help="Retrive the invite link to invite me anywhere you want!")
    async def invite(self, ctx):
        await ctx.send(
            embed=discord.Embed(
                title="https://amibot.gg/invite",
                timestamp=datetime.datetime.utcnow(),
                color=self.bot.color,
            )
        )

    @commands.command(
        help="Ship two members between themself, and get the love percentage!\nYou can ship yourself with another member sending the `<member>`, without `[member2]`."
    )
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

        # get the first mention avatar
        try:
            asset1 = pfp.avatar_url_as(size=512)
            avatar = BytesIO(await asset1.read())
        except Exception:
            asset1 = await self.bot.fetch_user(pfp.id)
            av = asset1.avatar_url_as(size=512)
            avatar = BytesIO(await av.read())

        # get the second mention avatar
        try:
            asset2 = pfp2.avatar_url_as(size=512)
            avatar2 = BytesIO(await asset2.read())
        except Exception:
            asset2 = await self.bot.fetch_user(pfp2.id)
            av = asset2.avatar_url_as(size=512)
            avatar2 = BytesIO(await av.read())

        perc = random.randint(0, 100)

        buffer = await self.bot.loop.run_in_executor(
            None, Ship.ship_func, perc, avatar, avatar2
        )
        file = discord.File(fp=buffer, filename="ship.png")

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

    @commands.command(
        help="Evaluate an expression, it's accepts float / int numbers.\nSupported calculation are:\n`/` = division\n`*` = multiplication\n`+` = addition\n`-` = subtraction\n`**` = power",
        aliases=["calc", "math", "expr"],
    )
    async def calculate(self, ctx, *, expression: str):
        try:
            calculation = simpleeval.simple_eval(expression)

            if len(str(calculation)) > 30:
                await ctx.send(
                    "<:4318crossmark:848857812565229601> Result is too long to be displayed"
                )
                return

            if str(expression) == "...":
                await ctx.send(
                    "<:4318crossmark:848857812565229601> Are you sure this is a valid expression?"
                )
                return

            await ctx.reply(
                f"<:4430checkmark:848857812632076314> {expression} = {calculation}"
            )

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

    @commands.command(
        help="Get a valid nitro gift and swag with your friend telling them you got free nitro!"
    )
    async def nitro(self, ctx):
        await ctx.send(
            "https://pics.me.me/thumb_when-youre-broke-so-you-make-your-own-nitro-boost-69569902.png"
        )

    @commands.command(help="Get a member avatar", pass_context=True, aliases=["av"])
    async def avatar(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        await ctx.send(member.avatar_url)

    # Members Counter Command
    @commands.command(
        help="Retrive a detailed member count for the guild, separated in `total members`, `people` and `bots`.",
        aliases=["mc"],
    )
    async def membercount(self, ctx):
        a = ctx.guild.member_count
        b = len([m for m in ctx.guild.members if (m.bot)])
        c = len([m for m in ctx.guild.members if not m.bot])
        await ctx.send(
            f"<:4430checkmark:848857812632076314> I can see **{a}** total members in this guild, which **{c}** are people and **{b}** bots."
        )

    # Ping & Pong
    @commands.command(
        help="Check the latency of the discord websocket.", pass_context=True
    )
    async def ping(self, ctx):
        websocket = round(self.bot.latency * 1000, 2)
        await ctx.send(f"<:babyyay:839518621352460289> `{websocket}`ms")

    @commands.command(
        help="See your actual time or the time of a member if set.\nTime are in **`UTC 12h`** format.\nUse `ami set-tz [zone]` to set your zone. ([All valid zones list](https://gist.github.com/Soheab/3bec6dd6c1e90962ef46b8545823820d))"
    )
    async def time(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        author_id = member.id
        db = await self.bot.db.fetchrow(
            "SELECT * FROM timezone WHERE user_id = $1", author_id
        )

        if not db:
            return await ctx.reply(f"No timezone set, use `ami set-tz` to set it.")

        t = db["tz"]
        fmt = "%A | %I:%M %p | %d %B %Y"
        dt_today = datetime.datetime.today()  # Local time
        dt_India = dt_today.astimezone(pytz.timezone(t))
        t3 = dt_India.strftime(fmt)
        em = discord.Embed(
            title=f"<:clock:708884522866835547> Time for {member.name}",
            description=f"{t3}",
            color=self.bot.color,
        )
        em.set_footer(text=f"{t}", icon_url=f"{member.avatar_url}")
        await ctx.send(embed=em)
        return

    @commands.command(help="Set your timezone to check your time ([All valid zones list](https://gist.github.com/Soheab/3bec6dd6c1e90962ef46b8545823820d))", aliases=["set-tz"])
    async def timezone(self, ctx, zone):
        author_id = ctx.author.id
        db = await self.bot.db.fetch(
            "SELECT * FROM timezone WHERE user_id = $1", author_id
        )

        if zone == None:
            await ctx.send(
                f"{ctx.author.name}, be sure to send a zone across the command."
            )
            return

        if zone in all_timezones:
            zone1 = zone
            await self.bot.db.execute(
                "INSERT INTO timezone (user_id, tz) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET tz = $2",
                author_id,
                zone,
            )
            await ctx.send(
                f"{ctx.author.name}, you have set **{zone1}** as your zone, now you can check your time with `ami time`."
            )
        else:
            await ctx.send("The zone you provided isn't in the list, check `ami help time` for the timezones list.")

    @commands.command()
    @is_team()
    async def setzone(self, ctx, member: discord.Member, *, args):
        member_id = member.id
        timezone = args

        if timezone == None:
            em = discord.Embed(description="Specify a zone!")
            em.set_author(
                name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}"
            )
            await ctx.send(embed=em)
            return

        data = await self.bot.db.fetch(
            "SELECT * FROM timezone WHERE user_id = $1", member_id
        )
        if not data:
            if timezone in all_timezones:
                zone1 = timezone
                await self.bot.db.execute(
                    "INSERT INTO timezone (user_id, tz) VALUES ($1, $2)",
                    member_id,
                    zone1,
                )
                return await ctx.send(f"Set **{timezone}** for `{member}`!")
            else:
                return await ctx.send("Zone not found.")

        if timezone in all_timezones:
            zone1 = timezone
            await self.bot.db.execute(
                "UPDATE timezone SET tz = $1 WHERE user_id = $2", zone1, member_id
            )
            return await ctx.send(f"Set **{timezone}** for `{member}`!")
        else:
            return await ctx.send("Zone not found.")

    @commands.command(help="Convert the discord markdown into html format")
    async def html(self, ctx, *, args):
        html = convert_to_html(args)
        em = discord.Embed(description=f"```\n{html}\n```", color=0x2F3136)
        await ctx.send(embed=em)

    @commands.command(
        help="Search an anime and retrive some useful info about that.", aliases=["sa"]
    )
    async def searchanime(self, ctx, *, animename):
        anime = await kitsu_client.search("anime", animename)
        if not anime:
            return await ctx.reply(
                f"<:redTick:596576672149667840> Nothing found for **{animename}**."
            )

        slink = await kitsu_client.fetch_anime_streaming_links(anime[0])
        if slink:
            link = slink[0].url
        else:
            link = "https://google.com"

        syno = anime[0].synopsis.strip("(Source: MAL Rewrite)")
        syno = anime[0].synopsis.strip("[Written by MAL Rewrite]")
        syno = anime[0].synopsis.strip("(Source: Crunchyroll)")
        syno = anime[0].synopsis.strip("(Source: ANN")
        em = discord.Embed(
            title=f"{anime[0].title}",
            url=f"{link}",
            description=f"{syno}",
            color=self.bot.color,
        )
        em.set_thumbnail(url=anime[0].poster_image_url)
        em.set_footer(
            text=f"Episodes: {anime[0].episode_count} | Status: {anime[0].status.title()} | Nsfw: {anime[0].nsfw} | {anime[0].age_rating_guide}"
        )
        if anime[0].ended_at:
            em.set_author(
                name=f"{anime[0].started_at.strftime('%Y-%m-%d')} - {anime[0].ended_at.strftime('%Y-%m-%d')} | Rank: #{anime[0].popularity_rank}"
            )
        else:
            em.set_author(
                name=f"{anime[0].started_at.strftime('%Y-%m-%d')} | Rank: #{anime[0].popularity_rank}"
            )
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

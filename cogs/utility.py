import discord
from discord.ext import commands, menus
from nudenet import NudeClassifier
import typing
from urllib.request import urlretrieve
import datetime
import aiohttp
import asyncio
import humanize
import async_cse
import time
from jishaku.paginators import WrappedPaginator, PaginatorInterface
from collections import Counter
from util.defs import is_team, get_size, line_count
import psutil
import platform
import secrets
import googletrans
from twemoji_parser import emoji_to_url
import aiofiles
import base64
import string
import random

MAX_FILE_SIZE = 15000000

Image_Union = typing.Union[
    discord.Member,
    discord.User,
    discord.PartialEmoji,
    discord.Emoji,
    str,
]

def premium(override=False):
    async def predicate(ctx):
        premium_users = await ctx.bot.db.fetch("SELECT * FROM premium")
        if ctx.author.id not in [dict(record)["user_id"] for record in premium_users]:
            if override and ctx.author.id in [144126010642792449, 410452466631442443, 711057339360477184, 590323594744168494, 691406006277898302, 343019667511574528]:
                return True
            await ctx.send(embed = discord.Embed(
                description = "If you wish to use some neat features, hurry up and go buy Ami [premium!](https://amidiscord.xyz/premium)",
                color = ctx.bot.color,
                timestamp = datetime.datetime.utcnow()
            ).set_author(name=f"{ctx.author.name}, you are not Premium!", icon_url=ctx.author.avatar_url))
            return False
        else:
            return True
    return commands.check(predicate)

class InvalidImage(Exception):
    pass

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "Utility"
        self.session = aiohttp.ClientSession()
        self.bot.command_counter = 0
        self.bot.commandsusages = Counter()
        self.trans = googletrans.Translator()

    async def get_url(self, ctx: commands.Context, thing: typing.Optional[str], **kwargs: typing.Dict[str, typing.Any]) -> str:
        url = None
        avatar = kwargs.get("avatar", True)
        check = kwargs.get("check", True)
        checktype = kwargs.get("checktype", True)
        gif = kwargs.get("gif", False)

        if ctx.message.reference:
            message = ctx.message.reference.resolved

            if message.embeds and message.embeds[0].type == "image":
                url = message.embeds[0].thumbnail.url

            elif message.embeds and message.embeds[0].type == "rich":
                if message.embeds[0].image.url:
                    url = message.embeds[0].image.url

                elif message.embeds[0].thumbnail.url:
                    url = message.embeds[0].thumbnail.url

            elif message.attachments and message.attachments[0].width and message.attachments[0].height:
                url = message.attachments[0].url

            if message.stickers:
                sticker = message.stickers[0]

                if sticker.format != discord.StickerType.lottie:
                    url = str(sticker.image.url)
                else:
                    return False

        if ctx.message.attachments and ctx.message.attachments[0].width and ctx.message.attachments[0].height:
            url = ctx.message.attachments[0].url

        if ctx.message.stickers:
            sticker = ctx.message.stickers[0]

            if sticker.format != discord.StickerType.lottie:
                url = str(sticker.image.url)
            else:
                return False

        if thing is None and avatar and url is None:
            if gif:
                url = str(ctx.author.avatar_url_as(static_format="png", size=512))
            else:
                url = str(ctx.author.avatar_url_as(format="png", size=512))

        elif isinstance(thing, (discord.PartialEmoji, discord.Emoji)):
            if gif:
                url = f"https://cdn.discordapp.com/emojis/{thing.id}.{'gif' if thing.animated else 'png'}"
            else:
                url = f"https://cdn.discordapp.com/emojis/{thing.id}.png"
                
        elif isinstance(thing, (discord.Member, discord.User)):
            if gif:
                url = str(thing.avatar_url_as(static_format="png", size=512))
            else:
                url = str(thing.avatar_url_as(format="png", size=512))

        elif url is None:
            thing = str(thing).strip("<>")

            if self.bot.url_regex.match(thing):
                url = thing
            else:
                url = await emoji_to_url(thing)
                if url == thing:
                    return False

        if not avatar:
            return None

        if not url:
            return False

        if check:
            async with self.bot.session.get(url) as resp:
                if resp.status != 200:
                    return False

                if "image" not in resp.content_type:
                    return False

                if checktype:
                    b = await resp.content.read(50)
                    if b.startswith(b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A") or b.startswith(b"\x89PNG"): # PNG Signature
                        pass

                    elif b[0:3] == b"\xff\xd8\xff" or b[6:10] in (b"JFIF", b"Exif"):
                        pass

                    elif b.startswith((b"\x47\x49\x46\x38\x37\x61", b"\x47\x49\x46\x38\x39\x61")): # GIF Signature
                        pass

                    elif b[:2] in (b"MM", b"II"):
                        pass

                    elif len(b) >= 3 and b[0] == ord(b"P") and b[1] in b"25" and b[2] in b" \t\n\r":
                        pass

                    elif b.startswith(b"BM"):
                        pass

                    elif not b.startswith(b"RIFF") or b[8:12] != b"WEBP":
                        return False

                    if resp.headers.get("Content-Length") and int(resp.headers.get("Content-Length")) > MAX_FILE_SIZE:
                        return False
        return url

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Utility Loaded")

    @commands.command()
    async def uptime(self, ctx):
        return await ctx.send(f"for {humanize.precisedelta(datetime.datetime.utcnow() - self.bot.launch_time, format='%.0f')} so far")

    @commands.command(help='Add some claps between the given text')
    async def clap(self, ctx, *text: str):
        if len(text) >= 151:
            return await ctx.send(f"{ctx.author.mention} your text is **{len(text)}** characters long, maximum is **150**.")
        s = ''.join([char + "👏" for char in text])
        await ctx.send("👏" + s)

    @commands.command(help="Retrive Covid-19 stats about the specified country!\nLeave the `country` parameter blank to get worldwide stats.")
    async def covid(self, ctx, *, country: str = "world"):
        url = f"https://disease.sh/v3/covid-19/countries/{country}?strict=true"
        if country == "world":
            url = "https://disease.sh/v3/covid-19/all"

        resp = await self.bot.session.get(url)
        data = await resp.json()

        try:
            flag = data["countryInfo"]["flag"] if country != "world" else "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Earth_Western_Hemisphere_transparent_background.png/1200px-Earth_Western_Hemisphere_transparent_background.png"
            total = data["cases"]
            today_cases = data["todayCases"]
            deaths = data["deaths"]
            today_deaths = data["todayDeaths"]
            recovered = data["recovered"]
            today_recovered = data["todayRecovered"]
            active = data["active"]
            critical = data["critical"]
            tests = data["tests"]

            em = discord.Embed(
                description = f"🔎 **Total**: {humanize.intcomma(total)}\n"
                                f"🚑 **Recovered**: {humanize.intcomma(recovered)}\n"
                                f"☠ **Deaths**: {humanize.intcomma(deaths)}\n-----------------------------\n"
                                f"🚩 **Today (Deaths)**: {humanize.intcomma(today_deaths)}\n"
                                f"🏳 **Today (Cases)**: {humanize.intcomma(today_cases)}\n"
                                f"🏴 **Today (Recovered)**: {humanize.intcomma(today_recovered)}\n-----------------------------\n"
                                f"🤒 **Active**: {humanize.intcomma(active)}\n"
                                f"😱 **Critical**: {humanize.intcomma(critical)}\n"
                                f"💉 **Tests**: {humanize.intcomma(tests)}",
                color = self.bot.color)
            em.set_thumbnail(url=flag)
            em.set_author(name=f"Covid in {country.title()}!", icon_url=self.bot.user.avatar_url)

            await ctx.send(embed=em)
        except Exception:
            return await ctx.send(f"{ctx.author.mention} i'm sure that **{country}** is not an existing country so far.")

    @commands.command()
    async def botinfo(self, ctx):

        shards_guilds = {i: 0 for i in range(len(self.bot.shards))}
        for guild in self.bot.guilds:
            shards_guilds[guild.shard_id] += 1

        hdd = psutil.disk_usage('/')
        m = psutil.Process().memory_full_info()
        ram_usage=get_size(m.rss)
        
        em = discord.Embed(
            description=f"**Total Shards**: {len(self.bot.shards)}\n"
            f"**Guild Shard**: #{ctx.guild.shard_id}\n"
            f"**RAM Used**: {ram_usage}\n"
            f"**Total Guilds**: {humanize.intcomma(len(self.bot.guilds))}\n"
            f"**Storage**: {get_size(hdd.used)} / {get_size(hdd.total)}\n",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow())

        em.set_thumbnail(url=self.bot.user.avatar_url)

        for shard_id, shard in self.bot.shards.items():
            em.add_field(name=f"Shard #{shard_id}", value = f"Latency: `{round(shard.latency*1000, 2)}`ms\n"
            f"Guilds: {humanize.intcomma(shards_guilds[shard_id])}")

        await ctx.send(embed=em)

    @commands.command(help=f"Translate the given message to english.\nYou can also reply with the command to a message to translate it.", aliases=["tr"])
    async def translate(self, ctx, *, message: commands.clean_content = None):

        if message is None:
            ref = ctx.message.reference
            if ref and isinstance(ref.resolved, discord.Message):
                message = ref.resolved.content
            else:
                return await ctx.send('<:4318crossmark:848857812565229601> You need to specify also the message to translate.\nYou can also reply to a message with this command to translate it.')

        try:
            trans = await self.bot.loop.run_in_executor(None, self.trans.translate, message)
        except Exception:
            return

        source_laungage = googletrans.LANGUAGES.get(trans.src, '(auto-detected)').title()
        language_destination = googletrans.LANGUAGES.get(trans.dest, 'Unknown').title()
        embed = discord.Embed(title='<:googletransPink:860988658252120084> Translation',
                            description = f"**Original ({source_laungage})**\n{trans.origin}\n\n**Translated ({language_destination})**\n{trans.text}",
                            color=self.bot.color)
        await ctx.send(embed=embed)

    @commands.command(help="Retrive the urban definition for the given term.")
    async def urban(self, ctx, term):
        try:
            async with self.session.get(f"https://api.urbandictionary.com/v0/define?term={term}") as resp:
                d = await resp.json()
                definition = d['list'][0]['definition']
                example = d['list'][0]['example']
                t_up = d['list'][0]['thumbs_up']
                t_down = d['list'][0]['thumbs_down']
                author = d['list'][0]['author']
                url_ref = d['list'][0]['permalink']
                word = d['list'][0]['word']

            em = discord.Embed(description=f"**Urban definition for [{word}]({url_ref})**\n\n Written By **`{author}`**\n\n__**Definition**__\n{definition}\n\n__**Example**__\n{example}", color = self.bot.color)
            em.set_footer(text=f"👍 {t_up} | 👎 {t_down}")
            return await ctx.send(embed=em)
        except Exception:
            return await ctx.send(f"{ctx.author.mention} no urban results found for **{term}**.")

    @commands.command(help="Convert the given phrase to binary format.")
    async def binary(self, ctx, *, to_convert:str):
        return await ctx.safe_send(" ".join(f"`{ord(i):08b}`" for i in to_convert))


    @commands.command(help="Generate a random password giving an appropriate length which can't be over 75.", aliases = ["psw", "pass", "passw", "passwd"])
    async def password(self, ctx, length:int=None):
        if length is None:
            length = 17

        if length == 76 or length == 0:
            return await ctx.reply("<:4318crossmark:848857812565229601> Lenght must be between 1 and 75")

        password_length = length
        try:
            await ctx.reply("<:4430checkmark:848857812632076314> Check your DMs!", mention_author=False)
            return await ctx.author.send(f"<:4430checkmark:848857812632076314> Hi buddy, that's your generated password:\n`{secrets.token_urlsafe(password_length)}`")
        except Exception:
            return await ctx.send(f"<:4318crossmark:848857812565229601> Can't send DMs to **{ctx.author.name}**.")

    @commands.command()
    @is_team()
    async def topguilds(self, ctx):

        msg = await ctx.send(f"{ctx.author.mention}, this command can be a little spammy, are you sure you want to execute it?\nClick the reaction in **30** seconds to continue.")
        await msg.add_reaction("<:check:819702267476967444>")

        def check(payload):
            return payload.message_id == msg.id and payload.emoji.name == "check" and payload.user_id == ctx.author.id

        try:
            payload = await self.bot.wait_for("raw_reaction_add", check=check, timeout=30)
        except asyncio.TimeoutError:
            return await msg.delete()

        await msg.delete()

        final = sorted(self.bot.guilds, key=lambda m: m.member_count, reverse=True)
        index = 0
        for guild in final:
            if "VANITY_URL" in guild.features:
                if guild.me.guild_permissions.manage_guild:
                    vanity = (await guild.vanity_invite()) and "Can't get the vanity due issues."
                else:
                    vanity = "No perms to get the Vanity URL"
            else:
                vanity = "No Vanity URL"

            desc = "This guild has no description set."
            if guild.description:
                desc = guild.description

            em = discord.Embed(title=f"{guild.name} (`{guild.id}`)", description=f"The guild owner is `{guild.owner}`\n{desc}\n\n<a:Casual_Crowe:853894751140446248> Members : {guild.member_count}\n<a:Casual_Crowe:853894751140446248> Emojis : {len(guild.emojis)}\n<a:Casual_Crowe:853894751140446248> Boosts & Tier : {guild.premium_subscription_count} / {guild.premium_tier}\n<a:Casual_Crowe:853894751140446248> Vanity URL : {vanity}\n<a:Casual_Crowe:853894751140446248> Text & Voice : <:text:843198832464625714> {len(guild.text_channels)} | <:voice:585783907673440266> {len(guild.voice_channels)}", color = self.bot.color)
            em.set_thumbnail(url=guild.icon_url)
            if guild.banner_url:
                em.set_image(url=guild.banner_url)

            await ctx.send(embed=em)
            index += 1
            if index >= 10:
                break

    @commands.command(aliases=["sys"])
    @is_team()
    async def system(self, ctx):
        """Get system informations"""
        uname = platform.uname()
        system_name = uname.system
        node_name = uname.node
        machine = uname.machine
        processor = uname.processor


        """Get the boot system time and convert
        it into a readable format."""
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.datetime.fromtimestamp(boot_time_timestamp)
        conv_boot = f"{bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}"

        """Get some CPU informations here"""
        # number of cores
        physical_cores = psutil.cpu_count(logical=False)
        total_cores = psutil.cpu_count(logical=True)

        # CPU frequencies
        cpufreq = psutil.cpu_freq()
        current_cpu_freq = f"{cpufreq.current:.2f}Mhz"

        # CPU usage
        cpu_usage = f"{psutil.cpu_percent()}%" 

        """Get some memory informations here"""
        # get the memory details
        svmem = psutil.virtual_memory()
        total_mem = f"{get_size(svmem.total)}"
        available_mem = f"{get_size(svmem.available)}"
        used_mem = f"{get_size(svmem.used)}"
        mem_perc = f"{svmem.percent}%"

        # get the swap memory details (if exists)
        swap = psutil.swap_memory()
        total_swap = f"{get_size(swap.total)}"
        free_swap = f"{get_size(swap.free)}"
        used_swap = f"{get_size(swap.used)}"
        perc_swap = f"{swap.percent}%"

        """Get some disk io informations here"""
        # get IO statistics since boot
        disk_io = psutil.disk_io_counters()
        disk_io_bytes_read = f"{get_size(disk_io.read_bytes)}"
        disk_io_bytes_send = f"{get_size(disk_io.write_bytes)}"

        """Get some network informations here"""
        net_io = psutil.net_io_counters()
        net_io_bytes_sent = f"{get_size(net_io.bytes_sent)}"
        net_io_bytes_recv = f"{get_size(net_io.bytes_recv)}"

        line_counter = line_count()

        em = discord.Embed(color = self.bot.color)
        em.add_field(name="System", value=f"```prolog\nName: {system_name}\nNode: {node_name}\nMachine: {machine}\nProcessor: {processor}\n```")
        em.add_field(name="CPU", value=f"```prolog\nPhysical Cores: {physical_cores}\nTotal Cores: {total_cores}\nFreq: {current_cpu_freq}\nUsage: {cpu_usage}\n```")
        em.add_field(name="Memory", value=f"```prolog\nTotal: {total_mem}\nAvailable: {available_mem}\nUsed: {used_mem}\nPercentage: {mem_perc}\n```")
        em.add_field(name="Swap", value=f"```prolog\nTotal: {total_swap}\nFree: {free_swap}\nUsed: {used_swap}\nPercentage: {perc_swap}\n```")
        em.add_field(name="Network (DISK & NET)", value=f"```prolog\nRead: {disk_io_bytes_read}\nSent: {disk_io_bytes_send}\nSent: {net_io_bytes_sent}\nReceived: {net_io_bytes_recv}\n```")
        em.add_field(name="Code", value=f"```prolog\n{line_counter}\n```")


        em.set_footer(text=f"System Boot : {conv_boot}")
        await ctx.send(embed=em)

    @commands.command(help="See information about me, who have designed me, and other stuff like guilds & members, vps usage & commands.", aliases=["about", "stats"])
    async def info(self, ctx):
        cpu_usage = psutil.cpu_percent()
        m = psutil.Process().memory_full_info()
        ram_usage=humanize.naturalsize(m.rss)
        cmds = len(list(self.bot.walk_commands()))
        vc = sum(len(guild.voice_channels) for guild in self.bot.guilds)
        txt = sum(len(guild.text_channels) for guild in self.bot.guilds)

        time_1 = time.perf_counter()
        await ctx.trigger_typing()
        time_2 = time.perf_counter()
        ping = round((time_2-time_1)*1000)

        em = discord.Embed(description="[**Support Server**](https://discord.gg/ZcErEwmVYu)", color = self.bot.color)
        em.add_field(name="<:settings:585767366743293952> Channels", value=f"<:voice:585783907673440266> Voice: `{vc}`\n<:text:843198832464625714> Text: `{txt}`")
        em.add_field(name="<:settings:585767366743293952> Stats", value=f"<:upward_stonks:739614245997641740> Guilds: `{len(self.bot.guilds)}`\n<:upward_stonks:739614245997641740> Users: `{len(self.bot.users)}`",inline=False)
        em.add_field(name="<:settings:585767366743293952> Latency", value=f"<:greenTick:596576670815879169> Websocket: `{round(self.bot.latency*1000, 2)}ms`\n<:greenTick:596576670815879169> Typing: `{ping}ms`", inline=False)
        em.add_field(name="<:settings:585767366743293952> VPS (Usage)", value=f"<:rich_presence:658538493521166336> RAM: `{ram_usage}`\n<:rich_presence:658538493521166336> CPU: `{cpu_usage}%`")
        em.add_field(name="<:settings:585767366743293952> Commands", value=f"<:upward_stonks:739614245997641740> Total Commands: `{cmds}`\n<:upward_stonks:739614245997641740> Invoked: `{self.bot.command_counter}`",inline=False)
        em.set_thumbnail(url=self.bot.user.avatar_url)
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)

    @commands.command(help="Get information about the guild where this commmand get executed.", aliases=["si"])
    async def serverinfo(self, ctx):

        format = "%a, %d %b %Y %I:%M %p"

        afk_channel = ctx.guild.afk_channel or "No AFK Channel."
        afk_timeout = ctx.guild.afk_timeout or "No AFK Timeout."
        banner = f"[Click Here!]({ctx.guild.banner_url})" if ctx.guild.banner_url else "No Banner."
        bitrate = f"{humanize.naturalsize(ctx.guild.bitrate_limit, True)}/s"
        categories = len(ctx.guild.categories)
        channels = len(ctx.guild.channels)
        created = ctx.guild.created_at.strftime(format)
        since = humanize.naturaltime(ctx.guild.created_at)
        default_role = ctx.guild.default_role or "No Default Role"
        desc = ctx.guild.description or "No Description"
        emoji_limit = ctx.guild.emoji_limit
        ecf = ctx.guild.explicit_content_filter or "No Explicit Filter"
        filesize_limit = f"{humanize.naturalsize(ctx.guild.filesize_limit)}"
        icon = ctx.guild.icon_url
        id = ctx.guild.id
        max_members = ctx.guild.max_members
        members = ctx.guild.member_count
        mfa_level = ctx.guild.mfa_level or "No MFA"
        name = ctx.guild.name
        owner = self.bot.get_user(ctx.guild.owner_id) or (await self.bot.fetch_user(ctx.guild.owner_id))
        p_count = ctx.guild.premium_subscription_count or "N/A"
        p_role = ctx.guild.premium_subscriber_role.mention if ctx.guild.premium_subscriber_role else "N/A"
        p_tier = ctx.guild.premium_tier
        region = ctx.guild.region
        v_level = ctx.guild.verification_level


        em = discord.Embed(
            title=name, 
            url=icon,
            description = f"**`{id}`** (Owner : {owner.mention if owner else 'Unknown'})\n{desc}\n\n"
                        f"<:8790dash:848857813111668817> **AFK Channel** : {afk_channel}\n"
                        f"<:8790dash:848857813111668817> **AFK Timeout** : {afk_timeout}\n"
                        f"<:8790dash:848857813111668817> **Banner** : {banner}\n"
                        f"<:8790dash:848857813111668817> **Bitrate** : {bitrate}\n"
                        f"<:8790dash:848857813111668817> **Categories** : {categories}\n"
                        f"<:8790dash:848857813111668817> **Channels** : {channels}\n"
                        f"<:8790dash:848857813111668817> **Created** : {created} ({since})\n"
                        f"<:8790dash:848857813111668817> **Default Role** : {default_role}\n"
                        f"<:8790dash:848857813111668817> **Emojis Limit** : {emoji_limit}\n"
                        f"<:8790dash:848857813111668817> **Explicit Content Filter** : {ecf}\n"
                        f"<:8790dash:848857813111668817> **Filesize Limit** : {filesize_limit}\n"
                        f"<:8790dash:848857813111668817> **Max Members** : {max_members}\n"
                        f"<:8790dash:848857813111668817> **Members** : {members}\n"
                        f"<:8790dash:848857813111668817> **MFA** : {mfa_level}\n"
                        f"<:8790dash:848857813111668817> **Boosts** : {p_count}\n"
                        f"<:8790dash:848857813111668817> **Nitro Role** : {p_role}\n"
                        f"<:8790dash:848857813111668817> **Guild Tier** : {p_tier}\n"
                        f"<:8790dash:848857813111668817> **Region** : {region}\n"
                        f"<:8790dash:848857813111668817> **Verification Level** : {v_level}", color = self.bot.color
        )

        em.set_thumbnail(url=icon)
        if ctx.guild.banner:
            em.set_image(url=ctx.guild.banner_url)
        await ctx.send(embed=em)

    @commands.command(help="See info about a member", aliases=["ui"])
    async def userinfo(self, ctx, *, user: discord.Member = None):
        if user is None:
            user = ctx.author
        
        if user not in ctx.guild.members:
            return await ctx.send(f"{ctx.author.mention} this user is not in the guild.")

        date_format = "%a, %d %b %Y %I:%M %p"

        if len(user.roles) > 1:
            role_string = ' '.join([r.mention for r in user.roles][1:])
        else:
            role_string = "No roles."


        flags_valid = {
            "bug_hunter": "<:bughunter:585765206769139723>",
            "bug_hunter_level_2": "<:DiscordGoldBug:813372529879679046>",
            "early_supporter": "<:supporter:585763690868113455>",
            "early_verified_bot_developer": "<:verifiedbotdev:853277205264859156>",
            "hypesquad": "<:hypesquad_events:585765895939424258>",
            "hypesquad_balance": "<:balance:585763004574859273>",
            "hypesquad_bravery": "<:bravery:585763004218343426>",
            "hypesquad_brilliance": "<:brilliance:585763004495298575>",
            "partner": "<:partner_old:748662699772346450>",
            "staff": "<:Discord_Staff:828196998951337984>",
            "verified_bot": "<:VerifiedBOT:730717381445419028>",
            "verified_bot_developer": "<:verifiedbotdev:853277205264859156>"
            }

        flags_user = [badge for badge, value in user.public_flags if value]

        flags = []

        if flags_user:
            for i in flags_user:
                if i in flags_valid:
                    flags.append(f"{flags_valid[i]}")
        else:
            flags.append("No Badges")

        perm_string = ', '.join([str(p[0]).replace("_", " ").title() for p in user.guild_permissions if p[1]])
        
            
        boosting = "Not Boosting"
        if user.premium_since:
            boosting = f"Boosting The Server (Since {humanize.naturaltime(user.premium_since)})"
            flags.append("<:booster3:585764446220189716>")
            flags.append("<:nitro:314068430611415041>")

        nickname = "No Nickname"
        if user.nick:
            nickname = user.nick

        joined = sorted(ctx.guild.members, key=lambda m: m.joined_at, reverse=False).index(user) + 1

        embed = discord.Embed(color=0xdfa3ff, description=f"<:gsarrow:819706480714055681> **ID** » {user.id}\n"
                                                        f"<:gsarrow:819706480714055681> **Joined** » {user.joined_at.strftime(date_format)} ({humanize.naturaltime(user.joined_at)})\n"
                                                        f"<:gsarrow:819706480714055681> **Join Position** » {joined} (In {ctx.guild.member_count} members)\n"
                                                        f"<:gsarrow:819706480714055681> **Nickname** » {nickname}\n"
                                                        f"<:gsarrow:819706480714055681> **Registered** » {user.created_at.strftime(date_format)} ({humanize.naturaltime(user.created_at)})\n"
                                                        f"<:gsarrow:819706480714055681> **Boosting** » {boosting}\n\n"
                                                        f"<:gsarrow:819706480714055681> **Badges** » {' '.join(flags)}\n"
                                                        f"<:gsarrow:819706480714055681> **Roles [{(len(user.roles)-1)}]** » {role_string}\n"
                                                        f"<:gsarrow:819706480714055681> **Top-Role** » {f'<@&{user.top_role.id}>' if user.roles[1:] else 'No Roles'}\n\n"
                                                        f"<:gsarrow:819706480714055681> **Guild Permissions** » {perm_string}")

        embed.set_author(name=str(user), icon_url=user.avatar_url)
        embed.set_thumbnail(url=user.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=embed)

    @commands.command(help="Search something on google", aliases=["ggl"])
    @premium(override=True)
    async def google(self, ctx, *, query):
        try:
            lat = (round(self.bot.latency*1000, 2))
            client = async_cse.Search("AIzaSyChzFV6odUmQh7nPp34laGuniYwdlJjSV4") # create the Search client (uses Google by default!)
            results = await client.search(f"{query}", safesearch=True) # returns a list of async_cse.Result objects
            first_result = results[0] # Grab the first result
            second_result = results[1] # Grab the second result
            tirth_result = results[2] # Grab the tirth result
            em = discord.Embed(description = f"Results for: **{query}**", color = 0x2F3136)
            em.add_field(name=f"{first_result.title}\n{first_result.url}", value = first_result.description, inline = False)
            em.add_field(name=f"{second_result.title}\n{second_result.url}", value = second_result.description, inline = False)
            em.add_field(name=f"{tirth_result.title}\n{tirth_result.url}", value = tirth_result.description, inline = False)
            em.set_footer(text=f"Safe search = Enabled | Latency = {lat}ms.", icon_url=f"{self.bot.user.avatar_url}") # Title, snippet, URL, and Image URL (if specified)
            await ctx.send(embed=em)
        except Exception:
            return await ctx.send(f"The search for **{query}** returned 0 results.")

    @commands.command(help="Donate something to support me")
    async def donate(self, ctx):
        em = discord.Embed(title="Thanks for considering donating!", description="Donations are totally managed by DonateBot and they will not give you any advantage in Ami, also if you are in the support server you can get special roles donating!\nAllowed methods to donate are currently only <:paypal:820778999549657138> **PayPal** (creating an account requires 5 minutes, and you can associate a card to pay with that with paypal)\nTo donate simply [click here!](https://donatebot.io/checkout/800176902765674496)\nIf you wish, you could also get Ami [premium!](https://amidiscord.xyz/premium)", color = self.bot.color)
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)

    @commands.command(help="Send a support request to the ami mods")
    async def support(self, ctx):
        await ctx.send("Need help? Join now in the support server.\nhttps://discord.gg/ZcErEwmVYu")

    @commands.command(help="Check a pic to retrive SFW & NSFW score, works with urls, @members and attachments")
    @premium(override=True)
    async def check(self, ctx, member: typing.Union[Image_Union]=None):
        url = await self.get_url(ctx, member)

        if url is False:
            return await ctx.reply(f":x: Something went wrong while parsing the image, could be an invalid file type or a file larger then {humanize.naturalsize(MAX_FILE_SIZE)}.")

        resp = await self.bot.session.get(url)
        if resp.status == 200:
            f = await aiofiles.open('check.png', mode='wb')
            await f.write(await resp.read())
            await f.close()

        classifier = NudeClassifier()
        classs = classifier.classify("check.png")
        dict1 = classs["check.png"]
        unsafe = dict1['unsafe']
        safe = dict1['safe']
        safec = ((safe)*100)/200
        unsafec = ((unsafe)*100)/200
        unsafep = round(unsafec*200,2)
        safep = round(safec*200,2)
        em = discord.Embed(color=self.bot.color)
        em.add_field(name="<:status_online:596576749790429200> Safe score", value = f"{safe} `({safep}%)`")
        em.add_field(name="<:status_dnd:596576774364856321> Unsafe score", value = f"{unsafe} `({unsafep}%)`")
        em.set_image(url=url)
        em.set_footer(text="Image NSFW Detection | Safe = SFW  | Unsafe = NSFW")
        await ctx.send(embed=em)



    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        self.bot.command_counter += 1
        self.bot.commandsusages[ctx.command.qualified_name] += 1

    @commands.command(help="See the commands usage")
    @is_team()
    async def cmdus(self, ctx):
        lists = []
        lists.append(f"Total usages » {self.bot.command_counter}")
        for i, (n, v) in enumerate(self.bot.commandsusages.most_common()):
            lists.append(f"{n:<30} {v:<15}")
        paginator = WrappedPaginator(max_size=1024, prefix="```coffeescript", suffix="```")
        paginator.add_line("\n".join(lists))
        interface = PaginatorEmbedInterface(ctx.bot, paginator, owner=ctx.author)
        return await interface.send_to(ctx)

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
    bot.add_cog(Utility(bot))

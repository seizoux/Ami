import discord
from discord.ext import commands, menus
from nudenet import NudeClassifier
import typing
from urllib.request import urlretrieve
import datetime
import aiofiles
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

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "Utility"
        self.session = aiohttp.ClientSession()
        self.bot.command_counter = 0
        self.bot.commandsusages = Counter()
        self.trans = googletrans.Translator()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Utility Loaded")

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
                            color=0xffcff1)
        await ctx.send(embed=embed)

    @commands.command(help="Retrive the urban definition for the given term.")
    async def urban(self, ctx, term):
        async with self.session.get(f"https://api.urbandictionary.com/v0/define?term={term}") as resp:
            d = await resp.json()
            definition = d['list'][0]['definition']
            example = d['list'][0]['example']
            t_up = d['list'][0]['thumbs_up']
            t_down = d['list'][0]['thumbs_down']
            author = d['list'][0]['author']
            written = d['list'][0]['written_on']
            url_ref = d['list'][0]['permalink']
            word = d['list'][0]['word']

        format = "%a, %d %b %Y %I:%M %p"

        em = discord.Embed(description=f"**Urban definition for [{word}]({url_ref})**\n\n Written By **`{author}`**\n\n__**Definition**__\n{definition}\n\n__**Example**__\n{example}", color = 0xffcff1)
        em.set_footer(text=f"👍 {t_up} | 👎 {t_down}")
        return await ctx.send(embed=em)

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

            em = discord.Embed(title=f"{guild.name} (`{guild.id}`)", description=f"The guild owner is `{guild.owner}`\n{desc}\n\n<a:Casual_Crowe:853894751140446248> Members : {guild.member_count}\n<a:Casual_Crowe:853894751140446248> Emojis : {len(guild.emojis)}\n<a:Casual_Crowe:853894751140446248> Boosts & Tier : {guild.premium_subscription_count} / {guild.premium_tier}\n<a:Casual_Crowe:853894751140446248> Vanity URL : {vanity}\n<a:Casual_Crowe:853894751140446248> Text & Voice : <:text:843198832464625714> {len(guild.text_channels)} | <:voice:585783907673440266> {len(guild.voice_channels)}", color = 0xffcff1)
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

        em = discord.Embed(color = 0xffcff1)
        em.add_field(name="System", value=f"```prolog\nName : {system_name}\nNode : {node_name}\nMachine : {machine}\nProcessor : {processor}\n```")
        em.add_field(name="CPU", value=f"```prolog\nPhysical Cores : {physical_cores}\nTotal Cores : {total_cores}\nFreq : {current_cpu_freq}\nUsage : {cpu_usage}\n```")
        em.add_field(name="Memory", value=f"```prolog\nTotal : {total_mem}\nAvailable : {available_mem}\nUsed : {used_mem}\nPercentage : {mem_perc}\n```")
        em.add_field(name="Swap", value=f"```prolog\nTotal : {total_swap}\nFree : {free_swap}\nUsed : {used_swap}\nPercentage : {perc_swap}\n```")
        em.add_field(name="Network (DISK & NET)", value=f"```prolog\nRead : {disk_io_bytes_read}\nSent : {disk_io_bytes_send}\nSent : {net_io_bytes_sent}\nReceived : {net_io_bytes_recv}\n```")
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

        alvin = "[`Cryptex#0117`](https://discordapp.com/users/590323594744168494)"
        jadon = "[`Jadon#2494`](https://discordapp.com/users/711057339360477184)"
        moanie = "[`ムーニー#6598`](https://discordapp.com/users/691406006277898302)"
        ali = "[`Ali™#9171`](https://discordapp.com/users/410452466631442443)"
        crunchy = "[`CrunchyAnime#3992`](https://discordapp.com/users/343019667511574528)"

        em = discord.Embed(description="[**Support Server**](https://discord.gg/ZcErEwmVYu)\nThis bot has been designed and developed by [`Daishiky#0828`](http://discordapp.com/users/144126010642792449)\n"
                           f"Team : {alvin}, {jadon}, {moanie}, {ali}, {crunchy}",color = 0xffcff1)
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
        owner = self.bot.get_user(ctx.guild.owner_id)
        p_count = ctx.guild.premium_subscription_count
        p_role = ctx.guild.premium_subscriber_role.mention
        p_tier = ctx.guild.premium_tier
        region = ctx.guild.region
        v_level = ctx.guild.verification_level


        em = discord.Embed(
            title=name, 
            url=icon,
            description = f"**`{id}`** (Owner : {owner.mention})\n{desc}\n\n"
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
                        f"<:8790dash:848857813111668817> **Verification Level** : {v_level}", color = 0xffcff1
        )

        em.set_thumbnail(url=icon)
        if ctx.guild.banner:
            em.set_image(url=ctx.guild.banner_url)
        await ctx.send(embed=em)

    @commands.command(help="See info about a member", aliases=["ui"])
    async def userinfo(self, ctx, *, user: discord.Member = None):
        if user is None:
            user = ctx.author
        
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
        except async_cse.NoMoreRequests:
            return await ctx.send("Limit of 100 search reached for today.")

    @commands.command(help="Donate something to support me")
    async def donate(self, ctx):
        donate = "[Click Here](https://donatebot.io/checkout/800176902765674496)"
        cancel = "[Click Here](https://discord.com/users/144126010642792449)"
        em = discord.Embed(color = 0xffcff1)
        em.add_field(name="<:paypal:820778999549657138> Donate <:paypal:820778999549657138>", value = f"{donate}")
        em.add_field(name="<:4228_discord_bot_dev:819689871307440200> Developer <:4228_discord_bot_dev:819689871307440200>", value = f"{cancel}")
        em.set_footer(text=f"{ctx.author.name}'s request.", icon_url=ctx.author.avatar_url)
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)


    @commands.command(help="Send a support request to the ami mods")
    async def support(self, ctx):
        await ctx.send("Need help? Join now in the support server.\nhttps://discord.gg/ZcErEwmVYu")

    @commands.command(help="Check a pic to retrive SFW & NSFW score, works with urls, @members and attachments")
    async def check(self, ctx, member: typing.Optional[typing.Union[discord.Member, str]]):
        if attachment := ctx.message.attachments:
            try:
                url = attachment[0]
                filename = "check.png"
                await url.save(filename)
                classifier = NudeClassifier()
                classs = classifier.classify("check.png")
                dict1 = classs["check.png"]
            except Exception:
                return await ctx.reply("No", mention_author=False)
            unsafe = dict1['unsafe']
            safe = dict1['safe']
            safec = ((safe)*100)/200
            unsafec = ((unsafe)*100)/200
            unsafep = round(unsafec*200,2)
            safep = round(safec*200,2)
            f = discord.File("check.png")
            em = discord.Embed(color=0xffcff1)
            em.add_field(name="<:status_online:596576749790429200> Safe score", value = f"{safe} `({safep}%)`")
            em.add_field(name="<:status_dnd:596576774364856321> Unsafe score", value = f"{unsafe} `({unsafep}%)`")
            em.set_image(url="attachment://check.png")
            em.set_footer(text="Image NSFW Detection | Safe = SFW  | Unsafe = NSFW")
            await ctx.send(file=f, embed=em)
            return

        if member == None:
            url = ctx.author.avatar_url
            filename = "check.png"
            await url.save(filename)
            classifier = NudeClassifier()
            classs = classifier.classify("check.png")
            dict1 = classs["check.png"]
            unsafe = dict1['unsafe']
            safe = dict1['safe']
            safec = ((safe)*100)/200
            unsafec = ((unsafe)*100)/200
            unsafep = round(unsafec*200,2)
            safep = round(safec*200,2)
            em = discord.Embed(color=0xffcff1)
            em.add_field(name="<:status_online:596576749790429200> Safe score", value = f"{safe} `({safep}%)`")
            em.add_field(name="<:status_dnd:596576774364856321> Unsafe score", value = f"{unsafe} `({unsafep}%)`")
            em.set_image(url=url)
            em.set_footer(text="Image NSFW Detection | Safe = SFW  | Unsafe = NSFW")
            await ctx.send(embed=em)
        elif isinstance(member, discord.Member) or isinstance(member, discord.User):
            url = member.avatar_url
            filename = "check.png"
            await url.save(filename)
            classifier = NudeClassifier()
            classs = classifier.classify("check.png")
            dict1 = classs["check.png"]
            unsafe = dict1['unsafe']
            safe = dict1['safe']
            safec = ((safe)*100)/200
            unsafec = ((unsafe)*100)/200
            unsafep = round(unsafec*200,2)
            safep = round(safec*200,2)
            em = discord.Embed(color=0xffcff1)
            em.add_field(name="<:status_online:596576749790429200> Safe score", value = f"{safe} `({safep}%)`")
            em.add_field(name="<:status_dnd:596576774364856321> Unsafe score", value = f"{unsafe} `({unsafep}%)`")
            em.set_image(url=url)
            em.set_footer(text="Image NSFW Detection | Safe = SFW  | Unsafe = NSFW")
            await ctx.send(embed=em)
        else:
            if member.startswith("https"):
                url = member
                url.replace("cdn.discordapp.com", "media.discordapp.net")
                async with aiohttp.ClientSession().get(url) as resp:

                    if resp.status != "200":
                        return await ctx.send(":x: Invalid Picture")
                    if not "image" in resp.content_type:
                        return await ctx.send(":x: Invalid Picture")
                    if resp.headers.get("Content-Length") and int(resp.headers.get("Content-Length")) > 15000000:
                        return await ctx.send(":x: Max size for images are **`15 MB`**")

                    bobo = await resp.read()
                    async with aiofiles.open("check.png", "wb") as f:
                        await f.write(bobo)

                    classifier = NudeClassifier()
                    classs = classifier.classify("check.png")
                    dict1 = classs["check.png"]
                    unsafe = dict1['unsafe']
                    safe = dict1['safe']
                    safec = ((safe)*100)/200
                    unsafec = ((unsafe)*100)/200
                    unsafep = round(unsafec*200,2)
                    safep = round(safec*200,2)
                    em = discord.Embed(color=0xffcff1)
                    em.add_field(name="<:status_online:596576749790429200> Safe score", value = f"{safe} `({safep}%)`")
                    em.add_field(name="<:status_dnd:596576774364856321> Unsafe score", value = f"{unsafe} `({unsafep}%)`")
                    em.set_image(url=url)
                    em.set_footer(text="Image NSFW Detection | Safe = SFW  | Unsafe = NSFW")
                    await ctx.send(embed=em)
            else:
                return await ctx.send(":x: Image not found / unsupported provided image.")



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

import discord
from discord.errors import NotFound
from discord.ext import commands
import alexflipnote
import aiozaneapi
from nudenet import NudeClassifier
import typing
from urllib.request import urlretrieve
import datetime
import aiofiles
import aiohttp
import asyncio
import humanize
import psutil
import async_cse
import time
from jishaku.paginators import WrappedPaginator, PaginatorInterface
from collections import Counter

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "Utility"
        self.bot.command_counter = 0
        self.bot.commandsusages = Counter()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Utility Loaded")

    @commands.command(help="Suggest new feature for ami")
    async def feature(self, ctx):
        user_id = str(f"{ctx.author.id}")
        db = await self.bot.pg_con.fetchrow("SELECT * FROM blacklist WHERE user_id = $1", user_id)
        if db:
            try:
                reason = db["reason"]
                em = discord.Embed(description=f"**{ctx.author.name}**, you're blacklisted from the bot. You can't use `ami feature & ami support`. If you think this is a mistake, feel free to reach the support team.\nReason: **`{reason}`**", color=0xffcff1)
                em.set_footer(text="https://discord.gg/ZcErEwmVYu")
                return await ctx.author.send(embed=em)
            except Exception:
                em = discord.Embed(description=f"**{ctx.author.name}**, you're blacklisted from the bot. You can't use `ami feature & ami support`. If you think this is a mistake, feel free to reach the support team.\nReason: **`{reason}`**", color=0xffcff1)
                em.set_footer(text="https://discord.gg/ZcErEwmVYu")
                return await ctx.send(embed=em)

        channel = self.bot.get_channel(805892487503413310)
        msg1 = "ami nvm"
        msg2 = "ami feature"
        await ctx.send("<:qmark:819702268479012974> Ok! Now send the feature u want to be added in Ami: you have `1 minute`. Use **ami nvm** to cancel the request.")

        try:
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel, timeout=60.0)

        except asyncio.TimeoutError:
            await ctx.send("<:allert:819708576796114994> Times Up!")
            return

        if msg.content == msg1:
            try:
                await ctx.send("<:vea:819703490703523860> Alright! Feature request deleted.")
                await ctx.message.delete()
                return
            except Exception:
                return

        if msg.content == msg2:
            await ctx.send("<:vea:819703490703523860> What are u trying to do? You can't send `ami feature` with `ami feature`, try again.")
            await ctx.message.delete()
            return
            
        if msg:
            await ctx.send("<:check:819702267476967444> Perfect! The feature has been forwarded to #features in the support server.")
            fmt = '%d/%m/%Y - %H:%m'
            time = datetime.datetime.utcnow()
            t3 = (time.strftime(fmt))
            em = discord.Embed(title="New feature requested!", color = 0xffcff1)
            em.add_field(name="Requested by", value =f"{ctx.author.name}#{ctx.author.discriminator}")
            em.add_field(name="Date", value = f"{t3}")
            em.add_field(name="Feature Message", value =f"{msg.content}", inline = False)
            em.set_footer(text=f"ID : {ctx.author.id}")
            react = await channel.send(embed=em)
            await react.add_reaction("<a:4214_yes_tick:819689871156445245>")
            await react.add_reaction("<a:no:819689870284816415>")

    @commands.command(help="See info about me and my dev")
    async def info(self, ctx):
        cpu_usage = psutil.cpu_percent()
        m = psutil.Process().memory_full_info()
        ram_usage=humanize.naturalsize(m.rss)
        cmds = len(list(self.bot.walk_commands()))
        vc = sum(len(guild.voice_channels) for guild in self.bot.guilds)
        txt = sum(len(guild.text_channels) for guild in self.bot.guilds)
        supp = "https://discord.gg/ZcErEwmVYu"

        count = 0
        for cmd in self.bot.commands:
            try:
                await cmd.can_run(ctx)
                count += 1
            except:
                continue

        time_1 = time.perf_counter()
        await ctx.trigger_typing()
        time_2 = time.perf_counter()
        ping = round((time_2-time_1)*1000)

        em = discord.Embed(color = 0xffcff1)
        em.add_field(name="<:settings:585767366743293952> Channels", value=f"<:voice:585783907673440266> Voice: `{vc}`\n<:text:843198832464625714> Text: `{txt}`")
        em.add_field(name="<:settings:585767366743293952> Stats", value=f"<:upward_stonks:739614245997641740> Guilds: `{len(self.bot.guilds)}`\n<:upward_stonks:739614245997641740> Users: `{len(self.bot.users)}`",inline=False)
        em.add_field(name="<:settings:585767366743293952> Latency", value=f"<:greenTick:596576670815879169> Websocket: `{round(self.bot.latency*1000, 2)}ms`\n<:greenTick:596576670815879169> Typing: `{ping}ms`", inline=False)
        em.add_field(name="<:settings:585767366743293952> VPS (Usage)", value=f"<:rich_presence:658538493521166336> RAM: `{ram_usage}`\n<:rich_presence:658538493521166336> CPU: `{cpu_usage}%`")
        em.add_field(name="<:settings:585767366743293952> Commands", value=f"<:upward_stonks:739614245997641740> Total Commands: `{cmds}`\n<:upward_stonks:739614245997641740> Runnable by you: `{count}`\n<:upward_stonks:739614245997641740> Invoked: `{self.bot.command_counter}`",inline=False)
        em.set_thumbnail(url=self.bot.user.avatar_url)
        em.set_footer(text=f"Support: {supp}", icon_url=ctx.author.avatar_url)
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)
        return

    @commands.command(help="See info about a member", aliases=["ui"])
    async def userinfo(self, ctx, *, user: discord.Member = None):
        if user is None:
            user = ctx.author
        
        date_format = "%a, %d %b %Y %I:%M %p"


        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        if len(user.roles) > 1:
            role_string = ' '.join([r.mention for r in user.roles][1:])
        else:
            role_string = "No roles."
        perm_string = ', '.join([str(p[0]).replace("_", " ").title() for p in user.guild_permissions if p[1]])
        embed = discord.Embed(color=0xdfa3ff, description=f"<:gsarrow:819706480714055681> **ID** » `{user.id}`\n<:gsarrow:819706480714055681> **Joined** » `{user.joined_at.strftime(date_format)}`\n<:gsarrow:819706480714055681> **Registered** » `{user.created_at.strftime(date_format)}`\n<:gsarrow:819706480714055681> **Roles [{(len(user.roles)-1)}]** » {role_string}")
        embed.add_field(name="Guild permissions", value=f"```css\n{perm_string}\n```", inline=False)
        embed.set_author(name=str(user), icon_url=user.avatar_url)
        embed.set_thumbnail(url=user.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=embed)

    @commands.command(help="Search something on google")
    async def ggl(self, ctx, *, query):
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
        user_id = str(f"{ctx.author.id}")
        db = await self.bot.pg_con.fetchrow("SELECT * FROM blacklist WHERE user_id = $1", user_id)
        if db:
            try:
                reason = db["reason"]
                em = discord.Embed(description=f"**{ctx.author.name}**, you're blacklisted from the bot. You can't use `ami feature & ami support`. If you think this is a mistake, feel free to reach the support team.\nReason: **`{reason}`**", color=0xffcff1)
                em.set_footer(text="https://discord.gg/ZcErEwmVYu")
                return await ctx.author.send(embed=em)
            except Exception:
                em = discord.Embed(description=f"**{ctx.author.name}**, you're blacklisted from the bot. You can't use `ami feature & ami support`. If you think this is a mistake, feel free to reach the support team.\nReason: **`{reason}`**", color=0xffcff1)
                em.set_footer(text="https://discord.gg/ZcErEwmVYu")
                return await ctx.send(embed=em)

        channel = self.bot.get_channel(810625559868342353)
        msg1 = "ami nvm"
        ms = await ctx.send("<:qmark:819702268479012974> Ok! Now send the message u want to send at the support, you have `1 minute`. Use **ami nvm** if u don't need support.")

        try:
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel, timeout=60.0)

        except asyncio.TimeoutError:
            await ctx.send("<:timealert:819702268457648148> Times Up!")
            return

        if msg.content == msg1:
            await ctx.send("<:vea:819703490703523860> Alright! Support request deleted.")
            await ms.delete()
            return
            
        if msg:
            await ms.delete()
            await ctx.send("<:check:819702267476967444> Perfect! The message has been forwarded to the bot support.")
            await channel.send(f"<:info:819702267480899634> **Yo! Someone asked for support, see info next**\n<:message:819702268269297665> The message is : {msg.content}\n<:author:819702267698610176> The author is : {ctx.author.name}#{ctx.author.discriminator}\n<a:dogekek:819739315125878822> Report sended at : {datetime.datetime.utcnow()}")
    
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
                try:
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
                except Exception:
                    return await ctx.send("Couldn't process the image, sorry. If it's actually an image, probably the link/the image isn't supported yet or the link doesn't redirect to the image.")
            else:
                return await ctx.send(":x: Image not found / unsupported provided image.")



    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        self.bot.command_counter += 1
        self.bot.commandsusages[ctx.command.qualified_name] += 1

    @commands.command(help="See the commands usage")
    @commands.is_owner()
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

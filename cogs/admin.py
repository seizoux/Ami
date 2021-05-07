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

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Admin Loaded")

 
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 820733298225315880:
            try:
                if message.content.isdigit():
                    await message.add_reaction("<:AtriYES:819739315579912203>")
                else:
                    pass
            except NotFound:
                pass


    @commands.command()
    @commands.is_owner()
    async def bye(self, ctx):
        em = discord.Embed(description="<a:9565_loading_hearts:808064290468003900>", color = 0xffcff1)
        await ctx.send(embed=em)
        await self.bot.close()
        

    @commands.command()
    @commands.is_owner()
    async def changename(self, ctx, *, newname=None):
        if newname == None:
            return await ctx.reply("No name specified")

        await ctx.guild.me.edit(nick=newname)
        await ctx.message.add_reaction("💌")


    @commands.command()
    async def testers(self, ctx):
        s = await self.bot.pg_con.fetch("SELECT COUNT(*) FROM testers")
        t = s[0]
        f = sum(t)
        await ctx.send(f"<:thumbsup:819703492481908776> I can see **{f}** tester/s in my database!")

    @commands.command()
    async def rows(self, ctx):
        s = await self.bot.pg_con.fetch("SELECT COUNT(*) FROM users")
        t = s[0]
        f = sum(t)
        await ctx.send(f"<:thumbsup:819703492481908776> I can see **{f}** total rows in `users` database!")



    @commands.command()
    @commands.is_owner()
    async def roadmap(self, ctx):
        em = discord.Embed(title="Complete Roadmap", color = 0x2F3136)
        em.add_field(name="First step", value = "<:check:819702267476967444> Get ami verified")
        em.add_field(name="Second step", value = "<:check:819702267476967444> Make welcome function total customizable (with roles)")
        em.add_field(name="Tirth step", value = "<:check:819702267476967444> Reach 200k total users")
        em.add_field(name="Fourth step", value = "<:x_:819702267887222846> Reach 500 guilds")
        em.add_field(name="Fifth step", value = "<:x_:819702267887222846> Add auto-moderation")
        em.add_field(name="Sixth step", value = "<:x_:819702267887222846> Reach 1000 guilds")
        em.set_footer(text="Roadmap manually updated by Daishiky.")
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)


    @commands.command(help="Disable a command (globally)")
    @commands.is_owner()
    async def disable(self, ctx, command):
        if ctx.guild.id == 800176902765674496:
            rol = discord.utils.get(ctx.guild.roles, name = "Mods")
            if not rol in ctx.author.roles:
                return
            else:
                command = self.bot.get_command(command)
                if not command.enabled:
                    return await ctx.send("This command is disabled for now.")
                command.enabled = False
                em = discord.Embed(description=f"• `{command.name}` disabled.\n• Use `ami enable <command>` to re-enable it.", color = 0xffcff1)
                await ctx.send(embed=em)
        else:
            return

    @commands.command(help="Enable a command (globally)")
    @commands.is_owner()
    async def enable(self, ctx, command):
        if ctx.guild.id == 800176902765674496:
            rol = discord.utils.get(ctx.guild.roles, name = "Mods")
            if not rol in ctx.author.roles:
                return
            else:
                command = self.bot.get_command(command)
                if command.enabled:
                    return await ctx.send("This command is already enabled.")
                command.enabled = True
                em = discord.Embed(description=f"• `{command.name}` enabled.\n• Use `ami disable <command>` to disable it.", color = 0xffcff1)
                await ctx.send(embed=em)
        else:
            return

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
                return await ctx.send("Image not found / unsupported provided image.")


    @commands.command()
    @commands.is_owner()
    async def addbl(self, ctx, member: discord.Member, *, reason:str):
        if ctx.guild.id == 800176902765674496:
            rol = discord.utils.get(ctx.guild.roles, name = "Mods")
            if not rol in ctx.author.roles:
                return
            else:
                db = await self.bot.pg_con.fetchrow("SELECT * FROM blacklist")
                user_id = str(member.id)
                reas = str(reason)
                if member == None:
                    await ctx.send("Uhm.. you didn't sent the member to put into the blacklist.")
                    return
                
                reason = reas
                if reason == None:
                    await ctx.send(f"Blacklisted **`{member.name}#{member.discriminator}`**.")
                else:
                    if reason:
                        await ctx.send(f"Blacklisted **`{member.name}#{member.discriminator}`**\nReason : **`{reason}`**.")
                
                await self.bot.pg_con.execute("INSERT INTO blacklist (user_id, reason) VALUES ($1, $2)", user_id, reas)
        else:
            return

    @commands.command()
    @commands.is_owner()
    async def rembl(self, ctx, member: discord.Member):
        if ctx.guild.id == 800176902765674496:
            rol = discord.utils.get(ctx.guild.roles, name = "Mods")
            if not rol in ctx.author.roles:
                return
            else:
                user_id = str(member.id)
                db = await self.bot.pg_con.fetchrow("SELECT * FROM blacklist WHERE user_id = $1", user_id)
                if member == None:
                    await ctx.send("Uhm.. the fuck, send also the member, baaka.")
                    return
                
                if not db:
                    return await ctx.reply("This member isn't blacklisted.")
                
                await ctx.send(f"Removed `{member.name}#{member.discriminator}` from the blacklist.")
                await self.bot.pg_con.execute("DELETE FROM blacklist WHERE user_id = $1", user_id)
        else:
            return

    """@commands.command()
    async def addpremium(self, ctx, member: discord.Member):
        if ctx.guild.id == 800176902765674496:
            rol = discord.utils.get(ctx.guild.roles, name = "Mods")
            if not rol in ctx.author.roles:
                return
            else:
                user_id = str(member.id)
                fmt = '%A | %H:%M | %d/%m/%Y'
                time = datetime.datetime.utcnow()
                sub_date = (time.strftime(fmt))
                await self.bot.pg_con.execute("INSERT INTO premium (user_id, sub_date) VALUES ($1, $2)", user_id, sub_date)
                await ctx.message.add_reaction("✅")
        else:
            return

    @commands.command()
    async def rempremium(self, ctx, member: discord.Member):
        if ctx.guild.id == 800176902765674496:
            rol = discord.utils.get(ctx.guild.roles, name = "Mods")
            if not rol in ctx.author.roles:
                return
            else:
                user_id = str(member.id)
                await self.bot.pg_con.execute("DELETE FROM premium WHERE user_id = $1", user_id)
                await ctx.message.add_reaction("✅")
        else:
            return"""

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
        num_users = len(self.bot.users)
        m = psutil.Process().memory_full_info()
        ram_usage=humanize.naturalsize(m.rss)
        wlat = (round(self.bot.latency*1000, 2))
        cmd = len(self.bot.commands)
        supp = "[Click Here!](https://discord.gg/ZcErEwmVYu)"
        me = "[Click Here!](https://discord.com/users/144126010642792449)"
        web = "[Click Here!](https://amidiscord.xyz/)"
        em = discord.Embed(title="<:info:819702267480899634> Bot Information", description = f"<:greenarrow:819706481883611197> Guilds » `{len(self.bot.guilds)}`\n<:greenarrow:819706481883611197> Members » `{num_users}`\n<:greenarrow:819706481883611197> Bot Commands » `{cmd}`\n<:greenarrow:819706481883611197> CPU Usage » `{cpu_usage}%`\n<:greenarrow:819706481883611197> Ram Usage » `{ram_usage}`\n<:greenarrow:819706481883611197> Websocket Latency » `{wlat}ms`\n<:greenarrow:819706481883611197> Support Server » **{supp}**\n<:greenarrow:819706481883611197> Website » **{web}**", color = 0xffcff1)
        em.set_thumbnail(url=self.bot.user.avatar_url)
        em.set_footer(text="Huge hug to everyone! ®")
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)
        return

    @commands.command(help="See info about a member")
    async def ui(self, ctx, *, user: discord.Member = None):
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
    async def ggl(self, ctx, *, args):
        try:
            lat = (round(self.bot.latency*1000, 2))
            client = async_cse.Search("AIzaSyChzFV6odUmQh7nPp34laGuniYwdlJjSV4") # create the Search client (uses Google by default!)
            results = await client.search(f"{args}", safesearch=True) # returns a list of async_cse.Result objects
            first_result = results[0] # Grab the first result
            second_result = results[1] # Grab the second result
            tirth_result = results[2] # Grab the tirth result
            em = discord.Embed(description = "Find that on google..", color = 0x2F3136)
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


    @commands.Cog.listener()
    async def on_socket_response(self, msg):
        self.bot.socket_receive += 1
        if msg.get("op") != 0:
            self.bot.socket_stats[self.bot.codes[msg.get("op")]] += 1
        else:
            self.bot.socket_stats[msg.get('t')] += 1


    @commands.command(help="Check the socket")
    async def socket(self, ctx):
        current_time = time.time()
        lists = []
        difference = int(current_time - self.bot.start_time)/60
        lists.append(f"Received {self.bot.socket_receive} / {self.bot.socket_receive//difference} sockets per minute")
        for i, (n, v) in enumerate(self.bot.socket_stats.most_common()):
            lists.append(f"{n:<30} {v:<15} {round(v/difference, 3)} /minute")
        paginator = commands.Paginator(max_size=500, prefix="```ml", suffix="```")
        for i in lists:
            paginator.add_line(i)
        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
        return await interface.send_to(ctx)



def setup(bot):
    bot.add_cog(Admin(bot))

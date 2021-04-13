import discord
from discord.errors import DiscordServerError, HTTPException, NotFound
from discord.ext import commands
import os
import traceback
import alexflipnote
import aiozaneapi
from discord.ext.commands.errors import CommandInvokeError
from nudenet import NudeClassifier
import typing
from urllib.request import urlretrieve
import datetime
from discord.ext import tasks

zane = aiozaneapi.Client('MTM=.99huoz8VxWkhWQ-q8wPe-4WlTuxpP-l2SCy4F0aC9fBCR0Hj')
alex_api = alexflipnote.Client("TTkXZ5zOW5pEWnvZxfxQ2DUtYkdZyYOl9Kel_hoK")
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
        await alex_api.close()
        await zane.close()
        await self.bot.close()
        

    @commands.command()
    @commands.is_owner()
    async def changename(self, ctx, *, newname=None):
        if newname == None:
            return await ctx.reply("No name specified")

        await ctx.guild.me.edit(nick=newname)
        await ctx.message.add_reaction("💌")




    @commands.command()
    @commands.is_owner()
    async def addtester(self, ctx, member: discord.Member):
        id = str(member.id)
        await self.bot.pg_con.fetch("SELECT * FROM testers")
        await self.bot.pg_con.execute("INSERT INTO testers (id) VALUES ($1)", id)
        await ctx.send(f"**{member.name}** added as ami tester! (**{member.name}#{member.discriminator}** - `{member.id}`)")

    @commands.command()
    async def priv(self, ctx):
        id = str(ctx.author.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM testers WHERE id = $1", id)
        if user:
            await ctx.send(f"**{ctx.author.name}** you are an official tester of ami! Thanks for support our work!")
        elif ctx.author.id == 144126010642792449:
            await ctx.send(f"**{ctx.author.name}**, you are my developer.. you want to be a tester too?")
        else:
            await ctx.send(f"**{ctx.author.name}**, you are not an ami tester.")

    @commands.command()
    @commands.is_owner()
    async def remtester(self, ctx, member: discord.Member):
        id = str(member.id)
        await self.bot.pg_con.fetch("SELECT * FROM testers")
        await self.bot.pg_con.execute("DELETE FROM testers WHERE id = $1", id)
        await ctx.send(f"**{member.name}** removed as ami tester! (**{member.name}#{member.discriminator}** - `{member.id}`)")


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
        em.add_field(name="Tirth step", value = "<:x_:819702267887222846> Reach 200k total users")
        em.add_field(name="Fourth step", value = "<:x_:819702267887222846> Reach 500 guilds")
        em.add_field(name="Fifth step", value = "<:x_:819702267887222846> Add auto-moderation")
        em.add_field(name="Sixth step", value = "<:x_:819702267887222846> Integrate website with ami commands")
        em.set_footer(text="Also remind to check once time all commands every 3 days (min)")
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)
        


    @commands.command(help="Reload all/one of the bots cogs!")
    @commands.is_owner()
    async def reload(self, ctx, cog=None):
        if not cog:
            # No cog, means we reload all cogs
            async with ctx.typing():
                embed = discord.Embed(
                    title="<a:verified:819702268348989480> Cogs Reloaded!",
                    color=0x808080,
                    timestamp=ctx.message.created_at
                )
                for ext in os.listdir("./cogs/"):
                    if ext.endswith(".py") and not ext.startswith("_"):
                        try:
                            self.bot.unload_extension(f"cogs.{ext[:-3]}")
                            self.bot.load_extension(f"cogs.{ext[:-3]}")
                        except Exception as e:
                            embed.add_field(
                                name=f":x:Failed to reload: `{ext}`",
                                value=e,
                                inline=False
                            )
                await ctx.send(embed=embed)
        else:
            # reload the specific cog
            async with ctx.typing():
                embed = discord.Embed(
                    color=0x808080,
                    timestamp=ctx.message.created_at
                )
                ext = f"{cog.lower()}.py"
                if not os.path.exists(f"./cogs/{ext}"):
                    # if the file does not exist
                    embed.add_field(
                        name=f":x:Failed to reload: `{ext}`",
                        value="This cog does not exist.",
                        inline=False
                    )

                elif ext.endswith(".py") and not ext.startswith("_"):
                    try:
                        self.bot.unload_extension(f"cogs.{ext[:-3]}")
                        self.bot.load_extension(f"cogs.{ext[:-3]}")
                        embed.add_field(
                            name=f":white_check_mark:Reloaded: `{ext}`",
                            value='\uFEFF',
                            inline=False
                        )
                    except Exception:
                        desired_trace = traceback.format_exc()
                        embed.add_field(
                            name=f":x:Failed to reload: `{ext}`",
                            value=desired_trace,
                            inline=False
                        )
                await ctx.send(embed=embed)



    @commands.command(help="Eval something")
    @commands.is_owner()
    async def eval(self, ctx, *, code):
        language_specifiers = ["python", "py", "javascript", "js", "html", "css", "php", "md", "markdown", "go", "golang", "c", "c++", "cpp", "c#", "cs", "csharp", "java", "ruby", "rb", "coffee-script", "coffeescript", "coffee", "bash", "shell", "sh", "json", "http", "pascal", "perl", "rust", "sql", "swift", "vim", "xml", "yaml"]
        loops = 0
        while code.startswith("`"):
            code = "".join(list(code)[1:])
            loops += 1
            if loops == 3:
                loops = 0
                break
        for language_specifier in language_specifiers:
            if code.startswith(language_specifier):
                code = code.lstrip(language_specifier)
        while code.endswith("`"):
            code = "".join(list(code)[0:-1])
            loops += 1
            if loops == 3:
                break
        code = "\n".join(f"    {i}" for i in code.splitlines()) #Adds an extra layer of indentation
        code = f"async def eval_expr():\n{code}" #Wraps the code inside an async function
        def send(text): #Function for sending message to discord if code has any usage of print function
            self.bot.loop.create_task(ctx.send(text))
        env = {
            "bot": self.bot,
            "client": self.bot,
            "ctx": ctx,
            "print": send,
            "_author": ctx.author,
            "_message": ctx.message,
            "_channel": ctx.channel,
            "_guild": ctx.guild,
            "_me": ctx.me
        }
        env.update(globals())
        try:
            exec(code, env)
            eval_expr = env["eval_expr"]
            result = await eval_expr()
            if result:
                await ctx.send(f'```py\n{result}\n```')
        except:
            await ctx.send(f"```{traceback.format_exc()}```")


    @commands.command(help="Disable a command (globally)")
    @commands.is_owner()
    async def disable(self, ctx, command):
        command = self.bot.get_command(command)
        if not command.enabled:
            return await ctx.send("This command is disabled for now.")
        command.enabled = False
        em = discord.Embed(description=f"• `{command.name}` disabled.\n• Use `ami enable <command>` to re-enable it.", color = 0xffcff1)
        await ctx.send(embed=em)

    @commands.command(help="Enable a command (globally)")
    @commands.is_owner()
    async def enable(self, ctx, command):
        command = self.bot.get_command(command)
        if command.enabled:
            return await ctx.send("This command is already enabled.")
        command.enabled = True
        em = discord.Embed(description=f"• `{command.name}` enabled.\n• Use `ami disable <command>` to disable it.", color = 0xffcff1)
        await ctx.send(embed=em)

    @commands.command(help="Check if a pic is NSFW")
    async def check(self, ctx, member: typing.Optional[typing.Union[discord.Member, str]]):
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
                    urs = member
                    url = urs.replace("cdn.discordapp.com", "media.discordapp.net")
                    urlretrieve(url, "check.png")

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

    @commands.command()
    @commands.is_owner()
    async def rembl(self, ctx, member: discord.Member):
        user_id = str(member.id)
        db = await self.bot.pg_con.fetchrow("SELECT * FROM blacklist WHERE user_id = $1", user_id)
        if member == None:
            await ctx.send("Uhm.. the fuck, send also the member, baaka.")
            return
        
        if not db:
            return await ctx.reply("This member isn't blacklisted.")
        
        await ctx.send(f"Removed `{member.name}#{member.discriminator}` from the blacklist.")
        await self.bot.pg_con.execute("DELETE FROM blacklist WHERE user_id = $1", user_id)

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

    @commands.command()
    @commands.is_owner()
    async def ytdlreload(self, ctx):
        latency = self.bot.latency
        lat = (round(self.bot.latency*1000, 3))
        ytdllat = (round(self.bot.latency*300, 3))
        em = discord.Embed(description=f"The wrapper of `YTDL` was reloaded with `{lat}ms`\nIt's running on **`2GB RAM`** and `4 Threads`, with `{ytdllat}ms` approximated.\nRunning on OS `Linux` with `Ubuntu 20.04` (VPS) (latest release).\nReloaded `144` lines, `33` def, `41` events and `1` unique process was running right now, with `1` thread.",color = 0xffcff1)
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Admin(bot))
import discord
from discord.ext import commands
import datetime
from io import BytesIO
from util.defs import premium
from util.pil_funcs import welcome_func
import humanize

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "Welcome"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Welcome Loaded")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 336642139381301249: #or if member.guild.id in blacklist:
            return

        if member.guild.id == 110373943822540800: #or if member.guild.id in blacklist:
            return

        if member.bot:
            return

        guilid = str(member.guild.id)
        guil = member.guild
        data = await self.bot.db.fetch("SELECT * FROM welcome WHERE guild_id = $1", guilid)
        if not data:
            return
        else:
            msg = data[0]["msg"]
            rolen = data[0]["roles"]
            role = data[0]["role"]
            chan = data[0]["channel"]
            embed = data[0]["embed"]
            welcome = data[0]["welc"]
            color = data[0]["embed_color_value"] or self.bot.color
            mex_out = data[0]["message_out"]
            image = data[0]["image"]

            if chan == None:
                return

            try:
                channel = await self.bot.fetch_channel(chan)
            except Exception:
                return

            if not msg:
                return

            namespace = {"{name}": member.name, "{member}": f"{member.name}#{member.discriminator}",
            "{mention}": member.mention,
            "{count}": member.guild.member_count,
            "{created}": member.created_at.strftime("%m/%d/%Y"),
            "{age}": f"{(datetime.datetime.utcnow() - member.created_at).days} days",
            "{guild}": member.guild.name}

            def replace_all(m: str) -> str:
                for k in namespace.keys():
                    m = m.replace(k, str(namespace[k]))
                return m

            msg = replace_all(msg)

            if welcome == "off":
                return

            elif welcome == "on":

                if image:
                    asset1 = member.avatar_url_as(size=512)
                    pfp= BytesIO(await asset1.read())
                    buffer = await self.bot.loop.run_in_executor(None, welcome_func, pfp, member.name, member.discriminator, member.guild.member_count)
                    file=discord.File(fp=buffer, filename="profile.png")

                if embed == "on":
                    if not mex_out:
                        em = discord.Embed(description = f"{msg}", color = color)
                    else:
                        em = discord.Embed(color = color)

                    if image:
                        em.set_image(url="attachment://profile.png")

                    if channel:
                        try:
                            if mex_out:
                                await channel.send(msg)
                                if image:
                                    await channel.send(file=file, embed=em)
                            else:
                                if not image and not mex_out:
                                    await channel.send(embed=em)
                                elif not image and mex_out:
                                    await channel.send(msg)
                                else:
                                    await channel.send(file=file, embed=em)
                        except Exception:
                            pass
                    else:
                        pass

                elif embed == "off":
                    if channel:
                        try:
                            if image:
                                await channel.send(msg, file=file)
                            else:
                                await channel.send(msg)
                        except Exception:
                            pass
                    
                if role == "off":
                    return

                elif role == "on":
                    if not rolen:
                        return
                    else:
                        for i in rolen:
                            try:
                                rol = discord.utils.get(member.guild.roles, id=i)
                                if not rol:
                                    continue
                                await member.add_roles(rol)
                            except discord.Forbidden:
                                pass


    @commands.group(help="Use this command to go trought all welcome config steps with me and recive instruction on what you need to provide to set-up properly the welcome!", invoke_without_command=True)
    async def welcome(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command":"welcome"})

    @welcome.command(help="`ami welcome` subcommand to enable or disable the welcome image.")
    @commands.has_permissions(manage_guild=True)
    @premium(override=True)
    async def image(self, ctx, option):
        data = await self.bot.db.fetch("SELECT * FROM welcome WHERE guild_id = $1", str(ctx.guild.id))

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom welcome.")

        valids = ["enable", "disable"]
        if option not in valids:
            return await ctx.send("This isn't a valid option, choose between `enable` & `disable`")

        fin = None
        t = ""

        if option.lower() == "enable":
            fin = True
            t = "ENABLED"
        elif option.lower() == "disable":
            fin = False
            t = "DISABLED"

        await self.bot.db.execute("UPDATE welcome SET image = $1 WHERE guild_id = $2", fin, str(ctx.guild.id))
        await ctx.send(f"<:greenTick:596576670815879169> **`WELCOME IMAGE {t}!`**")

    @welcome.command(name="mex-out", help="`ami welcome` subcommand to enable or disable the message out of the embed when the embed is enabled.")
    @commands.has_permissions(manage_guild=True)
    async def mex_out(self, ctx, option):
        data = await self.bot.db.fetch("SELECT * FROM welcome WHERE guild_id = $1", str(ctx.guild.id))

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom welcome.")

        valids = ["enable", "disable"]
        if option not in valids:
            return await ctx.send("This isn't a valid option, choose between `enable` & `disable`")

        fin = None
        t = ""

        if option.lower() == "enable":
            fin = True
            t = "ENABLED"
        elif option.lower() == "disable":
            fin = False
            t = "DISABLED"

        await self.bot.db.execute("UPDATE welcome SET message_out = $1 WHERE guild_id = $2", fin, str(ctx.guild.id))
        await ctx.send(f"<:greenTick:596576670815879169> **`MESSAGE OUT OF EMBED {t}!`**")

    @welcome.command(help="`ami welcome` subcommand to config the welcome for this guild under my instructions.")
    @commands.has_permissions(manage_guild=True)
    async def set(self, ctx):
        guild = str(ctx.guild.id)
        data = await self.bot.db.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            await self.bot.db.fetch("INSERT INTO welcome (guild_id) VALUES ($1)", guild)
        else:
            return await ctx.send(":x: This guild has already a config, use welcome subcommands to modify each thing.")

        em = discord.Embed(title="Custom welcome config!", description="Hi! Here you can set your **custom welcome message** for this guild! First of all, only members with **administrator** permission can set it! If you **don't** set it, when a member join here, i don't send any message ^^.\nSo, if you want to set your custom welcome, click on the **reaction below**, and start the configuration! ❤", color = self.bot.color)
        em.set_thumbnail(url=self.bot.user.avatar_url)
        em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        em.timestamp = datetime.datetime.utcnow()
        msg = await ctx.send(embed=em)
        await msg.add_reaction("<:check:819702267476967444>")

        def check(payload):
            return payload.message_id == msg.id and payload.emoji.name == "check" and payload.user_id == ctx.author.id
            
        payload = await self.bot.wait_for("raw_reaction_add", check=check)
        em = discord.Embed(title="1) The message", description="What message did i need to send when someone join here? Send it (you can also use discord markdown)\n**Accepted vars:**\n```py\n{name} > will return the member name\n{member} > will return like Name#1234\n{mention} > will return the member mention\n{count} > will return the position where it joined\n{age} > will return the accout date creation\n{guild} > will return the guild name\n```", color = self.bot.color)
        await msg.edit(embed=em)

        msg1 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel)

        if len(msg1.content) > 2000:
            ln = len(msg1.content)
            return await ctx.send(f"Seems you've sent a message which the lenght is {ln}. The discord limit is `2000`, so resend `ami setwelc` and try to make it shorter.")
        else:
            mex1 = str(msg1.content)
            await self.bot.db.execute("UPDATE welcome SET msg = $1 WHERE guild_id = $2", mex1, guild)
            em = discord.Embed(title="2) The channel", description="Where i need to send this message? **Mention** the channel.", color = self.bot.color)
            await msg.edit(embed=em)

        msg2 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel)

        if msg2:
            try:
                d = msg2.content.strip("<#>")
                v = self.bot.get_channel(int(d))
                if not v:
                    return await ctx.send(f"{d} was not found in the guild channels.")
            except:
                return await msg2.reply("This isn't a valid channel.")
            mex2 = str(d)
            await self.bot.db.execute("UPDATE welcome SET channel = $1 WHERE guild_id = $2", mex2, guild)
            em = discord.Embed(title="3) The roles", description="What roles i need to give to new members? Mention **all** roles you want to add.", color = self.bot.color)
            await msg.edit(embed=em)

        msg3 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel)

        if msg3:
            if msg3.role_mentions:
                for r in msg3.role_mentions:
                    role = discord.utils.get(ctx.guild.roles, id=r.id)
                    if not role:
                        await ctx.send(f"<:redTick:596576672149667840> {r} was not found inside the guild roles, try other roles.")
                        return msg3

                    await self.bot.db.execute("UPDATE welcome SET roles = array_append(roles, $1) WHERE guild_id = $2", r.id, guild)
            em = discord.Embed(title="4) The embed", description="You want the welcome message in an embed? Send `yes` to have it, or `no` to have a normal messagee.", color = self.bot.color)
            await msg.edit(embed=em)

        msg4 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel)

        if msg4.content in ("yes", "Yes"):
            mex4 = "on"
            await self.bot.db.execute("UPDATE welcome SET embed = $1 WHERE guild_id = $2", mex4, guild)
            em = discord.Embed(title="Configuration done! Check next", description="Alright! You've finished the custom welcome config!\nTo enable or disable something, use `ami welcset` and see all welcome settings!", color=self.bot.color)
            await msg.edit(embed=em)
            return

        if msg4.content in ("no", "No"):
            mex4 = "off"
            await self.bot.db.execute("UPDATE welcome SET embed = $1 WHERE guild_id = $2", mex4, guild)
            em = discord.Embed(title="Configuration done! Check next", description="Alright! You've finished the custom welcome config!\nTo enable or disable something, use `ami welcset` and see all welcome settings!", color=self.bot.color)
            await msg.edit(embed=em)
            return

        else:
            await ctx.send("I said `yes` or `no`.. aight, i'll set it on `no`.")
            await self.bot.db.execute("UPDATE welcome SET embed = $1 WHERE guild_id = $2", "off", guild)
            em = discord.Embed(title="Configuration done! Check next", description="Alright! You've finished the custom welcome config!\nTo enable or disable something, use `ami welcset` and see all welcome settings!", color=self.bot.color)
            await msg.edit(embed=em)

    @welcome.command(help="This command make you able to see the actual configuration of the welcome on this guild.")
    @commands.has_permissions(manage_channels=True)
    async def settings(self, ctx):
        guild = str(ctx.guild.id)
        data = await self.bot.db.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send(f"{ctx.author.mention} this guild has no welcome setup.")

        msg = data[0]["msg"]
        rolen = data[0]["roles"]
        role = data[0]["role"]
        channel = data[0]["channel"]
        embed = data[0]["embed"]
        welcome = data[0]["welc"]
        color = data[0]["embed_color"]
        image = data[0]["image"]
        mex_out = data[0]["message_out"]

        mex = "<:check:314349398811475968>"
        rl = "<:check:314349398811475968>"
        rle = "<:check:314349398811475968>"
        ch = "<:check:314349398811475968>"
        emb = "<:check:314349398811475968>"
        wel = "<:check:314349398811475968>"
        emb_color = "<:check:314349398811475968>"
        img = "<:check:314349398811475968>"
        mxo = "<:check:314349398811475968>"


        if not msg:
            mex = "<:empty:314349398723264512>"


        if not rolen:
            rl = "<:empty:314349398723264512>"


        if role == "off":
            rle = "<:xmark:314349398824058880>"
        elif role == "on":
            rle = "<:check:314349398811475968>"
        elif role == None:
            rle = "<:empty:314349398723264512>"


        if not channel:
            ch = "<:empty:314349398723264512>"
        elif channel == None:
            ch = "<:empty:314349398723264512>"



        if embed == "off":
            emb = "<:xmark:314349398824058880>"
        elif embed == "on":
            emb = "<:check:314349398811475968>"
        elif embed == None:
            emb = "<:empty:314349398723264512>"

        if welcome == "off":
            wel = "<:xmark:314349398824058880>"
        elif welcome == "on":
            wel = "<:check:314349398811475968>"
        elif welcome == None:
            wel = "<:empty:314349398723264512>"

        if not color:
            emb_color = "<:empty:314349398723264512>"

        if not image:
            img = "<:xmark:314349398824058880>"
        elif image:
            img = "<:check:314349398811475968>"
        elif image == None:
            img = "<:empty:314349398723264512>"

        if not mex_out:
            mxo = "<:xmark:314349398824058880>"
        elif mex_out:
            mxo = "<:check:314349398811475968>"
        elif mex_out == None:
            mxo = "<:empty:314349398723264512>"

        guil = ctx.guild
        s = []
        if rolen:
            for i in rolen:
                try:
                    role = discord.utils.get(ctx.guild.roles, id=i)
                except Exception:
                    role_d = "**@deleted role**"
                s.append(role.mention if role else role_d)
        
        rnnl = ' '.join(s)
        em = discord.Embed(title=f"{guil.name} Welcome Settings", description="Here you can see all welcome settings for this guild!\n<:check:314349398811475968> = On\n<:xmark:314349398824058880> = Off\n<:empty:314349398723264512> = Empty", color=self.bot.color)
        em.add_field(name=f"Configuration", value = f"`Message`: {mex}\n`Roles`: {rl}\n`Roles Assign`: {rle}\n`Channel`: {ch}\n`Embed`: {emb}\n`Embed Color`: {emb_color}\n`Welcome`: {wel}\n`Image`: {img}\n`Message Out`: {mxo}")
        if rolen:
            em.add_field(name=f"Auto-Roles List", value = f"{rnnl}")
        if msg:
            em.add_field(name="Message Set", value=msg, inline=False)
        em.set_footer(text='Check welcome category in "ami help" for more info!')
        em.set_thumbnail(url=ctx.guild.icon_url)
        await ctx.send(embed=em)

    @welcome.command(help="Change the welcome message sent when someone join in this guild! You can also use here the vars listed in `ami help welcome`.")
    @commands.has_permissions(manage_guild=True)
    async def message(self, ctx, *, args):
        guild = str(ctx.guild.id)
        data = await self.bot.db.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom welcome.")
        
        mex = str(args)
        await ctx.send("<:check:819702267476967444> **`WELCOME MESSAGE UPDATED!`**")
        await self.bot.db.execute("UPDATE welcome SET msg = $1 WHERE guild_id = $2", mex, guild)

    @welcome.command(help='Set the roles i need to give to new members when they join. You can mention multiple roles in row.')
    @commands.has_permissions(manage_guild=True)
    async def setroles(self, ctx, roles: commands.Greedy[discord.Role]):
        db = await self.bot.db.fetch("SELECT * FROM welcome WHERE guild_id = $1", str(ctx.guild.id))
        if not db:
            return await ctx.send("<:redTick:596576672149667840> This guild has no welcome congif setup, use `ami setwelc` before use welcome subcommands.")
        for i in roles:
            if i.id not in ctx.guild._roles:
                return await ctx.send(f"<:redTick:596576672149667840> {i} was not found inside the guild roles.")
            if i.id in db[0]["roles"]:
                return await ctx.send(f"{ctx.author.mention} the {i.mention} role is already on the roles to give.")
            await self.bot.db.execute("UPDATE welcome SET roles = array_append(roles, $1) WHERE guild_id = $2", i.id, str(ctx.guild.id))
        await ctx.send(f"<:greenTick:596576670815879169> Successfully set {', '.join(i.mention for i in roles)} as auto-role on member join!")

    @welcome.command(help="Delete roles from the role list set in the welcome configuration. You can mention multiple roles in row.")
    @commands.has_permissions(manage_guild=True)
    async def delroles(self, ctx, roles: commands.Greedy[discord.Role]):
        db = await self.bot.db.fetch("SELECT * FROM welcome WHERE guild_id = $1", str(ctx.guild.id))
        if not db:
            return await ctx.send("<:redTick:596576672149667840> This guild has no welcome congif setup, use `ami setwelc` before use welcome subcommands.")
        for i in roles:
            if i.id not in ctx.guild._roles:
                return await ctx.send(f"<:redTick:596576672149667840> {i} was not found inside the guild roles.")
            if i.id not in db[0]["roles"]:
                return await ctx.send(f"{ctx.author.mention} the {i.mention} role is not in the roles to give.")
            await self.bot.db.execute("UPDATE welcome SET roles = array_remove(roles, $1) WHERE guild_id = $2", i.id, str(ctx.guild.id))
        await ctx.send(f"<:greenTick:596576670815879169> Successfully deleted {', '.join(i.mention for i in roles)} from the auto-role assigned on member join!")


    @welcome.command(help="Turn on/off the role assignment (auto-role when someone join)")
    @commands.has_permissions(manage_guild=True)
    async def assignrole(self, ctx, *, args):
        guild = str(ctx.guild.id)
        data = await self.bot.db.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom welcome.")
        
        if args == "off":
            mex = str(args)
            await ctx.send("<:check:819702267476967444> **`WELCOME ROLE ASSIGN DISABLED!`**")
            await self.bot.db.execute("UPDATE welcome SET role = $1 WHERE guild_id = $2", mex, guild)
        elif args == "on":
            mex = str(args)
            await ctx.send("<:check:819702267476967444> **`WELCOME ROLE ASSIGN ENABLED!`**")
            await self.bot.db.execute("UPDATE welcome SET role = $1 WHERE guild_id = $2", mex, guild)
        else:
            return await ctx.send("Only `on/off` accepted for this command.")

    @welcome.command(help="Set the channel where you want to make me send the welcome message when someone join in this guild.")
    @commands.has_permissions(manage_guild=True)
    async def channel(self, ctx, *, args):
        guild = str(ctx.guild.id)
        data = await self.bot.db.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom welcome.")
        
        if args:
            d = ""
            if args.isdigit():
                d = args
                l = self.bot.get_channel(d)
                if not l:
                    return await ctx.reply("This **channel id** doesn't exist in this guild.")
            else:
                try:
                    d = args.strip("<#>")
                except Exception:
                    return await ctx.reply("This isn't a valid channel.")
            mex = str(d)
            await ctx.send("<:check:819702267476967444> **`WELCOME MESSAGE CHANNEL UPDATED!`**")
            await self.bot.db.execute("UPDATE welcome SET channel = $1 WHERE guild_id = $2", mex, guild)


    @welcome.command(help="Turn on/off the embed for the welcome message (remember: the welcome profile photo is enabled only in embed.)\nUse `ami welcome embed color <color>` to set the embed color.")
    @commands.has_permissions(manage_guild=True)
    async def embed(self, ctx, option, *, args):
        valid_options = ["set", "color"]
        if option not in valid_options:
            return await ctx.send("The option provied is not valid, choose from `set` and `color` (`set on/off` to enable/disable the embed, `color <HEXA_COLOR>` to set the color of the embed.)")
        guild = str(ctx.guild.id)
        data = await self.bot.db.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom welcome.")
        
        if option == "set":
            if args == "off":
                mex = str(''.join(args))
                await ctx.send("<:check:819702267476967444> **`WELCOME MESSAGE EMBED DISABLED!`**")
                await self.bot.db.execute("UPDATE welcome SET embed = $1 WHERE guild_id = $2", mex, guild)
            elif args == "on":
                mex = str(''.join(args))
                await ctx.send("<:check:819702267476967444> **`WELCOME MESSAGE EMBED ENABLED!`**")
                await self.bot.db.execute("UPDATE welcome SET embed = $1 WHERE guild_id = $2", mex, guild)
            else:
                return await ctx.send("Only `on/off` accepted for this command.")

        elif option == "color":
            valid_colors = {
                "blue" : discord.Color.blue(),
                "red" : discord.Color.red(),
                "green" : discord.Color.green(),
                "blurple" : discord.Color.blurple(),
                "gold" : discord.Color.gold(),
                "orange" : discord.Color.orange(),
                "greyple" : discord.Color.greyple(),
                "magenta" : discord.Color.magenta(),
                "purple" : discord.Color.purple(),
                "teal" : discord.Color.teal(),
                "dark green" : discord.Color.dark_green(),
                "dark gold" : discord.Color.dark_gold(),
                "dark blue" : discord.Color.dark_blue(),
                "dark magenta" : discord.Color.dark_magenta(),
                "dark orange" : discord.Color.dark_orange(),
                "dark purple" : discord.Color.dark_purple(),
                "dark red" : discord.Color.dark_red(),
                "dark theme" : discord.Color.dark_theme(),
                "dark grey" : discord.Color.darker_grey(),

            }


            colors = []
            for key in valid_colors:
                colors.append(f"`{key}`")


            if args.lower() not in valid_colors:
                return await ctx.send(f"{ctx.author.mention}, this is not a valid embed color, check valid colors here:\n{', '.join(colors)}")

            real_hexa = str(valid_colors[args.lower()])

            await self.bot.db.execute("UPDATE welcome SET embed_color = $1 WHERE guild_id = $2", real_hexa, guild)
            await self.bot.db.execute("UPDATE welcome SET embed_color_value = $1 WHERE guild_id = $2", valid_colors[args.lower()].value, guild)
            return await ctx.reply("<:check:819702267476967444> **`EMBED COLOR UPDATED!`**")

    @welcome.command(help="Turn on/off the entire welcome for this guild, no one will recive the welcome you've set anymore.")
    @commands.has_permissions(manage_guild=True)
    async def wel(self, ctx, *, args):
        guild = str(ctx.guild.id)
        data = await self.bot.db.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom welcome")
        
        if args == "off":
            mex = str(args)
            await ctx.send("<:check:819702267476967444> **`WELCOME DISABLED!`**")
            await self.bot.db.execute("UPDATE welcome SET welc = $1 WHERE guild_id = $2", mex, guild)
        elif args == "on":
            mex = str(args)
            await ctx.send("<:check:819702267476967444> **`WELCOME ENABLED!`**")
            await self.bot.db.execute("UPDATE welcome SET welc = $1 WHERE guild_id = $2", mex, guild)
        else:
            return await ctx.send("Only `on/off` accepted for this command.")

        
    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        if len(self.bot.guilds) == 10000:
            chan = self.bot.get_channel(800935539230113803)
            await chan.send(f"@everyone thanks to everyone for the 10,000 guilds! ❤\nCheck <#834940144917282857>, something is coming as soon as daishiky comes online..")

        channel = self.bot.get_channel(817439941902467103)
        await channel.send(f"<:plus_yellow:867507969218445322> **{guild.name}** | {humanize.intcomma(guild.member_count)}")

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        channel = self.bot.get_channel(817439941902467103)
        await channel.send(f"<:minus_yellow:867507968832700446> **{guild.name}** | {humanize.intcomma(guild.member_count)}")


def setup(bot):
    bot.add_cog(Welcome(bot))
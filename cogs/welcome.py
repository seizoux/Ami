import discord
from discord.ext import commands
import datetime
from io import BytesIO
from PIL import Image,ImageDraw, ImageFont
import random
import humanize

def welcome_func(pfp: discord.Member, member_name: str, member_disc: str, member_count: int):
    with Image.open("welcome_bg/welcome_bg.png").convert("RGBA") as wel_bg:

        with Image.open(pfp).convert("RGBA") as pfp_1:
            im = pfp_1.resize((370,370))
            bigsize = (im.size[0] * 3, im.size[1] * 3)
            mask = Image.new('L', bigsize, 0)
            draw = ImageDraw.Draw(mask) 
            draw.ellipse((0, 0) + bigsize, fill=255)
            mask = mask.resize(im.size, Image.ANTIALIAS)
            im.putalpha(mask)
            wel_bg.paste(im,(550,50),im)
            im.close()

        with Image.open("assets/circle.png").convert("RGBA") as circle:
            im = circle.resize((407,422))
            wel_bg.paste(im,(532,25), im)
            im.close()

        font = ImageFont.truetype("fonts/antom.ttf", 92)
        font2 = ImageFont.truetype("fonts/antom.ttf", 60)
        draw = ImageDraw.Draw(wel_bg)
        h = "You are our {} member.".format(humanize.ordinal(member_count))
        s = h.upper()
        tex = f"Welcome {member_name}#{member_disc}!"
        text = tex.upper()
        x, y = 722, 560
        x2, y2 = 742, 700
        fillcolor = "white"
        shadowcolor = "black"
        shadowcolor2 = "black"

        # thin border
        draw.text((x-1, y), text, font=font, fill=shadowcolor, anchor="ms")
        draw.text((x+1, y), text, font=font, fill=shadowcolor, anchor="ms")
        draw.text((x, y-1), text, font=font, fill=shadowcolor, anchor="ms")
        draw.text((x, y+1), text, font=font, fill=shadowcolor, anchor="ms")

        # thicker border
        draw.text((x-1, y-1), text, font=font, fill=shadowcolor, anchor="ms")
        draw.text((x+1, y-1), text, font=font, fill=shadowcolor, anchor="ms")
        draw.text((x-1, y+1), text, font=font, fill=shadowcolor, anchor="ms")
        draw.text((x+1, y+1), text, font=font, fill=shadowcolor, anchor="ms")

        draw.text((x, y), text, font=font, fill=fillcolor, anchor="ms")

        # thin border
        draw.text((x2-1, y2), s, font=font2, fill=shadowcolor2, anchor="ms")
        draw.text((x2+1, y2), s, font=font2, fill=shadowcolor2, anchor="ms")
        draw.text((x2, y2-1), s, font=font2, fill=shadowcolor2, anchor="ms")
        draw.text((x2, y2+1), s, font=font2, fill=shadowcolor2, anchor="ms")

        # thicker border
        draw.text((x2-1, y2-1), s, font=font2, fill=shadowcolor2, anchor="ms")
        draw.text((x2+1, y2-1), s, font=font2, fill=shadowcolor2, anchor="ms")
        draw.text((x2-1, y2+1), s, font=font2, fill=shadowcolor2, anchor="ms")
        draw.text((x2+1, y2+1), s, font=font2, fill=shadowcolor2, anchor="ms")

        draw.text((x2, y2), s, font=font2, fill=fillcolor, anchor="ms")

        buffer = BytesIO()
        wel_bg.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer


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

        if member.guild.id == 800176902765674496: 
            guild = member.guild
            channel = self.bot.get_channel(800188815528558623)
            role = discord.utils.get(member.guild.roles, name = "Members")
            await member.add_roles(role)
            await channel.send(f'**Welcome {member.mention}! You are our `{guild.member_count}th` member! Say "hi" in** <#800935539230113803> **!** <a:blackribbon:819739315004637194> ')
            return

        guilid = str(member.guild.id)
        guil = member.guild
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guilid)
        if not data:
            try:
                return
            except Exception:
                pass
        else:
            msg = data[0]["msg"]
            rolen = data[0]["roles"]
            role = data[0]["role"]
            chan = data[0]["channel"]
            embed = data[0]["embed"]
            welcome = data[0]["welc"]

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
                if embed == "on":
                    asset1 = member.avatar_url_as(size=512)
                    pfp= BytesIO(await asset1.read())
                    buffer = await self.bot.loop.run_in_executor(None, welcome_func, pfp, member.name, member.discriminator, member.guild.member_count)
                    file=discord.File(fp=buffer, filename="profile.png")
                    em = discord.Embed(description = f"{msg}", color = 0xffcff1)
                    em.set_image(url="attachment://profile.png")
                else:
                    pass
                if not channel:
                    try:
                        await guil.system_channel.send(file=file, embed=em)
                        if member.guild.system_channel == None:
                            return
                    except Exception:
                        pass
                elif channel:
                    await channel.send(file=file, embed=em)
            elif embed == "off":
                if not channel:
                    await guil.system_channel.send(msg)
                    if member.guild.system_channel == None:
                        return
                elif channel:
                    await channel.send(msg)
                
            if role == "off":
                    return
            if role == "on":
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


    @commands.command(help="Use this command to go trought all welcome config steps with me and recive instruction on what you need to provide to set-up properly the welcome!")
    @commands.has_permissions(manage_guild=True)
    async def setwelc(self, ctx):
        guild = str(ctx.guild.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            await self.bot.pg_con.fetch("INSERT INTO welcome (guild_id) VALUES ($1)", guild)
        else:
            return await ctx.send(":x: This guild has already a config, use welcome subcommands to modify each thing.")

        em = discord.Embed(title="Custom welcome config!", description="Hi! Here you can set your **custom welcome message** for this guild! First of all, only members with **administrator** permission can set it! If you **don't** set it, when a member join here, i don't send any message ^^.\nSo, if you want to set your custom welcome, click on the **reaction below**, and start the configuration! ❤", color = 0xffcff1)
        em.set_thumbnail(url=self.bot.user.avatar_url)
        em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        em.timestamp = datetime.datetime.utcnow()
        msg = await ctx.send(embed=em)
        await msg.add_reaction("<:check:819702267476967444>")

        def check(payload):
            return payload.message_id == msg.id and payload.emoji.name == "check" and payload.user_id == ctx.author.id
            
        payload = await self.bot.wait_for("raw_reaction_add", check=check)
        em = discord.Embed(title="1) The message", description="What message did i need to send when someone join here? Send it (you can also use discord markdown)\n**Accepted vars:**\n```py\n{name} > will return the member name\n{member} > will return like Name#1234\n{mention} > will return the member mention\n{count} > will return the position where it joined\n{age} > will return the accout date creation\n{guild} > will return the guild name\n```", color = 0xffcff1)
        await msg.edit(embed=em)

        msg1 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel)

        if len(msg1.content) > 2000:
            ln = len(msg1.content)
            return await ctx.send(f"Seems you've sent a message which the lenght is {ln}. The discord limit is `2000`, so resend `ami setwelc` and try to make it shorter.")
        else:
            mex1 = str(msg1.content)
            await self.bot.pg_con.execute("UPDATE welcome SET msg = $1 WHERE guild_id = $2", mex1, guild)
            em = discord.Embed(title="2) The channel", description="Where i need to send this message? **Mention** the channel.", color = 0xffcff1)
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
            await self.bot.pg_con.execute("UPDATE welcome SET channel = $1 WHERE guild_id = $2", mex2, guild)
            em = discord.Embed(title="3) The roles", description="What roles i need to give to new members? Mention **all** roles you want to add.", color = 0xffcff1)
            await msg.edit(embed=em)

        msg3 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel)

        if msg3:
            if msg3.role_mentions:
                for r in msg3.role_mentions:
                    role = discord.utils.get(ctx.guild.roles, id=r.id)
                    if not role:
                        await ctx.send(f"<:redTick:596576672149667840> {r} was not found inside the guild roles, try other roles.")
                        return msg3

                    await self.bot.pg_con.execute("UPDATE welcome SET roles = array_append(roles, $1) WHERE guild_id = $2", r.id, guild)
            em = discord.Embed(title="4) The embed", description="You want the welcome message in an embed? Send `yes` to have it, or `no` to have a normal messagee.", color = 0xffcff1)
            await msg.edit(embed=em)

        msg4 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel)

        if msg4.content in ("yes", "Yes"):
            mex4 = "on"
            await self.bot.pg_con.execute("UPDATE welcome SET embed = $1 WHERE guild_id = $2", mex4, guild)
            em = discord.Embed(title="Configuration done! Check next", description="Alright! You've finished the custom welcome config!\nTo enable or disable something, use `ami welcset` and see all welcome settings!", color=0xffcff1)
            await msg.edit(embed=em)
            return

        if msg4.content in ("no", "No"):
            mex4 = "off"
            await self.bot.pg_con.execute("UPDATE welcome SET embed = $1 WHERE guild_id = $2", mex4, guild)
            em = discord.Embed(title="Configuration done! Check next", description="Alright! You've finished the custom welcome config!\nTo enable or disable something, use `ami welcset` and see all welcome settings!", color=0xffcff1)
            await msg.edit(embed=em)
            return

        else:
            await ctx.send("I said `yes` or `no`.. aight, i'll set it on `no`.")
            await self.bot.pg_con.execute("UPDATE welcome SET embed = $1 WHERE guild_id = $2", "off", guild)
            em = discord.Embed(title="Configuration done! Check next", description="Alright! You've finished the custom welcome config!\nTo enable or disable something, use `ami welcset` and see all welcome settings!", color=0xffcff1)
            await msg.edit(embed=em)

    @commands.command(help="This command make you able to see the actual configuration of the welcome on this guild.")
    @commands.has_permissions(manage_channels=True)
    async def welcset(self, ctx):
        guild = str(ctx.guild.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            await self.bot.pg_con.fetch("INSERT INTO welcome (guild_id) VALUES ($1)", guild)

        msg = data[0]["msg"]
        rolen = data[0]["roles"]
        role = data[0]["role"]
        channel = data[0]["channel"]
        embed = data[0]["embed"]
        welcome = data[0]["welc"]

        mex = "<:check:314349398811475968>"
        rl = "<:check:314349398811475968>"
        rle = "<:check:314349398811475968>"
        ch = "<:check:314349398811475968>"
        emb = "<:check:314349398811475968>"
        wel = "<:check:314349398811475968>"


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

        guil = ctx.guild
        s = []
        if rolen:
            for i in rolen:
                try:
                    role = discord.utils.get(ctx.guild.roles, id=i)
                except Exception:
                    role.replace(i, "**@deleted role**")
                s.append(role.mention)
        
        rnnl = ' '.join(s)
        em = discord.Embed(title=f"{guil.name} Welcome Settings", description="Here you can see all welcome settings for this guild!\n<:check:314349398811475968> = On\n<:xmark:314349398824058880> = Off\n<:empty:314349398723264512> = Empty", color=0xffcff1)
        em.add_field(name=f"Configuration", value = f"`Message` = {mex}\n`Roles` = {rl}\n`Roles Assign` = {rle}\n`Channel` = {ch}\n`Embed` = {emb}\n`Welcome` = {wel}")
        if rolen:
            em.add_field(name=f"Auto-Roles List", value = f"{rnnl}")
        if msg:
            em.add_field(name="Message Set", value=msg, inline=False)
        em.set_footer(text='Check welcome category in "ami help" for more info!')
        await ctx.send(embed=em)

    @commands.command(help="Change the welcome message sent when someone join in this guild! You can also use here the vars listed in `ami help welcome`.")
    @commands.has_permissions(manage_guild=True)
    async def setmex(self, ctx, *, args):
        guild = str(ctx.guild.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom help")
        
        mex = str(args)
        await ctx.send("<:check:819702267476967444> **`WELCOME MESSAGE UPDATED!`**")
        await self.bot.pg_con.execute("UPDATE welcome SET msg = $1 WHERE guild_id = $2", mex, guild)

    @commands.command(help='Set the roles i need to give to new members when they join. You can mention multiple roles in row.')
    async def setroles(self, ctx, roles: commands.Greedy[discord.Role]):
        db = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", str(ctx.guild.id))
        if not db:
            return await ctx.send("<:redTick:596576672149667840> This guild has no welcome congif setup, use `ami setwelc` before use welcome subcommands.")
        for i in roles:
            if i.id not in ctx.guild._roles:
                return await ctx.send(f"<:redTick:596576672149667840> {i} was not found inside the guild roles.")
            await self.bot.pg_con.execute("UPDATE welcome SET roles = array_append(roles, $1) WHERE guild_id = $2", i.id, str(ctx.guild.id))
        await ctx.send(f"<:greenTick:596576670815879169> Successfully set {', '.join(i.mention for i in roles)} as auto-role on member join!")

    @commands.command(help="Delete roles from the role list set in the welcome configuration. You can mention multiple roles in row.")
    async def delroles(self, ctx, roles: commands.Greedy[discord.Role]):
        db = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", str(ctx.guild.id))
        if not db:
            return await ctx.send("<:redTick:596576672149667840> This guild has no welcome congif setup, use `ami setwelc` before use welcome subcommands.")
        for i in roles:
            if i.id not in ctx.guild._roles:
                return await ctx.send(f"<:redTick:596576672149667840> {i} was not found inside the guild roles.")
            await self.bot.pg_con.execute("UPDATE welcome SET roles = array_remove(roles, $1) WHERE guild_id = $2", i.id, str(ctx.guild.id))
        await ctx.send(f"<:greenTick:596576670815879169> Successfully deleted {', '.join(i.mention for i in roles)} from the auto-role assigned on member join!")


    @commands.command(help="Turn on/off the role assignment (auto-role when someone join)")
    @commands.has_permissions(manage_guild=True)
    async def setassign(self, ctx, *, args):
        guild = str(ctx.guild.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom help")
        
        if args == "off":
            mex = str(args)
            await ctx.send("<:check:819702267476967444> **`WELCOME ROLE ASSIGN DISABLED!`**")
            await self.bot.pg_con.execute("UPDATE welcome SET role = $1 WHERE guild_id = $2", mex, guild)
        elif args == "on":
            mex = str(args)
            await ctx.send("<:check:819702267476967444> **`WELCOME ROLE ASSIGN ENABLED!`**")
            await self.bot.pg_con.execute("UPDATE welcome SET role = $1 WHERE guild_id = $2", mex, guild)
        else:
            return await ctx.send("Only `on/off` accepted for this command.")

    @commands.command(help="Set the channel where you want to make me send the welcome message when someone join in this guild.")
    @commands.has_permissions(manage_guild=True)
    async def setchannel(self, ctx, *, args):
        guild = str(ctx.guild.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom help")
        
        if args:
            d = ""
            if args.isdigit():
                d = args
                l = await self.bot.get_channel(d)
                if not l:
                    return await ctx.reply("This **channel id** doesn't exist in this guild.")
            else:
                try:
                    d = args.strip("<#>")
                except Exception:
                    return await ctx.reply("This isn't a valid channel.")
            mex = str(d)
            await ctx.send("<:check:819702267476967444> **`WELCOME MESSAGE CHANNEL UPDATED!`**")
            await self.bot.pg_con.execute("UPDATE welcome SET channel = $1 WHERE guild_id = $2", mex, guild)


    @commands.command(help="Turn on/off the embed for the welcome message (remember: the welcome profile photo is enabled only in embed.)")
    @commands.has_permissions(manage_guild=True)
    async def emb(self, ctx, *, args):
        guild = str(ctx.guild.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom help")
        
        if args == "off":
            mex = str(args)
            await ctx.send("<:check:819702267476967444> **`WELCOME MESSAGE EMBED DISABLED!`**")
            await self.bot.pg_con.execute("UPDATE welcome SET embed = $1 WHERE guild_id = $2", mex, guild)
        elif args == "on":
            mex = str(args)
            await ctx.send("<:check:819702267476967444> **`WELCOME MESSAGE EMBED ENABLED!`**")
            await self.bot.pg_con.execute("UPDATE welcome SET embed = $1 WHERE guild_id = $2", mex, guild)
        else:
            return await ctx.send("Only `on/off` accepted for this command.")


    @commands.command(help="Turn on/off the entire welcome for this guild, no one will recive the welcome you've set anymore.")
    @commands.has_permissions(manage_guild=True)
    async def wel(self, ctx, *, args):
        guild = str(ctx.guild.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM welcome WHERE guild_id = $1", guild)

        if not data:
            return await ctx.send("This guild isn't in the database. Send `ami setwelc` to config the custom welcome")
        
        if args == "off":
            mex = str(args)
            await ctx.send("<:check:819702267476967444> **`WELCOME DISABLED!`**")
            await self.bot.pg_con.execute("UPDATE welcome SET welc = $1 WHERE guild_id = $2", mex, guild)
        elif args == "on":
            mex = str(args)
            await ctx.send("<:check:819702267476967444> **`WELCOME ENABLED!`**")
            await self.bot.pg_con.execute("UPDATE welcome SET welc = $1 WHERE guild_id = $2", mex, guild)
        else:
            return await ctx.send("Only `on/off` accepted for this command.")

        

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        try:
            here1 = "[here](https://top.gg/bot/801742991185936384/vote)"
            here2 = "[here](https://discordbotlist.com/bots/ami/upvote)"
            em = discord.Embed(title=guild.name, description = f"Hi cuties, thanks to have added me here! I'm ami, a multi-purpose discord bot, and i come with over 160 commands, included an entire economy system, a live music playing, and ton of other stuff!\n\nI was deployed and published on 21/01/2021, and i was online for 99.95% of the time, without issues not announced. I don't have a dashboard, i am totally discord-side, with commands to manage all my settings.\n\nI'm able to make the experience in this discord server more enjoyable, here it is some tips to do to make me work at my best:\n\n1) Use `ami setwelc` to set a custom welcome message when someone joins here! (Tip: After that, you can use `ami wel off` to disable the welcome)\n2) Give me the `Embed Links` permission, most of my commands works only if i have this permission.\n\nI hope you enjoy this experience, and i appreciate if you vote me {here1} and {here2}!", color = 0xffcff1)
            if guild.icon_url:
                em.set_thumbnail(url=guild.icon_url)
            else:
                pass
            if guild.banner_url:
                em.set_image(url=guild.banner_url)
            else:
                pass
            await guild.system_channel.send(embed=em)
        except Exception:
            pass

        channel = self.bot.get_channel(817439941902467103)
        em = discord.Embed(title="Added in a new guild!", description = f"**Guild name** : `{guild.name}`\n\n**Guild members** : `{guild.member_count}`\n\n**Owner** : `{guild.owner}` - (`{guild.owner_id}`)\n\n**Guild region** : `{guild.region}`\n\n**Guild created at** : `{guild.created_at}`", color = 0xffcff1)
        if guild.icon_url:
            em.set_thumbnail(url=guild.icon_url)
        else:
            pass
        if guild.banner_url:
            em.set_image(url=guild.banner_url)
        else:
            pass
        await channel.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        try:
            await self.bot.pg_con.execute("DELETE * FROM welcome WHERE guild_id = $1", str(guild.id))
        except Exception:
            pass
        channel = self.bot.get_channel(817439941902467103)
        em = discord.Embed(title=f"Got removed from `{guild.name}`..", description=f"Lost `{guild.member_count}` members.\n\nOwner : `{guild.owner} - ({guild.owner_id})`", color = 0xffcff1)
        if guild.icon_url:
            em.set_thumbnail(url=guild.icon_url)
        else:
            pass
        if guild.banner_url:
            em.set_image(url=guild.banner_url)
        else:
            pass
        await channel.send(embed=em)


def setup(bot):
    bot.add_cog(Welcome(bot))

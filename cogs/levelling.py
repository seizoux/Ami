import discord
from discord.ext import commands, tasks
import json
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random

def levelup_func(avatar: discord.Member):
    with Image.open("assets/levelup.png").convert("RGBA") as bg:

        with Image.open(avatar).convert("RGBA") as pfp_1:
            im = pfp_1.resize((223, 223))
            bigsize = (im.size[0] * 3, im.size[1] * 3)
            mask = Image.new('L', bigsize, 0)
            draw = ImageDraw.Draw(mask) 
            draw.ellipse((0, 0) + bigsize, fill=255)
            mask = mask.resize(im.size, Image.ANTIALIAS)
            im.putalpha(mask)
            bg.paste(im,(9, 49),im)
            im.close()

        font = ImageFont.truetype("fonts/antom.ttf", 48)
        draw = ImageDraw.Draw(bg)
        text = "L E V E L  U P!"
        color = "white"
        shadow = "black"

        x, y = 285, 120

        draw.text((x-1, y), text, font=font, fill=shadow)
        draw.text((x+1, y), text, font=font, fill=shadow)
        draw.text((x, y-1), text, font=font, fill=shadow)
        draw.text((x, y+1), text, font=font, fill=shadow)

        # thicker border
        draw.text((x-1, y-1), text, font=font, fill=shadow)
        draw.text((x+1, y-1), text, font=font, fill=shadow)
        draw.text((x-1, y+1), text, font=font, fill=shadow)
        draw.text((x+1, y+1), text, font=font, fill=shadow)

        draw.text((x, y), text, font=font, fill=color)

        buffer = BytesIO()
        bg.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

def level_func(avatar: discord.Member, name:str, level:str, xp:str, needed:str):
    with Image.open("assets/level_banner.png").convert("RGBA") as bg:

        with Image.open("assets/level_circle.png").convert("RGBA") as circle:
            im = circle.resize((180,190))
            bg.paste(im,(50,20), im)
            im.close()

        with Image.open(avatar).convert("RGBA") as pfp_1:
            im = pfp_1.resize((110, 103))
            bigsize = (im.size[0] * 3, im.size[1] * 3)
            mask = Image.new('L', bigsize, 0)
            draw = ImageDraw.Draw(mask) 
            draw.ellipse((0, 0) + bigsize, fill=255)
            mask = mask.resize(im.size, Image.ANTIALIAS)
            im.putalpha(mask)
            bg.paste(im,(85,54),im)
            im.close()
      
        exp = int(xp)
        need = int(needed)
        spkx, spky = 245, 155

        with Image.open("assets/sparkle_not.png").convert("RGBA") as not_sparkle:
            dfc = not_sparkle.resize((40, 40))
            bg.paste(dfc, (245, 155), dfc)
            n = 0
            d, c = 245, 155
            for i in range(10):
                n += 1
                d += 40
                s = not_sparkle.resize((40, 40))
                bg.paste(s, (d, c), s)
                if n >= 9:
                    break

        with Image.open("assets/sparkle.png").convert("RGBA") as sparkle:
            im = sparkle.resize((40, 40))

            if (exp >= need/10):
                bg.paste(im, (spkx, spky), im)

            if (exp >= need-(need/2)):
                bg.paste(im, (spkx+40, spky), im)

            if (exp >= need-(need/3)):
                bg.paste(im, (spkx+80, spky), im)

            if (exp >= need-(need/4)):
                bg.paste(im, (spkx+120, spky), im)

            if (exp >= need-(need/5)):
                bg.paste(im, (spkx+160, spky), im)

            if (exp >= need-(need/6)):
                bg.paste(im, (spkx+200, spky), im)

            if (exp >= need-(need/7)):
                bg.paste(im, (spkx+240, spky), im)

            if (exp >= need-(need/8)):
                bg.paste(im, (spkx+280, spky), im)

            if (exp >= need-(need/9)):
                bg.paste(im, (spkx+320, spky), im)

            if (exp >= need-(need/10)):
                bg.paste(im, (spkx+360, spky), im)
            
            if (exp >= need):
                bg.paste(s, (spkx+40, spky), s)


        font = ImageFont.truetype("fonts/ArialUnicodeMS.ttf", 38)
        font2 = ImageFont.truetype("fonts/louis.ttf", 18)
        draw = ImageDraw.Draw(bg)

        # colors
        color = "#F8F8FF"
        color2 = "black"

        #TEXTS
        member_name = name
        level_text = f"Level : {level}"
        xp_text = f"Exp : {xp} / {need}"

        #coords
        x, y = 250, 70
        x2, y2 = 250, 90

        # drawing member name
        draw.text((x+1, y-1), member_name, font=font, fill="black")
        draw.text((x+2, y-2), member_name, font=font, fill="black")
        draw.text((x, y), member_name, font=font, fill=color)

        # drawing member level
        draw.text((x2+300, y2+40), level_text, font=font2, fill=color2)

        # drawing member xp
        draw.text((x2, y2+40), xp_text, font=font2, fill=color2)

        buffer = BytesIO()
        bg.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

class Levelling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "Levelling"
        self._cd = commands.CooldownMapping.from_cooldown(1, 5.0, commands.BucketType.user)
        self.modality = {}
        self.xp_users = {}
        self.levels_users = {}
        self.bot.loop.create_task(self.cache_levels())
        self.save_level.start()

    def ratelimit_xp(self, message):
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()
    
    @tasks.loop(minutes=30)
    async def save_level(self):
        await self.bot.wait_until_ready()
        for i, v in self.xp_users.items():
            await self.bot.pg_con.execute("INSERT INTO levelling (guild_id, xp) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET xp = $2", i, json.dumps(v))
        
        for i, v in self.levels_users.items():
            await self.bot.pg_con.execute("INSERT INTO levelling (guild_id, levels) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET levels = $2", i, json.dumps(v))

    async def cache_levels(self):
        db = await self.bot.pg_con.fetch("SELECT * FROM levelling")
        db2 = await self.bot.pg_con.fetch("SELECT * FROM levelling_settings")
        for s in db2:
            if s["toggle"] == "enable":
                self.modality[int(s["guild_id"])] = True

        for i in db:
            if i["xp"]:
                self.xp_users[i["guild_id"]] = json.loads(i["xp"])

            if i["levels"]:
                self.levels_users[i["guild_id"]] = json.loads(i["levels"])



    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Levelling Loaded")

    @commands.command(help="See your rank card according to the guild where you execute this command.\nThis will return `0`, `0` if not **xp** / **level**", aliases=["rank", "lvl"])
    async def level(self, ctx, member: discord.Member = None):
        """ Command to see your level / the level of a member"""
        if member is None:
            member = ctx.author

        if ctx.guild.id not in self.modality:
            return await ctx.send("<:4318crossmark:848857812565229601> Levelling is disabled in this guild.")

        if ctx.guild.id in self.xp_users:
            if str(ctx.author.id) not in self.xp_users[ctx.guild.id]:
                return await ctx.send("<:4318crossmark:848857812565229601> This member has **0**xp and it's **Lvl. 0**.")
        
        name = f"{member.name}#{member.discriminator}"
        level = 0
        if str(member.id) in self.levels_users[ctx.guild.id]:
            level = self.levels_users[ctx.guild.id][str(member.id)]["level"]
        xp = self.xp_users[ctx.guild.id][str(member.id)]["xp_earned"]
        needed = self.xp_users[ctx.guild.id][str(member.id)]["next_level"]

        asset1 = member.avatar_url_as(size=128)
        avatar = BytesIO(await asset1.read())

        buffer = await self.bot.loop.run_in_executor(None, level_func, avatar, name, str(level), str(xp), str(needed))
        file=discord.File(fp=buffer, filename="level.png")
        await ctx.send(file=file)


    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.wait_until_ready()

        if message.guild.id not in self.modality:
            return

        if message.guild.id not in self.xp_users:
            self.xp_users[message.guild.id] = {}
            
        if message.guild.id not in self.levels_users:
            self.levels_users[message.guild.id] = {}

        if message.author.bot:
            return

        retry_after = self.ratelimit_xp(message)
        if retry_after:
            return

        if str(message.author.id) not in self.xp_users[message.guild.id]:
            self.xp_users[message.guild.id][str(message.author.id)] = {
                                                'xp_earned': 0,
                                                'xp': 0,
                                                'next_level': 447
                                                }

        d = random.randint(31, 74)
        self.xp_users[message.guild.id][str(message.author.id)]["xp_earned"] = self.xp_users[message.guild.id][str(message.author.id)]["xp"] + d
        self.xp_users[message.guild.id][str(message.author.id)]["xp"] = self.xp_users[message.guild.id][str(message.author.id)]["xp"] + d

        if self.xp_users[message.guild.id][str(message.author.id)]["xp"] >= self.xp_users[message.guild.id][str(message.author.id)]["next_level"]:
            self.xp_users[message.guild.id][str(message.author.id)]["xp"] = 0
            self.xp_users[message.guild.id][str(message.author.id)]["next_level"] = self.xp_users[message.guild.id][str(message.author.id)]["xp_earned"] + 447
            
            if str(message.author.id) not in self.levels_users[message.guild.id]:
                self.levels_users[message.guild.id][str(message.author.id)] = {
                                                    'level': 0
                                                    }

            self.levels_users[message.guild.id][str(message.author.id)]["level"] = self.levels_users[message.guild.id][str(message.author.id)]["level"] + 1

            db = await self.bot.pg_con.fetch("SELECT * FROM levelling_settings WHERE guild_id = $1", str(message.guild.id))
            mex = db[0]["message"]
            channel = db[0]["channel"]
            image = db[0]["levelup_image"]

            if not mex:
                return

            if not channel:
                return

            namespace = {"{name}": message.author.name, 
            "{member}": f"{message.author.name}#{message.author.discriminator}",
            "{mention}": message.author.mention,
            "{level}": self.levels_users[message.guild.id][str(message.author.id)]["level"]}

            def replace_all(m: str) -> str:
                for k in namespace.keys():
                    m = m.replace(k, str(namespace[k]))
                return m

            msg = replace_all(mex)

            ch = self.bot.get_channel(channel)
            if not ch:
                return

            try:
                if image == "enable":
                    asset1 = message.author.avatar_url_as(size=128)
                    avatar = BytesIO(await asset1.read())

                    buffer = await self.bot.loop.run_in_executor(None, levelup_func, avatar)
                    file=discord.File(fp=buffer, filename="levelup.png")
                    await ch.send(msg)
                    await ch.send(file=file)
            except Exception:
                return

    @commands.command()
    async def leveluptest(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
    
        asset1 = ctx.author.avatar_url_as(size=128)
        avatar = BytesIO(await asset1.read())

        buffer = await self.bot.loop.run_in_executor(None, levelup_func, avatar)
        file=discord.File(fp=buffer, filename="levelup.png")
        await ctx.send(file=file)

    @commands.command(help="Manage the levelling feature settings for this guild!\n`ami levelling settings` to check the levelling settings for the guild\n`ami levelling enable` to enable the levelling\n`ami levelling disable` to disable the levelling\n"
                            "`ami levelling message [set]` to set the level-up message\n`ami levelling channel [set]` to set the channel where send level-up messages\n"
                            "`ami levelling levelup-image [set]` to enable / disable the image on levelup messages.\n\n"
                            "**You can also use some variables in the level-up message:**```py\n{name} : will return the member name\n{mention} : will return the member mention\n{member} : will return the complete member name\n{level} : will return the member level\n```")
    @commands.has_permissions(manage_guild=True)
    async def setlevelling(self, ctx, mode, *, set=None):
        if mode.lower() == "settings":
            db = await self.bot.pg_con.fetch("SELECT * FROM levelling_settings WHERE guild_id = $1", str(ctx.guild.id))
            if not db:
                return await ctx.send("<:4318crossmark:848857812565229601> This guild has no levelling settings yet.")

            mexs = db[0]["message"]
            chs = db[0]["channel"]
            tog = db[0]["toggle"]

            gfc = ""

            chd = self.bot.get_channel(chs)
            if not chd:
                gfc = chs
            gfc = chd.mention

            if tog.lower() in ["off", "disable"]:
                tog = "Disabled"

            elif tog.lower() in ["on", "enable"]:
                tog = "Enabled"

            d1 = "Message set? : <:4430checkmark:848857812632076314>"
            d2 = "Channel set? : <:4430checkmark:848857812632076314>"

            if not mexs:
                d1 = "Message set? : <:4318crossmark:848857812565229601>"
                mexs = "No message set."

            if not chs:
                d2 = "Channel set? : <:4318crossmark:848857812565229601>"
                chs = "No channel set."

            if not tog:
                tog = "No modality set"

            em = discord.Embed(title = "Levelling Settings", description = f"The levelling in this guild is **{tog.title()}**", color = 0xffcff1)
            em.add_field(name=f"{ctx.guild.name} options", value = f"{d1}\n{d2}\n\n**Channel** : {gfc}\n**Message** : {mexs}")
            em.set_thumbnail(url=ctx.guild.icon_url)
            em.set_footer(text="Check `ami help setlevelling` for more things.")
            return await ctx.send(embed=em)

        if mode.lower() == "enable":
            db = await self.bot.pg_con.fetch("SELECT * FROM levelling_settings WHERE guild_id = $1", str(ctx.guild.id))
            if not db:
                await self.bot.pg_con.execute("INSERT INTO levelling_settings (guild_id, toggle) VALUES ($1, $2)", str(ctx.guild.id), mode)
                self.modality[ctx.guild.id] = True
                return await ctx.message.add_reaction("<:4430checkmark:848857812632076314>")

            await self.bot.pg_con.execute("UPDATE levelling_settings SET toggle = $1 WHERE guild_id = $2", mode, str(ctx.guild.id))
            self.modality[ctx.guild.id] = True
            return await ctx.message.add_reaction("<:4430checkmark:848857812632076314>")

        elif mode.lower() == "disable":
            db = await self.bot.pg_con.fetch("SELECT * FROM levelling_settings WHERE guild_id = $1", str(ctx.guild.id))
            if not db:
                await self.bot.pg_con.execute("INSERT INTO levelling_settings (guild_id, toggle) VALUES ($1, $2)", str(ctx.guild.id), mode)
                del self.modality[ctx.guild.id]
                return await ctx.message.add_reaction("<:4318crossmark:848857812565229601>")

            await self.bot.pg_con.execute("UPDATE levelling_settings SET toggle = $1 WHERE guild_id = $2", mode, str(ctx.guild.id))
            del self.modality[ctx.guild.id]
            return await ctx.message.add_reaction("<:4318crossmark:848857812565229601>")

        elif mode.lower() == "levelup-image":
            if not set:
                return await ctx.send("<:4318crossmark:848857812565229601> The `[set]` argument is required for this option, example:\n"
                                    "ami setlevelling levelup-message enable / ami setlevelling levelup-message disable")
            
            modescf = ["enable", "disable"]
            if set.lower() not in modescf:
                return await ctx.send("<:4318crossmark:848857812565229601> This isn't a valid option for **levelup-image**. Valids are `enable` & `disable`")

            db = await self.bot.pg_con.fetch("SELECT * FROM levelling_settings WHERE guild_id = $1", str(ctx.guild.id))
            if not db:
                await self.bot.pg_con.execute("INSERT INTO levelling_settings (guild_id, levelup_image) VALUES ($1, $2)", str(ctx.guild.id), set)
        
            await self.bot.pg_con.execute("UPDATE levelling_settings SET levelup_image = $1 WHERE guild_id = $2", set, str(ctx.guild.id))

            if set.lower() == "enable":
                return await ctx.send("<:4430checkmark:848857812632076314> Levelup image succesfully enabled!")
            return await ctx.send("<:4318crossmark:848857812565229601> Levelup image succesfully disabled!")

        elif mode.lower() == "message":
            if not set:
                return await ctx.send("<:4318crossmark:848857812565229601> The `[set]` argument is required for this option, example:\n"
                                    "ami setlevelling message 🎉 {member} is now **Lvl. {level}!**")
            
            db = await self.bot.pg_con.fetch("SELECT * FROM levelling_settings WHERE guild_id = $1", str(ctx.guild.id))
            if not db:
                await self.bot.pg_con.execute("INSERT INTO levelling_settings (guild_id, message) VALUES ($1, $2)", str(ctx.guild.id), set)
                return await ctx.send(f"<:4430checkmark:848857812632076314> Levelup message succesfully set!")
    
            await self.bot.pg_con.execute("UPDATE levelling_settings SET message = $1 WHERE guild_id = $2", set, str(ctx.guild.id))
            return await ctx.send(f"<:4430checkmark:848857812632076314> Levelup message succesfully set!")

        elif mode.lower() == "channel":
            if not set:
                return await ctx.send("<:4318crossmark:848857812565229601> The `[set]` argument is required for this option, example:\n"
                                    "ami setlevelling channel #mention / ami setlevelling channel 87493829249205534")

            d = set.strip("<#>")
            v = self.bot.get_channel(int(d))
            if not v:
                return await ctx.send(f"{set} is not a valid channel.")

            db = await self.bot.pg_con.fetch("SELECT * FROM levelling_settings WHERE guild_id = $1", str(ctx.guild.id))
            if not db:
                await self.bot.pg_con.execute("INSERT INTO levelling_settings (guild_id, channel) VALUES ($1, $2)", str(ctx.guild.id), int(d))
                return await ctx.send("<:4430checkmark:848857812632076314> Levelling channel updated, i'll send every level up message there.")

            await self.bot.pg_con.execute("UPDATE levelling_settings SET channel = $1 WHERE guild_id = $2", int(d), str(ctx.guild.id))
            return await ctx.send("<:4430checkmark:848857812632076314> Levelling channel updated, i'll send every level up message there.")
        else:
            return await ctx.send("<:4318crossmark:848857812565229601> The provided option is invalid, check `ami help levelling` for more info's.")

#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################

    @commands.command()
    @commands.is_owner()
    async def addlevels(self, ctx, amount:int, member: discord.Member = None):
        if member is None:
            member = ctx.author

        #daishiky u change those commands urself i am lazy
        await ctx.send(f"<:4430checkmark:848857812632076314> Added **{amount}** levels to **{member.name}#{member.discriminator}**")

    @commands.command()
    @commands.is_owner()
    async def remlevels(self, ctx, amount:int, member: discord.Member = None):
        if member is None:
            member = ctx.author

        db = await self.bot.pg_con.fetch("SELECT * FROM levelling WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, member.id)
        if not db:
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{member.name}#{member.discriminator}** is not in the database.")

        if amount > db[0]["level"]:
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{member.name}#{member.discriminator}** level is **{db[0]['level']}**, you can't remove **{amount}** levels.")

        await self.bot.pg_con.execute("UPDATE levelling SET level = $1 WHERE guild_id = $2 AND user_id = $3", db[0]["level"] - amount, ctx.guild.id, member.id)
        await ctx.send(f"<:4430checkmark:848857812632076314> Removed **{amount}** levels to **{member.name}#{member.discriminator}**")

    @commands.command()
    @commands.is_owner()
    async def addxp(self, ctx, amount:int, member: discord.Member = None):
        if member is None:
            member = ctx.author

        db = await self.bot.pg_con.fetch("SELECT * FROM levelling WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, member.id)
        if not db:
            await self.bot.pg_con.execute("INSERT INTO levelling (guild_id, user_id, xp) VALUES ($1, $2, $3)", ctx.guild.id, member.id, amount)
            return await ctx.send(f"<:4430checkmark:848857812632076314> Added **{amount}** xp to **{member.name}#{member.discriminator}**")

        await self.bot.pg_con.execute("UPDATE levelling SET xp = $1 WHERE guild_id = $2 AND user_id = $3", db[0]["xp"] + amount, ctx.guild.id, member.id)
        await ctx.send(f"<:4430checkmark:848857812632076314> Added **{amount}** xp to **{member.name}#{member.discriminator}**")

    @commands.command()
    @commands.is_owner()
    async def remxp(self, ctx, amount:int, member: discord.Member = None):
        if member is None:
            member = ctx.author

        db = await self.bot.pg_con.fetch("SELECT * FROM levelling WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, member.id)
        if not db:
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{member.name}#{member.discriminator}** is not in the database.")

        if amount > db[0]["level"]:
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{member.name}#{member.discriminator}** xp is **{db[0]['xp']}**, you can't remove **{amount}** xp.")

        await self.bot.pg_con.execute("UPDATE levelling SET xp = $1 WHERE guild_id = $2 AND user_id = $3", db[0]["xp"] - amount, ctx.guild.id, member.id)
        await ctx.send(f"<:4430checkmark:848857812632076314> Removed **{amount}** xp to **{member.name}#{member.discriminator}**")

def setup(bot):
    bot.add_cog(Levelling(bot))

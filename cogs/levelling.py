import discord
from discord.ext import commands, tasks
import json
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
from numerize import numerize
from cogsf.defs import is_team

class RankCard():
  """
  A class function to draw our rank card
  """

  def drawProgressBar(d, x, y, w, h, progress, fg="#FFB6C1"):

      w *= progress
      d.ellipse((x+w, y, x+h+w, y+h),fill=fg)
      d.ellipse((x, y, x+h, y+h),fill=fg)
      d.rectangle((x+(h/2), y, x+w+(h/2), y+h),fill=fg)

      return d

  def levelup_func(avatar: discord.Member, level:str):
      with Image.open("assets/levelup.png").convert("RGBA") as bg:
          bg = bg.resize((230, 100))

          with Image.open("assets/glass.png").convert("RGBA") as glass:
              im = glass.resize((150, 90))
              bg.paste(im, (70, 5), im)
              im.close()

          with Image.open(avatar).convert("RGBA") as pfp_1:
              im = pfp_1.resize((85, 85))
              bg.paste(im,(9, 8),im)
              im.close()

          font = ImageFont.truetype("fonts/antom.ttf", 28)
          draw = ImageDraw.Draw(bg)
          text = f"{level}"
          text2 = "LEVEL UP!"
          color = "white"
          color2 = "gold"
          shadow = "black"

          x, y = 150, 70
          x2, y2 = 105, 10

          draw.text((x-1, y), text, font=font, fill=shadow, anchor="mm")
          draw.text((x+1, y), text, font=font, fill=shadow, anchor="mm")
          draw.text((x, y-1), text, font=font, fill=shadow, anchor="mm")
          draw.text((x, y+1), text, font=font, fill=shadow, anchor="mm")

          # thicker border
          draw.text((x-1, y-1), text, font=font, fill=shadow, anchor="mm")
          draw.text((x+1, y-1), text, font=font, fill=shadow, anchor="mm")
          draw.text((x-1, y+1), text, font=font, fill=shadow, anchor="mm")
          draw.text((x+1, y+1), text, font=font, fill=shadow, anchor="mm")

          draw.text((x, y), text, font=font, fill=color, anchor="mm")

          draw.text((x2-1, y2), text2, font=font, fill=shadow)
          draw.text((x2+1, y2), text2, font=font, fill=shadow)
          draw.text((x2, y2-1), text2, font=font, fill=shadow)
          draw.text((x2, y2+1), text2, font=font, fill=shadow)

          # thicker border
          draw.text((x2-1, y2-1), text2, font=font, fill=shadow)
          draw.text((x2+1, y2-1), text2, font=font, fill=shadow)
          draw.text((x2-1, y2+1), text2, font=font, fill=shadow)
          draw.text((x2+1, y2+1), text2, font=font, fill=shadow)

          draw.text((x2, y2), text2, font=font, fill=color2)

          buffer = BytesIO()
          bg.save(buffer, format="PNG")
          buffer.seek(0)

          return buffer

  def level_func(avatar: discord.Member, name:str, disc:str, level:int, xp:int, needed:int, rank:str):
      with Image.open("assets/level_card.png").convert("RGBA") as bg:

          with Image.open(avatar).convert("RGBA") as pfp_1:
              im = pfp_1.resize((241, 242))
              bigsize = (im.size[0] * 3, im.size[1] * 3)
              mask = Image.new('L', bigsize, 0)
              draw = ImageDraw.Draw(mask) 
              draw.ellipse((0, 0) + bigsize, fill=255)
              mask = mask.resize(im.size, Image.ANTIALIAS)
              im.putalpha(mask)
              bg.paste(im,(34,19),im)
              im.close()
        
          exp = int(xp)
          need = int(needed)
          spkx, spky = 355, 216

          sparky = 0.00
          x_sparky = int(need/100)
          f = x_sparky
          for i in range(100):
              if exp >= x_sparky:
                  sparky += 0.01
                  x_sparky += f

          d = ImageDraw.Draw(bg)
          d = RankCard.drawProgressBar(d, spkx, spky+10, 815, 30, sparky)

          font = ImageFont.truetype("fonts/ArialUnicodeMS.ttf", 58)
          font_disc = ImageFont.truetype("fonts/ArialUnicodeMS.ttf", 35)
          font2 = ImageFont.truetype("fonts/louis.ttf", 38)
          font3 = ImageFont.truetype("fonts/louis.ttf", 42)
          font4 = ImageFont.truetype("fonts/louis.ttf", 70)
          font5 = ImageFont.truetype("fonts/louis.ttf", 36)
          font6 = ImageFont.truetype("fonts/louis.ttf", 45)
          font7 = ImageFont.truetype("fonts/louis.ttf", 78)
          draw = ImageDraw.Draw(bg)

          # colors
          color = "#F8F8FF"
          color2 = "white"

          #TEXTS
          member_name = name
          member_disc = disc
          level_text = f"LVL."
          level_number_text = f"{level}"
          xp_text = f"{xp:,} XP /"
          needed_xp_text = f"{need:,}"
          rank_text = "RANK"
          rank_number_text = f"#{rank}"

          #coords
          x, y = 355, 28
          x2, y2 = 360, 130
          x3, y3 = 365 + font.getsize(member_name)[0], 53
          x4 = 370 + font3.getsize(xp_text)[0]
          x5 = 1010 + font4.getsize(level_text)[0]
          x6, y6 = 955, 50
          x7 = 965 + font6.getsize(rank_text)[0]

          # drawing member rank text
          draw.text((x6, y6), rank_text, font=font6, fill="white")

          # drawing member rank number
          draw.text((x7, y6-30), rank_number_text, font=font7, fill="#FFB6C1")

          # drawing member name
          if len(member_name) >= 10:
              font = ImageFont.truetype("fonts/ArialUnicodeMS.ttf", 38)
              y += 12
              x3, y3 = 360 + font.getsize(member_name)[0], 42
          draw.text((x-1, y+1), member_name, font=font, fill="black")
          draw.text((x-2, y+2), member_name, font=font, fill="black")
          draw.text((x, y), member_name, font=font, fill=color)

          # drawing member disc
          draw.text((x3, y3), member_disc, font=font_disc, fill="#FFB6C1")

          # drawing member level text
          draw.text((x2+700, y2+40), level_text, font=font2, fill=color2)

          # drawing member level number with border bold black
          draw.text((x5, y2+10), level_number_text, font=font4, fill="#FFB6C1")

          # drawing member xp
          draw.text((x2, y2+40), xp_text, font=font3, fill="#FFB6C1")
          draw.text((x2-1, (y2+40)-1), xp_text, font=font3, fill="#FFB6C1")

          # drawing member needed xp with border bold black
          draw.text((x4, y2+44), needed_xp_text, font=font5, fill="#DCDCDC")

          buffer = BytesIO()
          bg.save(buffer, format="PNG")
          buffer.seek(0)

          return buffer

class Levelling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "Levelling"
        self._cd = commands.CooldownMapping.from_cooldown(1, 7.2, commands.BucketType.user)
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

    @commands.group(help="Manage the leveling feature settings for this guild!\n`ami setleveling settings` to check the leveling settings for the guild\n`ami setleveling set enable` to enable the leveling\n`ami setleveling set disable` to disable the leveling\n"
                            "`ami setleveling message [set]` to set the level-up message\n`ami setleveling channel [set]` to set the channel where send level-up messages\n"
                            "`ami setleveling levelup-image [set]` to enable / disable the image on levelup messages.\n\n"
                            "**You can also use some variables in the level-up message:**```py\n{name} : will return the member name\n{mention} : will return the member mention\n{member} : will return the complete member name\n{level} : will return the member level\n```", invoke_without_command=True)
    async def setleveling(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command":"setleveling"})

    @commands.command(help="See your rank card according to the guild where you execute this command.\nThis will return `0`, `0` if not **xp** / **level**", aliases=["rank", "lvl"])
    async def level(self, ctx, member: discord.Member = None):
        """ Command to see your level / the level of a member"""
        if member is None:
            member = ctx.author

        if ctx.guild.id not in self.modality:
            return await ctx.send("<:4318crossmark:848857812565229601> Leveling is disabled in this guild.")

        if ctx.guild.id not in self.xp_users:
            return

        if ctx.guild.id not in self.levels_users:
            return

        name = f"{member.name}"
        disc = f"#{member.discriminator}"

        level = 0
        if str(member.id) in self.levels_users[ctx.guild.id]:
            level = self.levels_users[ctx.guild.id][str(member.id)]["level"]
        
        xp = 0
        if str(member.id) in self.xp_users[ctx.guild.id]:
            xp = self.xp_users[ctx.guild.id][str(member.id)]["xp"]
        
        needed = 300
        if str(member.id) in self.xp_users[ctx.guild.id]:
            needed = self.xp_users[ctx.guild.id][str(member.id)]["next_level"]

        rank = "N/A"
        if ctx.guild.id in self.xp_users:
            if str(member.id) in self.xp_users[ctx.guild.id]:
                rank =  sorted([x['xp_earned'] for x in self.xp_users[ctx.guild.id].values()], reverse=True).index(self.xp_users[ctx.guild.id][str(member.id)]['xp_earned']) + 1

        asset1 = member.avatar_url_as(size=128)
        avatar = BytesIO(await asset1.read())

        buffer = await self.bot.loop.run_in_executor(None, RankCard.level_func, avatar, name, disc, int(level), int(xp), int(needed), str(rank))
        file=discord.File(fp=buffer, filename="level.png")
        await ctx.send(file=file)


    @commands.Cog.listener()
    async def on_message(self, message):
        """ 
        Our event function to add xp to members on mesage
        This works with a commands.CooldownMapping(1, 7.3) timeout
        When someone is ratelimited, just return without add xp

        If the member xp is > or = to the needed_xp to level-up, this
        reset the member xp to 0, add 1 level if the member is in our
        self.levels_users dict, then if in the guild leveling settings
        the level-up image is enabled, continue sending the level-up
        image in the designed channel.
        """
        await self.bot.wait_until_ready()

        try:
            if message.guild.id not in self.modality:
                return
        except Exception:
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
                                                'next_level': 301
                                                }

        d = random.randint(11, 28)
        self.xp_users[message.guild.id][str(message.author.id)]["xp_earned"] = self.xp_users[message.guild.id][str(message.author.id)]["xp_earned"] + d
        self.xp_users[message.guild.id][str(message.author.id)]["xp"] = self.xp_users[message.guild.id][str(message.author.id)]["xp"] + d

        if self.xp_users[message.guild.id][str(message.author.id)]["xp"] >= self.xp_users[message.guild.id][str(message.author.id)]["next_level"]:
            self.xp_users[message.guild.id][str(message.author.id)]["xp"] = 0
            self.xp_users[message.guild.id][str(message.author.id)]["next_level"] = self.xp_users[message.guild.id][str(message.author.id)]["xp_earned"] + 301
            
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
                    level = self.levels_users[message.guild.id][str(message.author.id)]["level"]
                    asset1 = message.author.avatar_url_as(size=128)
                    avatar = BytesIO(await asset1.read())

                    buffer = await self.bot.loop.run_in_executor(None, RankCard.levelup_func, avatar, level)
                    file=discord.File(fp=buffer, filename="levelup_member.png")
                    await ch.send(msg, file=file)
            except Exception:
                return

    @commands.command()
    async def leveluptest(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author
    
        asset1 = ctx.author.avatar_url_as(size=128)
        avatar = BytesIO(await asset1.read())
        level = self.levels_users[ctx.guild.id][str(ctx.author.id)]["level"]

        buffer = await self.bot.loop.run_in_executor(None, RankCard.levelup_func, avatar, level)
        file=discord.File(fp=buffer, filename="levelup.png")
        await ctx.send(file=file)

    @setleveling.command()
    @commands.has_permissions(manage_guild=True)
    async def settings(self, ctx, mode, *, set=None):
        db = await self.bot.pg_con.fetch("SELECT * FROM levelling_settings WHERE guild_id = $1", str(ctx.guild.id))
        if not db:
            return await ctx.send("<:4318crossmark:848857812565229601> This guild has no leveling settings yet.")

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

        em = discord.Embed(title = "Leveling Settings", description = f"The leveling in this guild is **{tog.title()}**", color = 0xffcff1)
        em.add_field(name=f"{ctx.guild.name} options", value = f"{d1}\n{d2}\n\n**Channel** : {gfc}\n**Message** : {mexs}")
        em.set_thumbnail(url=ctx.guild.icon_url)
        em.set_footer(text="Check `ami help setleveling` for more things.")
        return await ctx.send(embed=em)

    @setleveling.command()
    @commands.has_permissions(manage_guild=True)
    async def set(self, ctx, mode):
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

    @setleveling.command(name="levelup-image")
    @commands.has_permissions(manage_guild=True)
    async def levelup_image(self, ctx, set):
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

    @setleveling.command()
    @commands.has_permissions(manage_guild=True)
    async def message(self, ctx, set):    
        db = await self.bot.pg_con.fetch("SELECT * FROM levelling_settings WHERE guild_id = $1", str(ctx.guild.id))
        if not db:
            await self.bot.pg_con.execute("INSERT INTO levelling_settings (guild_id, message) VALUES ($1, $2)", str(ctx.guild.id), set)
            return await ctx.send(f"<:4430checkmark:848857812632076314> Levelup message succesfully set!")
    
        await self.bot.pg_con.execute("UPDATE levelling_settings SET message = $1 WHERE guild_id = $2", set, str(ctx.guild.id))
        return await ctx.send(f"<:4430checkmark:848857812632076314> Levelup message succesfully set!")

    @setleveling.command()
    @commands.has_permissions(manage_guild=True)
    async def channel(self, ctx, set):
        d = set.strip("<#>")
        v = self.bot.get_channel(int(d))
        if not v:
            return await ctx.send(f"{set} is not a valid channel.")

        db = await self.bot.pg_con.fetch("SELECT * FROM levelling_settings WHERE guild_id = $1", str(ctx.guild.id))
        if not db:
            await self.bot.pg_con.execute("INSERT INTO levelling_settings (guild_id, channel) VALUES ($1, $2)", str(ctx.guild.id), int(d))
            return await ctx.send("<:4430checkmark:848857812632076314> Leveling channel updated, i'll send every level up message there.")

        await self.bot.pg_con.execute("UPDATE levelling_settings SET channel = $1 WHERE guild_id = $2", int(d), str(ctx.guild.id))
        return await ctx.send("<:4430checkmark:848857812632076314> Leveling channel updated, i'll send every level up message there.")

#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################
#########################################################################################################

    @commands.command()
    @is_team()
    async def addlevels(self, ctx, amount:int, member: discord.Member = None):
        if member is None:
            member = ctx.author

        if amount >= 1000:
            return await ctx.send("<:4318crossmark:848857812565229601> Amount can't be over 1000.")

        if ctx.guild.id not in self.modality:
            return await ctx.send("<:4318crossmark:848857812565229601> Leveling in this guild is disabled.")

        if ctx.guild.id not in self.levels_users:
            return await ctx.send("<:4318crossmark:848857812565229601> Guild not found in levels cache.")

        if str(member.id) not in self.levels_users[ctx.guild.id]:
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{member.name}#{member.discriminator}** is not in the database.")
    
        self.levels_users[ctx.guild.id][str(member.id)]["level"] = self.levels_users[ctx.guild.id][str(member.id)]["level"] + amount
        await ctx.send(f"<:4430checkmark:848857812632076314> Added **{amount}** levels to **{member.name}#{member.discriminator}**")

    @commands.command()
    @is_team()
    async def remlevels(self, ctx, amount:int, member: discord.Member = None):
        if member is None:
            member = ctx.author

        if ctx.guild.id not in self.modality:
            return await ctx.send("<:4318crossmark:848857812565229601> Leveling in this guild is disabled.")

        if ctx.guild.id not in self.levels_users:
            return await ctx.send("<:4318crossmark:848857812565229601> Guild not found in levels cache.")

        if str(member.id) not in self.levels_users[ctx.guild.id]:
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{member.name}#{member.discriminator}** is not in the database.")

        if amount > self.levels_users[ctx.guild.id][str(member.id)]["level"]:
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{member.name}#{member.discriminator}** level is **{self.levels_users[ctx.guild.id][str(member.id)]['level']}**, you can't remove **{amount}** levels.")

        self.levels_users[ctx.guild.id][str(member.id)]["level"] = self.levels_users[ctx.guild.id][str(member.id)]["level"] - amount
        await ctx.send(f"<:4430checkmark:848857812632076314> Removed **{amount}** levels to **{member.name}#{member.discriminator}**")

    @commands.command()
    @is_team()
    async def addxp(self, ctx, amount:int, member: discord.Member = None):
        if member is None:
            member = ctx.author

        if amount >= 100000:
            return await ctx.send("<:4318crossmark:848857812565229601> Amount can't be over 100k.")

        if ctx.guild.id not in self.modality:
            return await ctx.send("<:4318crossmark:848857812565229601> Leveling in this guild is disabled.")

        if ctx.guild.id not in self.xp_users:
            return await ctx.send("<:4318crossmark:848857812565229601> Guild not found in levels cache.")

        if str(member.id) not in self.xp_users[ctx.guild.id]:
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{member.name}#{member.discriminator}** is not in the database.")

        self.xp_users[ctx.guild.id][str(member.id)]["xp"] =  self.xp_users[ctx.guild.id][str(member.id)]["xp"] + amount
        self.xp_users[ctx.guild.id][str(member.id)]["xp_earned"] = self.xp_users[ctx.guild.id][str(member.id)]["xp_earned"] + amount
        await ctx.send(f"<:4430checkmark:848857812632076314> Added **{amount}** xp to **{member.name}#{member.discriminator}**")

    @commands.command()
    @is_team()
    async def remxp(self, ctx, amount:int, member: discord.Member = None):
        if member is None:
            member = ctx.author

        if ctx.guild.id not in self.modality:
            return await ctx.send("<:4318crossmark:848857812565229601> Leveling in this guild is disabled.")

        if ctx.guild.id not in self.xp_users:
            return await ctx.send("<:4318crossmark:848857812565229601> Guild not found in levels cache.")

        if str(member.id) not in self.xp_users[ctx.guild.id]:
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{member.name}#{member.discriminator}** is not in the database.")

        if amount > self.xp_users[ctx.guild.id][str(member.id)]["xp"]:
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{member.name}#{member.discriminator}** xp is **{self.xp_users[ctx.guild.id][str(member.id)]['xp']}**, you can't remove **{amount}** xp.")

        self.xp_users[ctx.guild.id][str(member.id)]["xp"] = self.xp_users[ctx.guild.id][str(member.id)]["xp"] - amount
        self.xp_users[ctx.guild.id][str(member.id)]["xp_earned"] = self.xp_users[ctx.guild.id][str(member.id)]["xp_earned"] - amount

        await ctx.send(f"<:4430checkmark:848857812632076314> Removed **{amount}** xp to **{member.name}#{member.discriminator}**")

def setup(bot):
    bot.add_cog(Levelling(bot))

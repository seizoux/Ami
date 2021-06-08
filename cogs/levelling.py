import discord
from discord.ext import commands, tasks
import json
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random

def level_func(avatar: discord.Member, name:str, rank:str, level:str, xp:str):
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

        font = ImageFont.truetype("fonts/louis.ttf", 28)
        font2 = ImageFont.truetype("fonts/louis.ttf", 18)
        draw = ImageDraw.Draw(bg)

        # colors
        color = "purple"
        color2 = "grey"

        #TEXTS
        member_name = name
        level_text = f"Level : {level}"
        xp_text = f"XP : {xp}"
        rank_number = f"#{rank}"
        rank_text = "RANK"

        #coords
        x, y = 250, 90
        x2, y2 = 250, 130

        # drawing member name
        draw.text((x, y), member_name, font=font, fill=color)

        # drawing member level
        draw.text((x2, y2), level_text, font=font2, fill=color2)

        # drawing member xp
        draw.text((x2, y2+30), xp_text, font=font2, fill=color2)

        # drawing member rank text
        draw.text((x, y-40), rank_text, font=font, fill="black")

        # drawing member rank number
        draw.text((x+80, y-40), rank_number, font=font, fill="white")

        buffer = BytesIO()
        bg.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

class Levelling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "Levelling"
        self.save_level.start()
        self.modality = {}
        self.xp_users = {}
        self.levels_users = {}
        self.bot.loop.create_task(self.cache_levels())
    
    @tasks.loop(minutes=1)
    async def save_level(self):
        await self.bot.wait_until_ready()
        for i, v in self.xp_users.items():
            await self.bot.pg_con.execute("INSERT INTO levelling (guild_id, xp) VALUES ($1, $2) WHERE guild_id = $1 ON CONFLICT (guild_id) DO UPDATE SET xp = $2", i, json.dumps(v))
        
        for i, v in self.levels_users.items():
            await self.bot.pg_con.execute("INSERT INTO levelling (guild_id, levels) VALUES ($1, $2) WHERE guild_id = $1 ON CONFLICT (guild_id) DO UPDATE SET levels = $2", i, json.dumps(v))
        
            
      

    async def cache_levels(self):
        db = await self.bot.pg_con.fetch("SELECT * FROM levelling")
        db2 = await self.bot.pg_con.fetch("SELECT * FROM levelling_settings")
        for s in db2:
            if s["toggle"] == "on":
                self.modality[int(s["guild_id"])] = True

        for i in db:
            if i["xp"]:
                self.xp_users[i["guild_id"]] = json.loads(i["xp"])

            if i["levels"]:
                self.levels_users[i["guild_id"]] = json.loads(i["levels"])



    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Levelling Loaded")

    @commands.command()
    @commands.is_owner()
    async def levelling_cache(self, ctx):
        return await ctx.send(f"**self.modality**\n{self.modality}\n\n**self.xp_users**\n{self.xp_users}\n\n**self.levels_users**\n{self.levels_users}")

    @commands.command(help="See your rank card according to the guild where you execute this command.\nThis will return `0`, `0` if not **xp** / **level**")
    async def level(self, ctx, member: discord.Member = None):
        """ Command to see your level / the level of a member"""
        if member is None:
            member = ctx.author

        if ctx.guild.id not in self.modality:
            return await ctx.send("<:4318crossmark:848857812565229601> Levelling is disabled in this guild.")

        if ctx.guild.id in self.xp_users:
            if ctx.author.id not in self.xp_users[ctx.guild.id]:
                return await ctx.send("<:4318crossmark:848857812565229601> This member has **0**xp and it's **Lvl. 0**.")
        
        name = f"{member.name}#{member.discriminator}"
        rank = await self.bot.pg_con.fetchval("SELECT count(*)+1 FROM levelling WHERE guild_id = $1 AND xp > (SELECT xp FROM levelling WHERE guild_id = $1 AND user_id = $2)", ctx.guild.id, member.id)
        level = self.levels_users[ctx.guild.id][ctx.author.id]["level"]
        xp = self.xp_users[ctx.guild.id][ctx.author.id]["xp_earned"]

        asset1 = member.avatar_url_as(size=128)
        avatar = BytesIO(await asset1.read())

        buffer = await self.bot.loop.run_in_executor(None, level_func, avatar, name, str(rank), str(level), str(xp))
        file=discord.File(fp=buffer, filename="level.png")
        await ctx.send(file=file)


    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.wait_until_ready()
        if message.guild.id not in self.modality:
            return

        if message.guild.id not in self.xp_users:
            self.xp_users[message.guild.id] = {}

        if message.author.bot:
            return

        if message.author.id not in self.xp_users:
            f = random.randint(320, 798)
            self.xp_users[message.guild.id][message.author.id] = {
                                                'xp_earned': 0,
                                                'xp': 0,
                                                'next_level': f
                                                }

        d = random.randint(1, 50)
        self.xp_users[message.guild.id][message.author.id]["xp_earned"] = self.xp_users[message.guild.id][message.author.id]["xp"] + d
        self.xp_users[message.guild.id][message.author.id]["xp"] = self.xp_users[message.guild.id][message.author.id]["xp"] + d

        if self.xp_users[message.guild.id][message.author.id]["xp"] >= self.xp_users[message.guild.id][message.author.id]["next_level"]:
            self.xp_users[message.guild.id][message.author.id]["xp"] = 0
            self.levels_users[message.guild.id][message.author.id]["level"] = self.levels_users[message.guild.id][message.author.id]["level"] + 1
            await message.channel.send(f"<:4430checkmark:848857812632076314> {message.author.mention} has leveled up to **Lvl. {self.levels_users[message.guild.id][message.author.id]['level']}**!")

    @commands.command(help="Enable or disable the levelling in the guild\n`ami setlevelling on` to enable the levelling\n`ami setlevelling off` to disable the levelling")
    @commands.is_owner()
    async def setlevelling(self, ctx, mode):
        modes = ["on", "off"]

        if mode.lower() not in modes:
            return

        if mode.lower() == "on":
            db = await self.bot.pg_con.fetch("SELECT * FROM levelling_settings WHERE guild_id = $1", str(ctx.guild.id))
            if not db:
                await self.bot.pg_con.execute("INSERT INTO levelling_settings (guild_id, toggle) VALUES ($1, $2)", str(ctx.guild.id), mode)
                self.modality[ctx.guild.id] = True
                return await ctx.message.add_reaction("<:4430checkmark:848857812632076314>")

            await self.bot.pg_con.execute("UPDATE levelling_settings SET toggle = $1 WHERE guild_id = $2", mode, str(ctx.guild.id))
            self.modality[ctx.guild.id] = True
            return await ctx.message.add_reaction("<:4430checkmark:848857812632076314>")

        elif mode.lower() == "off":
            db = await self.bot.pg_con.fetch("SELECT * FROM levelling_settings WHERE guild_id = $1", str(ctx.guild.id))
            if not db:
                await self.bot.pg_con.execute("INSERT INTO levelling_settings (guild_id, toggle) VALUES ($1, $2)", str(ctx.guild.id), mode)
                del self.modality[ctx.guild.id]
                return await ctx.message.add_reaction("<:4318crossmark:848857812565229601>")

            await self.bot.pg_con.execute("UPDATE levelling_settings SET toggle = $1 WHERE guild_id = $2", mode, str(ctx.guild.id))
            del self.modality[ctx.guild.id]
            return await ctx.message.add_reaction("<:4318crossmark:848857812565229601>")


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

import discord
from discord.ext import commands
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random

# just skip this part, is pil image yes yes
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
        self.modality = {}
        self.xp_users = {}
        self.levels_users = {}
        self.bot.loop.create_task(self.cache_levels())
    
    # on cog load, insert into our dicts respective values from db, separated for each guild_id.
    async def cache_levels(self):
        await self.bot.wait_until_ready()
        db = await self.bot.pg_con.fetch("SELECT * FROM levelling")
        db2 = await self.bot.pg_con.fetch("SELECT * FROM levelling_settings")
        for s in db2:
            if s["toggle"] == "on":
                self.modality[int(s["guild_id"])] = True #insert it into self.modality as True, to enable levelling in that guild

        for i in db:
            if i["xp"]:
                """ here we're put into `self.xp_users` dict every member in the db with at least 1 xp and level 1, separated for each guild_id 
                    example:
                    self.xp_users= {guild_id_here: {
                                                        user_id_here: {
                                                        "xp": user_xp_here, 
                                                        "xp_needed_levelup": xp + 1732},
                                                        }, 
                                                        {
                                                        user2_id_here: {
                                                        "xp": user2_xp_here, 
                                                        "xp_needed_levelup": xp + 1732
                                                        },
                                                   },
                                              }
                                    
                """
                self.xp_users[int(i["guild_id"])] = {
                                                            int(i["user_id"]): {
                                                            'xp': i["xp"],
                                                            'next_level': i["xp"] + random.randint(320, 798)
                                                        ,},}


            if i["level"]:
                """ same thing here as xp, but with levels """
                self.levels_users[int(i["guild_id"])] = {
                                                            int(i["user_id"]): {
                                                            'level': i["level"]
                                                        ,},}


    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Levelling Loaded")

    @commands.command()
    @commands.is_owner()
    async def levelling_cache(self, ctx):
        return await ctx.send(self.xp_users)

    
    # ignore this one, this works well cuz it use directly the db #
    
    @commands.command(help="See your rank card according to the guild where you execute this command.\nThis will return `0`, `0` if not **xp** / **level**")
    async def level(self, ctx, member: discord.Member = None):
        """ Command to see your level / the level of a member"""
        if member is None:
            member = ctx.author

        db = await self.bot.pg_con.fetch("SELECT * FROM levelling WHERE guild_id = $1 AND user_id = $2", str(ctx.guild.id), str(member.id))
        if not db:
            if member:
                return await ctx.send("<:4318crossmark:848857812565229601> This member has **0**xp and it's **Lvl. 0**.")
        
        name = f"{member.name}#{member.discriminator}"
        rank = await self.bot.pg_con.fetchval("SELECT count(*)+1 FROM levelling WHERE guild_id = $1 AND xp > (SELECT xp FROM levelling WHERE guild_id = $1 AND user_id = $2)", str(ctx.guild.id), str(member.id))
        level = db[0]["level"]
        xp = db[0]["xp"]

        asset1 = member.avatar_url_as(size=128)
        avatar = BytesIO(await asset1.read())

        buffer = await self.bot.loop.run_in_executor(None, level_func, avatar, name, str(rank), str(level), str(xp))
        file=discord.File(fp=buffer, filename="level.png")
        await ctx.send(file=file)


    @commands.Cog.listener()
    async def on_message(self, message):
        #if the guild has levelling disabled, return
        if message.guild.id not in self.modality:
            return

        #if the guild is not in our `self.xp_users`, insert it into that
        if not message.guild.id in self.xp_users:
            self.xp_users.append(message.guild.id)

        #if the message author is not in our self.xp_users dict
        if message.author.id not in self.xp_users[message.guild.id]:
            db = await self.bot.pg_con.fetch("SELECT * FROM levelling WHERE guild_id = $1 AND user_id = $2", str(message.guild.id), str(message.author.id))
            if not db: #if the user is not in db, insert it and add it into our `self.xp_users` cache.
                await self.bot.pg_con.execute("INSERT INTO levelling (guild_id, user_id, level, xp) VALUES ($1, $2, $3, $4)", str(message.guild.id), str(message.author.id), 0, 0)
            
                self.xp_users[int(db[0]["guild_id"])] = {
                                                            int(db[0]["user_id"]): {
                                                            'xp': db[0]["xp"],
                                                            'next_level': db[0]["xp"] + random.randint(320, 798)
                                                        },}

        #now let's add the xp on each message, first gets it from db
        db = await self.bot.pg_con.fetch("SELECT * FROM levelling WHERE guild_id = $1 AND user_id = $2", str(message.guild.id), str(message.author.id))

        #add a random xp amount to that users in our dict `self.xp_users` from 1 to 50
        self.xp_users[message.guild.id][int(db[0]["user_id"])]["xp"] = self.xp_users[message.guild.id][int(db[0]["user_id"])]["xp"] + random.randint(1, 50)
        
        #check if xp is > or = to xp needed to level up
        if self.xp_users[message.guild.id][int(db[0]["user_id"])]["xp"] >= self.xp_users[message.guild.id][int(db[0]["user_id"])]["next_level"]:
            
            #if xp is > or = to xp needed to level up, reset xp in cache to 0
            self.xp_users[message.guild.id][int(db[0]["user_id"])]["xp"] = 0
            
            # then add +1 to the level of the user in our `self.levels_users` cache
            self.levels_users[message.guild.id][int(db[0]["user_id"])]["level"] = self.levels_users[message.guild.id][int(db[0]["user_id"])]["level"] + 1

            
    # this works fine, skip.
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
            return await ctx.message.add_reaction("<:4430checkmark:848857812632076314>")

        elif mode.lower() == "off":
            db = await self.bot.pg_con.fetch("SELECT * FROM levelling_settings WHERE guild_id = $1", str(ctx.guild.id))
            if not db:
                await self.bot.pg_con.execute("INSERT INTO levelling_settings (guild_id, toggle) VALUES ($1, $2)", str(ctx.guild.id), mode)
                self.modality[ctx.guild.id] = True
                return await ctx.message.add_reaction("<:4318crossmark:848857812565229601>")

            await self.bot.pg_con.execute("UPDATE levelling_settings SET toggle = $1 WHERE guild_id = $2", mode, str(ctx.guild.id))
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

        db = await self.bot.pg_con.fetch("SELECT * FROM levelling WHERE guild_id = $1 AND user_id = $2", str(ctx.guild.id), str(member.id))
        if not db:
            await self.bot.pg_con.execute("INSERT INTO levelling (guild_id, user_id, level) VALUES ($1, $2, $3)", str(ctx.guild.id), str(member.id), amount)
            return await ctx.send(f"<:4430checkmark:848857812632076314> Added **{amount}** levels to **{member.name}#{member.discriminator}**")

        await self.bot.pg_con.execute("UPDATE levelling SET level = $1 WHERE guild_id = $2 AND user_id = $3", db[0]["level"] + amount, str(ctx.guild.id), str(member.id))
        await ctx.send(f"<:4430checkmark:848857812632076314> Added **{amount}** levels to **{member.name}#{member.discriminator}**")

    @commands.command()
    @commands.is_owner()
    async def remlevels(self, ctx, amount:int, member: discord.Member = None):
        if member is None:
            member = ctx.author

        db = await self.bot.pg_con.fetch("SELECT * FROM levelling WHERE guild_id = $1 AND user_id = $2", str(ctx.guild.id), str(member.id))
        if not db:
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{member.name}#{member.discriminator}** is not in the database.")

        if amount > db[0]["level"]:
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{member.name}#{member.discriminator}** level is **{db[0]['level']}**, you can't remove **{amount}** levels.")

        await self.bot.pg_con.execute("UPDATE levelling SET level = $1 WHERE guild_id = $2 AND user_id = $3", db[0]["level"] - amount, str(ctx.guild.id), str(member.id))
        await ctx.send(f"<:4430checkmark:848857812632076314> Removed **{amount}** levels to **{member.name}#{member.discriminator}**")

    @commands.command()
    @commands.is_owner()
    async def addxp(self, ctx, amount:int, member: discord.Member = None):
        if member is None:
            member = ctx.author

        db = await self.bot.pg_con.fetch("SELECT * FROM levelling WHERE guild_id = $1 AND user_id = $2", str(ctx.guild.id), str(member.id))
        if not db:
            await self.bot.pg_con.execute("INSERT INTO levelling (guild_id, user_id, xp) VALUES ($1, $2, $3)", str(ctx.guild.id), str(member.id), amount)
            return await ctx.send(f"<:4430checkmark:848857812632076314> Added **{amount}** xp to **{member.name}#{member.discriminator}**")

        await self.bot.pg_con.execute("UPDATE levelling SET xp = $1 WHERE guild_id = $2 AND user_id = $3", db[0]["xp"] + amount, str(ctx.guild.id), str(member.id))
        await ctx.send(f"<:4430checkmark:848857812632076314> Added **{amount}** xp to **{member.name}#{member.discriminator}**")

    @commands.command()
    @commands.is_owner()
    async def remxp(self, ctx, amount:int, member: discord.Member = None):
        if member is None:
            member = ctx.author

        db = await self.bot.pg_con.fetch("SELECT * FROM levelling WHERE guild_id = $1 AND user_id = $2", str(ctx.guild.id), str(member.id))
        if not db:
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{member.name}#{member.discriminator}** is not in the database.")

        if amount > db[0]["level"]:
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{member.name}#{member.discriminator}** xp is **{db[0]['xp']}**, you can't remove **{amount}** xp.")

        await self.bot.pg_con.execute("UPDATE levelling SET xp = $1 WHERE guild_id = $2 AND user_id = $3", db[0]["xp"] - amount, str(ctx.guild.id), str(member.id))
        await ctx.send(f"<:4430checkmark:848857812632076314> Removed **{amount}** xp to **{member.name}#{member.discriminator}**")

def setup(bot):
    bot.add_cog(Levelling(bot))

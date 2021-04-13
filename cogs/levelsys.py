import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandInvokeError
import vacefron
import random
from disrank.generator import Generator
import re


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            guild = str(message.guild.id)
            author = str(message.author.id)

            
            data = await self.bot.pg_con.fetchrow("SELECT * FROM levels WHERE user_id = $1 AND guild_id = $2", author, guild)

            if not data:
                pass

            else:
                if data['xp'] >= 500000:
                    await self.bot.pg_con.execute("UPDATE levels SET xp = $1 WHERE user_id = $2 AND guild_id = $3", 0, author, guild)

                    data1 = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author)
                    
                    try:
                        await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", data1["bank"] + 100000, author)
                        await message.channel.send(f"{message.author.name}, congrats to have reached **`500.000 xp`**! Your xp has been reset to `0` and i've sent **`100.000 coins`** in your bank as reward!")
                    except Exception:
                        pass
                    
            if not data:
                await self.bot.pg_con.execute("INSERT INTO levels (user_id, guild_id, level, xp) VALUES ($1, $2, 1, 1)", author, guild)
                return

            if message.guild.id == 336642139381301249:
                return

            if message.author == self.bot.user:
                return

            author_id = str(message.author.id)
            guild_id = str(message.guild.id)

            user = await self.bot.pg_con.fetch("SELECT * FROM levels WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)

            if not user:
                await self.bot.pg_con.execute("INSERT INTO levels (user_id, guild_id, level, xp) VALUES ($1, $2, 1, 1)", author_id, guild_id)
                return

            number = random.randint(1, 125)

            user = await self.bot.pg_con.fetchrow("SELECT * FROM levels WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)
            await self.bot.pg_con.execute("UPDATE levels SET xp = $1 WHERE user_id = $2 AND guild_id = $3", user["xp"] + number, author_id, guild_id)
        except AttributeError:
            pass


    @commands.command(help="Raise your level with coins")
    async def lvlup(self, ctx, levels=None):
        if levels == None:
            levels = 1

        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM levels WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)
        user1 = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        bal = user1[0]["bank"]
        coins = ""
        amount = 0
        if user[0]["level"] <= 20:
            coins = "5000"
            amount = 5000
        if user[0]["level"] > 20:
            coins = "10000"
            amount = 10000
        if user[0]["level"] > 50:
            coins = "20000"
            amount = 20000
        if user[0]["level"] > 100:
            coins = "50000"
            amount = 50000
        if user[0]["level"] > 150:
            coins = "100000"
            amount = 100000
        if user[0]["level"] > 200:
            coins = "250000"
            amount = 250000
        if user[0]["level"] > 300:
            coins = "500000"
            amount = 500000
        if user[0]["level"] > 500:
            coins = "1000000"
            amount = 1000000
        
    
        amount=int(amount)
        if bal < amount-1:
            await ctx.send(f"<:ikillyou:819694934432022528> **Level-Up** failed: needed **{coins}** coins!")
            return

        if ctx.author == self.bot.user:
            return

        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        if not user:
            return await ctx.send("You don't have a balance, open one with `ami bal` and start level up!")

        if levels:
            amo=int(amount)*int(levels)
            if bal < amo-1:
                await ctx.send(f"<:ikillyou:819694934432022528> **Level-Up** failed: needed **{amo}** coins!")
                return
            else:
                await ctx.send(f"<:maeHeart:820992680808939520> {ctx.author.mention} goes from level **{user[0]['level']}** to level **{user[0]['level'] + int(levels)}!**")
        else:
            await ctx.send(f"<:maeHeart:820992680808939520> {ctx.author.mention} is now level **{user[0]['level'] + int(levels)}!**")

        ct = amount*int(levels)
        await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", user1[0]["bank"] - ct, author_id)
        await self.bot.pg_con.execute("UPDATE levels SET level = $1 WHERE user_id = $2 AND guild_id = $3", user[0]["level"] + int(levels), author_id, guild_id)

    @commands.command(help="Set your custom level card background! The link needs to redirect directly to the image.\nExample: ami setlevelbg https://wallpapercave.com/wp/wp6042272.jpg")
    async def setlevelbg(self, ctx, link):
        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',ctx.message.content.lower())
        if not urls:
            return await ctx.send("This isn't an url.")
        
        await self.bot.pg_con.execute("UPDATE levels SET level_bg = $1 WHERE user_id = $2 AND guild_id = $3", link, author_id, guild_id)
        await ctx.send(f"<a:tup:819703490162458735> `{link}`\nBackground set! If you want to change it again, resend this command.\n(Tip: If your background was not set, the link isn't correct, so change link.)")


    @commands.command(help="See your level or a member level")
    async def lvl(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
            
        author_id = str(member.id)
        guild_id = str(ctx.guild.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM levels WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)

        if not data:
            return await ctx.send("The member has 0 xp and it is level 0.")

        bg = data[0]["level_bg"]
        if bg == None:
            bg = "https://cdn.statically.io/img/wallpapercave.com/wp/wp3025493.png"

        rank = await self.bot.pg_con.fetchval("SELECT count(*)+1 FROM levels WHERE guild_id = $1 AND level > (SELECT level FROM levels WHERE guild_id = $1 AND user_id = $2)", guild_id, author_id)
        

        try:
            avatar = member.avatar_url
            status = str(member.status)
            name = f"{member.name}#{member.discriminator}"
            args = {
                'bg_image' : f"{bg}", # Background image link 
                'profile_image' : f'{avatar}', # User profile picture link
                'level' : int(data[0]['level']), # User current level 
                'current_xp' : 0, # Current level minimum xp 
                'user_xp' : int(data[0]['xp']), # User current xp
                'next_xp' : 500000, # xp required for next level
                'user_position' : int(rank), # User position in leaderboard
                'user_name' : f'{name}', # user name with descriminator 
                'user_status' : f'{status}', # User status eg. online, offline, idle, streaming, dnd
            }

            image = Generator().generate_profile(**args)

            # In a discord command
            file = discord.File(fp=image, filename='image.png')
            await ctx.send(file=file)
        except Exception:
            avatar = ctx.author.avatar_url
            status = str(member.status)
            name = f"{ctx.author.name}#{ctx.author.discriminator}"
            args = {
                'bg_image' : "https://cdn.statically.io/img/wallpapercave.com/wp/wp3025493.png", # Background image link 
                'profile_image' : f'{avatar}', # User profile picture link
                'level' : int(data[0]['level']), # User current level 
                'current_xp' : 0, # Current level minimum xp 
                'user_xp' : int(data[0]['xp']), # User current xp
                'next_xp' : 500000, # xp required for next level
                'user_position' : int(rank), # User position in leaderboard
                'user_name' : f'{name}', # user name with descriminator 
                'user_status' : f'{status}', # User status eg. online, offline, idle, streaming, dnd
            }

            image = Generator().generate_profile(**args)

            # In a discord command
            file = discord.File(fp=image, filename='image.png')
            await ctx.send(file=file)




def setup(bot):
    bot.add_cog(Levels(bot))
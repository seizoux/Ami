import discord
from discord.ext import commands
import datetime
import asyncio
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import async_cleverbot as ac
import time
from io import BytesIO
from wonderwords import RandomWord
import humanize
import typing
from cogsf.defs import is_team

def lead_func(pfp: typing.List[BytesIO], user_name:str, user_bal:str):
    with Image.open("assets/leaderboard.png") as bg:

        font = ImageFont.truetype("fonts/bebas.ttf", 90)
        font2 = ImageFont.truetype("fonts/antom.ttf", 125)
        draw = ImageDraw.Draw(bg)

        text = f"{user_name}"

        text2 = f"{user_bal}"

        x, y = 130, 200

        x2, y2 = x+1300, y

        fillcolor = "#6495ED"
        shadowcolor = "black"

        fillcolor2 = "#DC143C"
        shadowcolor2 = "black"

        # thin border
        draw.text((x-1, y), text, font=font, fill=shadowcolor)
        draw.text((x+1, y), text, font=font, fill=shadowcolor)
        draw.text((x, y-1), text, font=font, fill=shadowcolor)
        draw.text((x, y+1), text, font=font, fill=shadowcolor)

        # thicker border
        draw.text((x-1, y-1), text, font=font, fill=shadowcolor)
        draw.text((x+1, y-1), text, font=font, fill=shadowcolor)
        draw.text((x-1, y+1), text, font=font, fill=shadowcolor)
        draw.text((x+1, y+1), text, font=font, fill=shadowcolor)

        draw.text((x, y), text, font=font, fill=fillcolor)

        # thin border
        draw.text((x2-1, y2), text2, font=font, fill=shadowcolor2)
        draw.text((x2+1, y2), text2, font=font, fill=shadowcolor2)
        draw.text((x2, y2-1), text2, font=font, fill=shadowcolor2)
        draw.text((x2, y2+1), text2, font=font, fill=shadowcolor2)

        # thicker border
        draw.text((x2-1, y2-1), text2, font=font, fill=shadowcolor2)
        draw.text((x2+1, y2-1), text2, font=font, fill=shadowcolor2)
        draw.text((x2-1, y2+1), text2, font=font, fill=shadowcolor2)
        draw.text((x2+1, y2+1), text2, font=font, fill=shadowcolor2)

        draw.text((x2, y2), text2, font=font, fill=fillcolor2)

        x3, y3 = x-90, y
        for i in pfp:
            y3 += 86
            with Image.open(i).convert("RGBA") as pfp:
                image1 = pfp.resize((80,80), resample=Image.NEAREST, reducing_gap=1)
                bg.paste(image1,(x3,y3-80))
                image1.close()

        buffer = BytesIO()
        bg.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

class Eco(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "Economy"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Eco Loaded")


    @commands.command(help="See the global <:cupcake:845632403405012992> leaderboard!\nThis command shows you the people with most <:cupcake:845632403405012992> in their balances.", aliases = ["lb"])
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def leaderboard(self, ctx):
        msg = await ctx.send("<:4430checkmark:848857812632076314> Loading leaderboard...")
        user = await self.bot.pg_con.fetch("SELECT user_id, sum(wallet+bank) AS total, RANK() OVER (ORDER BY sum(bank+wallet) DESC) FROM users GROUP BY user_id LIMIT $1", 10)
        top = []
        amount = []
        avatar_list = []
        index = 0
        for i in user:
            index += 1
            member = self.bot.get_user(int(i["user_id"])) or (await self.bot.fetch_user(int(i["user_id"])))
            coins = i["total"]
            asse = member.avatar_url_as(size=512)
            asset = BytesIO(await asse.read())
            avatar_list.append(asset)
            top.append(f"| {member.name}#{member.discriminator}")
            amount.append(f"{coins:,}")


        name_list = "\n".join(top)
        amount_list = "\n".join(amount)
        
        buffer = await self.bot.loop.run_in_executor(None, lead_func, avatar_list, name_list, amount_list)
        file=discord.File(fp=buffer, filename="leaderboard.png")
        try:
            await msg.delete()
        except discord.NotFound:
            pass
        await ctx.send(file=file)


    # Economy system commands
    @commands.command(help="Take a look on your actual balance, else mention a member to see the balance of that member.\nWith this command you can check your wallet, bank, investments and your awful pet.", aliases=["bal"])
    async def balance(self, ctx, member: discord.User = None):
        author_id = str(ctx.author.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        if not user:
            await self.bot.pg_con.execute("INSERT INTO users (user_id, wallet, bank) VALUES ($1, 100, 100)", author_id)
            em = discord.Embed(description="<:greenTick:596576670815879169> Dude, your balance is now ready to store <:cupcake:845632403405012992>! Start doing `ami bal` again to see your actual balance.", color = 0xffcff1)
            await ctx.send(embed=em)
            return

        if member == None:
            member = ctx.author if not member else member

        if member:
            member_id = str(member.id)
            user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", member_id)

            if not user:
                return await ctx.reply("<:redTick:596576672149667840> This member doesn't have a balance.")

            invest = user[0]['investments']
            if not invest:
                invest = "0"

            earned = user[0]['total_earn']
            if not earned:
                earned = "0"

            petsd = user[0]["pet_name"]
            petse = user[0]["pet_tag"]

            phrase = ''
            
            if petse == None:
                petse = petsd

            if petsd == None:
                phrase = "Seems you don't have **`a pet`**, hurry up, and go to buy one to get __useful__ mining boosts!"
            else:
                phrase = f'You also have a companion of mine called <:doggo:820992892515778650> **`{petse}`**'

            z = f"You have <:cupcake:845632403405012992> **`{user[0]['wallet']}`** in your **wallet** and <:cupcake:845632403405012992> **`{user[0]['bank']}`** in your **bank**. You've profited with <:stats:852923361948467240> **`{invest} investments`** and you've earned <:cupcake:845632403405012992> **`{earned}`** since you've started. {phrase}"
            user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", member_id)
            em=discord.Embed(color=0xffcff1)
            em.add_field(name="<a:9123_red_circle:819689872821583960> Balance", value =f"{z}", inline = False)
            em.set_author(name=f"{member.name}", icon_url=f"{member.avatar_url}")
            em.set_thumbnail(url=member.avatar_url)
            em.set_footer(text="Ami S.R.L Bank ®", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=em)
        else:
            member_id = str(member.id)
            user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

            invest = user[0]['investments']
            if not invest:
                invest = "0"

            earned = user[0]['total_earn']
            if not earned:
                earned = "0"

            petsd = user[0]["pet_name"]
            petse = user[0]["pet_tag"]

            phrase = ''
            
            if petse == None:
                petse = petsd

            if petsd == None:
                phrase = "Seems you don't have **`a pet`**, hurry up, and go to buy one to get __useful__ mining boosts!"
            else:
                phrase = f'You also have a companion of mine called <:doggo:820992892515778650> **`{petse}`**'


            z = f"You have <:cupcake:845632403405012992> **`{user[0]['wallet']}`** in your **wallet** and <:cupcake:845632403405012992> **`{user[0]['bank']}`** in your **bank**. You've profited with <:stats:852923361948467240> **`{invest} investments`** and you've earned <:cupcake:845632403405012992> **`{earned}`** since you've started. {petse}"
            user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", member_id)
            em=discord.Embed(color=0xffcff1)
            em.add_field(name="<a:9123_red_circle:819689872821583960> Balance", value =f"{z}", inline = False)
            em.set_author(name=f"{member.name}", icon_url=f"{member.avatar_url}")
            em.set_thumbnail(url=member.avatar_url)
            em.set_footer(text="Ami S.R.L Bank ®", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=em)



    @commands.command(help="Swing your powerful pickaxe's in a cave and mine <:cupcake:845632403405012992>!\nWith a pet, this command profit more <:cupcake:845632403405012992>.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def mine(self, ctx):
        author_id = str(ctx.author.id)
        users = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        if not users:
            await self.bot.pg_con.execute("INSERT INTO users (user_id, wallet, bank) VALUES ($1, 100, 100)", author_id)
            em = discord.Embed(description="<:greenTick:596576670815879169> Seems you're trying to mine without a balance.. i've opened one for you, now you can earn and store <:cupcake:845632403405012992>!", color = 0xffcff1)
            await ctx.send(embed=em)

        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)

        earnings=random.randrange(100, 700)
        pickaxe=random.randrange(1, 100)

        pet = user["pet_name"]
        earning = 0
        earning1 = 0
        perc = ""

        if pet:
            if pet == "Artic Husky":
                perc = "+5%"
                e = (5/100)*earnings
                earning = earnings + e
            elif pet == "White Ocelot":
                perc = "+20%"
                e = (20/100)*earnings
                earning = earnings + e
            elif pet == "Baby Dragon":
                perc = "+25%"
                e = (25/100)*earnings
                earning = earnings + e
            elif pet == "Black Rabbit":
                perc = "+30%"
                e = (30/100)*earnings
                earning = earnings + e
            elif pet == "Ice Golem":
                perc = "+50%"
                e = (50/100)*earnings
                earning = earnings + e
            elif pet == "Super Roo":
                perc = "+55%"
                e = (55/100)*earnings
                earning = earnings + e
            elif pet == "Silver Cat":
                perc = "+60%"
                e = (60/100)*earnings
                earning = earnings + e
            elif pet == "Iron Turtle":
                perc = "+65%"
                e = (65/100)*earnings
                earning = earnings + e
            elif pet == "Primordial Butterfly":
                perc = "+70%"
                e = (70/100)*earnings
                earning = earnings + e
            elif pet == "Mystic Pig":
                perc = "+75%"
                e = (75/100)*earnings
                earning = earnings + e
            elif pet == "Gold Crocodile":
                perc = "+80%"
                e = (80/100)*earnings
                earning = earnings + e
    

            pett = users[0]["pet_tag"]
            if pett == None:
                pett = pet
            em = discord.Embed(description=f"⛏️ You used **{pickaxe}%** of your pickaxe's power, and earned <:cupcake:845632403405012992> **{earnings}**!\n<:maeHeart:820992680808939520> Thanks to **`{pett}`**, you've got <:cupcake:845632403405012992> **{perc}** (**`{round(e)}`**)!", color = 0xffcff1)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)

            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user["wallet"] + 1*earning, author_id)
            await self.bot.pg_con.execute("UPDATE users SET total_earn = $1 WHERE user_id = $2", user["total_earn"] + 1*earning, author_id)

        else:
            em = discord.Embed(description=f"⛏️ You used **{pickaxe}%** of your pickaxe's power, and earned <:cupcake:845632403405012992> **{earnings}**!\n(Seems you didn't have a pet.. why not? Check it in `ami petshop`!)", color = 0xffcff1)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)

            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user["wallet"] + 1*earnings + 1*earning1, author_id)  
            await self.bot.pg_con.execute("UPDATE users SET total_earn = $1 WHERE user_id = $2", user["total_earn"] + 1*earnings + 1*earning1, author_id)  

    @commands.command(help="Invest your awful <:cupcake:845632403405012992> and maybe earn more <:cupcake:845632403405012992>!\n50% of doubling the investment, 50% to lose the total investment.")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def invest(self, ctx, amount=None):
        if not amount:
            return self.bot.get_command("invest").reset_cooldown(ctx)

        author_id = str(ctx.author.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        wallet = data[0]["wallet"]

        if not data:
            self.bot.get_command("invest").reset_cooldown(ctx)
            return await ctx.send("<:redTick:596576672149667840> Seems you don't have a balance: open one with `ami bal` to can invest <:cupcake:845632403405012992>!.")


        if amount == "all":
            if wallet > 1000000:
                await ctx.reply("<:redTick:596576672149667840> You have more than <:cupcake:845632403405012992> **`1 million`** in your wallet, max invest is **`1 million`**.")
                return self.bot.get_command("invest").reset_cooldown(ctx)
            if wallet <= 0:
                await ctx.reply(f"<:redTick:596576672149667840> You have <:cupcake:845632403405012992> {wallet} in your wallet, investment failed.")
                return self.bot.get_command("invest").reset_cooldown(ctx)
            amount = wallet

        if int(amount) > 1000000:
            await ctx.reply("<:redTick:596576672149667840> You can't invest more than <:cupcake:845632403405012992> **`1 million`**.")
            return self.bot.get_command("invest").reset_cooldown(ctx)

        if int(amount) > wallet:
            self.bot.get_command("invest").reset_cooldown(ctx)
            return await ctx.send("<:redTick:596576672149667840> You don't have so much <:cupcake:845632403405012992> in your pocket.")

        if int(amount) < 0:
            self.bot.get_command("invest").reset_cooldown(ctx)
            return await ctx.send("<:redTick:596576672149667840> You can't trade negative imports. (0, -1)")

        s = RandomWord()
        answer = s.word()
        earn = random.randint(int(amount), int(amount)*2)
        profit = int(earn) - int(amount)
        both = ["yes", "no"]
        pon = random.choice(both)

        if pon == "yes":
            em = discord.Embed(description=f"<a:ayamecloser:820999193199509554> You've invested <:cupcake:845632403405012992> **`{amount}`** in **`{answer}`** and earned <:cupcake:845632403405012992> **`{earn}`**, with a profit of <:cupcake:845632403405012992> **`{profit}`**! You can invest again in **`1 hour`**!", color = 0xffcff1)
            em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=em)
            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data[0]["wallet"] - int(amount), author_id)
            await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", data[0]["bank"] + int(earn), author_id)
            await self.bot.pg_con.execute("UPDATE users SET total_earn = $1 WHERE user_id = $2", data[0]["total_earn"] + int(earn), author_id)
            await self.bot.pg_con.execute("UPDATE users SET investments = $1 WHERE user_id = $2", data[0]["investments"] + 1, author_id)

        elif pon == "no":
            em = discord.Embed(description=f"<a:ayamecloser:820999193199509554> You've invested <:cupcake:845632403405012992> **`{amount}`** in **`{answer}`** but your investment was a total mistake and u lost all. You can invest again in **`1 hour`**!", color = 0xffcff1)
            em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=em)
            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data[0]["wallet"] - int(amount), author_id)


    @commands.command(help="Get your daily gift with <:cupcake:845632403405012992> and items!\nYou can reedem this gift every 24h.")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        author_id = str(ctx.author.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        if not user:
            await self.bot.pg_con.execute("INSERT INTO users (user_id, wallet, bank) VALUES ($1, 100, 100)", author_id)
            em = discord.Embed(description="<:greenTick:596576670815879169> Ayo, i've open a balance for you: now you can redeem your daily gift!", color = 0xffcff1)
            await ctx.send(embed=em)
            self.bot.get_command("daily").reset_cooldown(ctx)
            return

        await self.bot.pg_con.execute("UPDATE users SET daily_streak = $1 WHERE user_id = $2", user[0]["daily_streak"] + 1, author_id)
        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)

        earnings=random.randrange(1500, 15000)
        ite = await self.bot.pg_con.fetchrow("SELECT * FROM items WHERE user_id = $1", author_id)
        items = ["<:waterbottle:831186859056562277> Water Bottle", "<:redrum:831182405444173855> RedRum"]
        itemsc = random.choice(items)
        word = ""

        if ite:
            if itemsc == "<:waterbottle:831186859056562277> Water Bottle":
                word = "water_bottles"
                await self.bot.pg_con.execute("UPDATE items SET water_bottles = $1 WHERE user_id = $2", ite['water_bottles'] + 1, author_id)
            elif itemsc == "<:redrum:831182405444173855> RedRum":
                word = "redrums"
                await self.bot.pg_con.execute("UPDATE items SET redrums = $1 WHERE user_id = $2", ite['redrums'] + 1, author_id)

            user_daily = user["daily_streak"]

            if user_daily is None:
                user_daily = 1

            em = discord.Embed(title=f"{ctx.author.name} daily reward!", description=f'`Wallet` : <:cupcake:845632403405012992> **{user["wallet"]}** ⇒ <:cupcake:845632403405012992> **{user["wallet"] + earnings}** | (<:cupcake:845632403405012992> `+{earnings}`)\n\n`Items` : **{itemsc}** [`{ite[word]}`] ⇒ **`{ite[word] + 1}`**\n\n```fix\n◎ Daily Streak : #{user_daily}\n```', color = 0xffcff1)
            em.set_footer(text='Check "ami help cuppy" for more rewards!')
            em.set_thumbnail(url=ctx.author.avatar_url)
            await ctx.reply(embed=em)

            await asyncio.sleep(3)

            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user["wallet"] + earnings, author_id)
            await self.bot.pg_con.execute("UPDATE users SET total_earn = $1 WHERE user_id = $2", user["total_earn"] + earnings, author_id)
        
        else:
            user_daily = user["daily_streak"]

            if user_daily is None:
                user_daily = 1

            em = discord.Embed(title=f"{ctx.author.name} daily reward!", description=f'`Wallet` : <:cupcake:845632403405012992> **{user["wallet"]}** ⇒ <:cupcake:845632403405012992> **{user["wallet"] + earnings}** | (<:cupcake:845632403405012992> `+{earnings}`)\n\n`Items` : **BUY A GARAGE TO STORE ITEMS! (`ami buygarage`)**\n\n```fix\n◎ Daily Streak : #{user_daily}\n```', color = 0xffcff1)
            em.set_footer(text='Check "ami help cuppy" for more rewards!')
            em.set_thumbnail(url=ctx.author.avatar_url)
            await ctx.reply(embed=em)

            await asyncio.sleep(3)

            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user["wallet"] + earnings, author_id)
            await self.bot.pg_con.execute("UPDATE users SET total_earn = $1 WHERE user_id = $2", user["total_earn"] + earnings, author_id)



    @commands.command(help="Withdraw <:cupcake:845632403405012992> from your bank.\nBe careful, people can rob your <:cupcake:845632403405012992> from your wallet.", aliases = ["wd"])
    async def withdraw(self, ctx, amount=None):
        author_id = str(ctx.author.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        if not user:
            await self.bot.pg_con.execute("INSERT INTO users (user_id, wallet, bank) VALUES ($1, 100, 100)", author_id)
            em = discord.Embed(description="<:greenTick:596576670815879169> Seems you haven't open a balance.. no problem, i've opened one for you, have fun!", color = 0xffcff1)
            await ctx.send(embed=em)

        if amount == None:
            em = discord.Embed(description="<:redTick:596576672149667840> Specify an amount!", color = 0xffcff1)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        bal=user["bank"]

        if amount == "all":
            if user["bank"] == 0:
                return await ctx.reply("<:redTick:596576672149667840> You don't have anything to withdraw.")
            amount=user["bank"]

        amount=int(amount)
        if amount > user["bank"]:
                em = discord.Embed(description=f"<:redTick:596576672149667840> You don't have <:cupcake:845632403405012992> {amount}!", color = 0xffcff1)
                em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                await ctx.send(embed=em)
                return
        if amount < 0:
            em = discord.Embed(description="<:redTick:596576672149667840> You can't preleve negative imports (0, -1 ecc)", color = 0xffcff1)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", user["bank"] -1*amount, author_id)
        await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user["wallet"] + amount, author_id)

        em = discord.Embed(description=f"<:greenTick:596576670815879169> You have **withdrawn** <:cupcake:845632403405012992> `{amount}`!", color = 0xffcff1)
        em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
        await ctx.send(embed=em)


    @commands.command(help="Deposit your <:cupcake:845632403405012992> into your bank to block other people from robbing it.", aliases = ["dep"])
    async def deposit(self, ctx, amount=None):
        author_id = str(ctx.author.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        if not user:
            await self.bot.pg_con.execute("INSERT INTO users (user_id, wallet, bank) VALUES ($1, 100, 100)", author_id)
            em = discord.Embed(description="<:greenTick:596576670815879169> You didn't open a balance, so i've opened one new for you, have fun!", color = 0xffcff1)
            await ctx.send(embed=em)

        if amount == None:
            em = discord.Embed(description="<:redTick:596576672149667840> Specify an amount!", color = 0xffcff1)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        bal=user["wallet"]

        if amount == "all":
            if bal == 0:
                return await ctx.reply("<:redTick:596576672149667840> You don't have anything to deposit.")
            amount=bal

        amount=int(amount)
        if amount > bal:
                em = discord.Embed(description=f"<:redTick:596576672149667840> You don't have <:cupcake:845632403405012992> {amount}!", color = 0xffcff1)
                em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                await ctx.send(embed=em)
                return
        if amount < 0:
            em = discord.Embed(description="<:redTick:596576672149667840> You can't deposit negative imports (0, -1 ecc)", color = 0xffcff1)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user["wallet"] - 1*amount, author_id)
        await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", user["bank"] + amount, author_id)

        em = discord.Embed(description=f"<:greenTick:596576670815879169> You have **deposited** <:cupcake:845632403405012992> `{amount}`!", color = 0xffcff1)
        em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
        await ctx.send(embed=em)


    @commands.command(help="Send some <:cupcake:845632403405012992> to other members to make their day's!\nYou can send also cups to bots, but there's no reason to do it, except if you want a bot in the leaderboard.")
    async def send(self, ctx, member: discord.Member, amount=None):
        author_id = str(ctx.author.id)
        member_id = str(member.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        if not user:
            await self.bot.pg_con.execute("INSERT INTO users (user_id, wallet, bank) VALUES ($1, 100, 100)", member_id)
            em = discord.Embed(description="<:greenTick:596576670815879169> From now you have a balance! Start to earn some <:cupcake:845632403405012992> with mining!", color = 0xffcff1)
            await ctx.send(embed=em)

        if amount == None:
            em = discord.Embed(description="<:redTick:596576672149667840> Specify an amount!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        user1 = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", member_id)
        if not user1:
            return await ctx.send(f"<:redTick:596576672149667840> {ctx.author.mention}, this member doesn't have a balance, so you can't send <:cupcake:845632403405012992> at him.")
            
        bal=user["bank"]

        if amount == "all":
            if bal == 0:
                return await ctx.reply("<:redTick:596576672149667840> You don't have anything to send.")
            amount=bal

        amount=int(amount)
        if amount > bal:
                em = discord.Embed(description=f"<:redTick:596576672149667840> You don't have <:cupcake:845632403405012992> {amount}!", color = 0xffcff1)
                em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                await ctx.send(embed=em)
                return
        if amount < 0:
            em = discord.Embed(description="<:redTick:596576672149667840> You can't deposit negative imports (0, -1 ecc)", color = 0xffcff1)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        if member == ctx.author:
            em = discord.Embed(description="<:redTick:596576672149667840> You can't send <:cupcake:845632403405012992> at yourself.", color = 0xffcff1)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", user["bank"] -1*amount, author_id)


        em = discord.Embed(description=f"<:greenTick:596576670815879169> You've sent <:cupcake:845632403405012992> **`{amount}`** at **{member.name}**!", color = 0xffcff1)
        em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
        await ctx.send(embed=em)
        await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user1["wallet"] + amount, member_id)


    @commands.command(help="Rob <:cupcake:845632403405012992> to other members wallets!\nIf the member have less than <:cupcake:845632403405012992> 100, the rob will fail.")
    @commands.cooldown(1, 14400, commands.BucketType.user)
    async def rob(self, ctx, member: discord.Member):
        author_id = str(ctx.author.id)
        member_id = str(member.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", member_id)

        if not user:
            self.bot.get_command("rob").reset_cooldown(ctx)
            await self.bot.pg_con.execute("INSERT INTO users (user_id, wallet, bank) VALUES ($1, 100, 100)", member_id)
            em = discord.Embed(description="<:greenTick:596576670815879169> Ok, you're trying to rob someone, but where you store the coins?.. I've opened a balance for you, use it.", color = 0xffcff1)
            await ctx.send(embed=em)

        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", member_id)
        bal=user["wallet"]

        if member.id == ctx.author.id:
            self.bot.get_command("rob").reset_cooldown(ctx)
            await ctx.send("<:redTick:596576672149667840> You can't rob at yourself.")
            return

        if bal < 100:
                em = discord.Embed(description=f"<:redTick:596576672149667840> No profit, **`{member.name}`** is really poor.", color = 0xffcff1)
                em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                await ctx.send(embed=em)
                return

        earnings=random.randrange(0, int(bal))

        await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user["wallet"] - earnings, member_id)
        await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user["wallet"] + earnings, author_id)

        em = discord.Embed(description=f"<:greenTick:596576670815879169> You've robbed <:cupcake:845632403405012992> **`{earnings}`** at **{member.name}**!", color = 0xffcff1)
        em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
        await ctx.send(embed=em)

        await self.bot.pg_con.execute("UPDATE users SET total_earn = $1 WHERE user_id = $2", user["total_earn"] + earnings, author_id)

    @commands.command(help="Change the name of your pet!\nThis name will stay also for future bought pets, you can change it whenever you want to.")
    async def petname(self, ctx, *, petname):
        author_id = str(ctx.author.id)

        if len(petname) > 10:
            return await ctx.send("<:redTick:596576672149667840> Your pet name can't be over 10 letters.")

        if petname == None:
            return await ctx.send("<:redTick:596576672149667840> Pet name not provided. Usage: `ami petname <newpetname>`")

        author_id = str(ctx.author.id)
        pet = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)
        petn = pet[0]["pet_name"]
        if not petn:
            return await ctx.send("<:redTick:596576672149667840> You don't have a pet, buy one before try to set a name to it.")

        await self.bot.pg_con.execute("UPDATE users SET pet_tag = $1 WHERE user_id = $2", petname, author_id)
        await ctx.send(f"<:greenTick:596576670815879169> Perfect! Your pet (**`{petn}`**) now has the name **{petname}**")

    @commands.command(help="Check your current pet and what boost it gave to you!")
    async def mypet(self, ctx):
        author_id = str(ctx.author.id)
        pet = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)
        petn = pet[0]["pet_name"]
        pett = pet[0]["pet_tag"]
        
        if petn == None:
            return await ctx.send("<:redTick:596576672149667840> You don't have a pet, check what pets are aviable in `ami petshop`!")
        
        if pett == None:
            pett = "No custom name"
        perc = ""
        if petn == "Artic Husky":
            perc = "5%"
        elif petn == "White Ocelot":
            perc = "20%"
        elif petn == "Baby Dragon":
            perc = "25%"
        elif petn == "Black Rabbit":
            perc = "30%"
        elif petn == "Ice Golem":
            perc = "50%"
        elif petn == "Super Roo":
            perc = "55%"
        elif petn == "Silver Cat":
            perc = "60%"
        elif petn == "Iron Turtle":
            perc = "65%"
        elif petn == "Primordial Butterfly":
            perc = "70%"
        elif petn == "Mystic Pig":
            perc = "75%"
        elif petn == "Gold Crocodile":
            perc = "80%"
        await ctx.send(f"<:greenTick:596576670815879169> {ctx.author.mention}, here it is your __pet__ info:\n**{petn}** (`{pett}`)\nThis pet will make you gain <:cupcake:845632403405012992> **+{perc}** from `ami mine`!")

    @commands.command(help="Check what pet's are available's and buy one!\nPet's are one of the most useful thing to earn <:cupcake:845632403405012992> faster.")
    async def petshop(self, ctx):
        em = discord.Embed(title="<:status_streaming:596576747294818305> Pet Shop", description="**<:status_idle:596576773488115722> Artic Husky** : <:cupcake:845632403405012992> `3000 - +5% Mining`\n**<:status_idle:596576773488115722> White Ocelot** : <:cupcake:845632403405012992> `20000 - +20% Mining`\n**<:status_idle:596576773488115722> Baby Dragon** : <:cupcake:845632403405012992> `35000 - +25% Mining`\n**<:status_idle:596576773488115722> Black Rabbit** : <:cupcake:845632403405012992> `50000 - +30% Mining`\n**<:status_idle:596576773488115722> Ice Golem** : <:cupcake:845632403405012992> `75000 - +50% Mining`\n**<:status_idle:596576773488115722> Super Roo** : <:cupcake:845632403405012992> `125000 - +55% Mining`\n**<:status_idle:596576773488115722> Silver Cat** : <:cupcake:845632403405012992> `150000 - +60% Mining`\n**<:status_idle:596576773488115722> Iron Turtle** : <:cupcake:845632403405012992> `200000 - +65% Mining`\n**<:status_idle:596576773488115722> Primordial Butterfly** : <:cupcake:845632403405012992> `300000 - +70% Mining`\n**<:status_idle:596576773488115722> Mystic Pig** : <:cupcake:845632403405012992> `350000 - +75% Mining`\n**<:status_idle:596576773488115722> Gold Crocodile** : <:cupcake:845632403405012992> `400000 - +80% Mining`\n\n<:status_streaming:596576747294818305> Buy one of this with `ami buypet <petname>`!", color = 0xffcff1)
        em.set_footer(text='You can change your pet name with "ami petname <petname>"')
        await ctx.send(embed=em)

    @commands.command(help="Buy the pet you've choosed from the petshop!\nPrices are the number next to the <:cupcake:845632403405012992>!")
    async def buypet(self, ctx, *, petname):
        author_id = str(ctx.author.id)
        pet = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        if petname == None:
            return await ctx.send("<:redTick:596576672149667840> Missing the name of the pet you want to buy, check in `ami petshop`.")

        if pet == None:
            return await ctx.send("<:redTick:596576672149667840> I didn't found you in my database: try to send `ami bal` and see if you have a balance.")

        if petname == "artic husky":
            petname = "Artic Husky"
        elif petname == "white ocelot":
            petname = "White Ocelot"
        elif petname == "baby dragon":
            petname = "Baby Dragon"
        elif petname == "black rabbit":
            petname = "Black Rabbit"
        elif petname == "ice golem":
            petname = "Ice Golem"
        elif petname == "super roo":
            petname = "Super Roo"
        elif petname == "silver cat":
            petname = "Silver Cat"
        elif petname == "iron turtle":
            petname = "Iron Turtle"
        elif petname == "primordial butterfly":
            petname = "Primordial Butterfly"
        elif petname == "mystic pig":
            petname == "Mystic Pig"
        elif petname == "gold crocodile":
            petname = "Gold Crocodile"
        
        n = str(petname)

        pets = ["Artic Husky", "White Ocelot", "Baby Dragon", "Black Rabbit", "Ice Golem", "Super Roo", "Silver Cat", "Iron Turtle", "Primordial Butterfly", "Mystic Pig", "Gold Crocodile"]
        if petname in pets:
            if petname == "Artic Husky":
                if pet[0]["wallet"] < 3000:
                    return await ctx.send("<:redTick:596576672149667840> You don't have sufficent <:cupcake:845632403405012992> to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", n, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 3000, author_id)
                await ctx.send(f"<:greenTick:596576670815879169> Congratulations! You've bought **{petname}**! This pet will make you gain <:cupcake:845632403405012992> **+5%** in `ami mine`!")

            if petname == "White Ocelot":
                if pet[0]["wallet"] < 20000:
                    return await ctx.send("<:redTick:596576672149667840> You don't have sufficent <:cupcake:845632403405012992> to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", n, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 20000, author_id)
                await ctx.send(f"<:greenTick:596576670815879169> Congratulations! You've bought **{petname}**! This pet will make you gain <:cupcake:845632403405012992> **+20%** in `ami mine`!")
            
            if petname == "Baby Dragon":
                if pet[0]["wallet"] < 35000:
                    return await ctx.send("<:redTick:596576672149667840> You don't have sufficent <:cupcake:845632403405012992> to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 35000, author_id)
                await ctx.send(f"<:greenTick:596576670815879169> Congratulations! You've bought **{petname}**! This pet will make you gain <:cupcake:845632403405012992> **+25%** in `ami mine`!")
            
            if petname == "Black Rabbit":
                if pet[0]["wallet"] < 50000:
                    return await ctx.send("<:redTick:596576672149667840> You don't have sufficent <:cupcake:845632403405012992> to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 50000, author_id)
                await ctx.send(f"<:greenTick:596576670815879169> Congratulations! You've bought **{petname}**! This pet will make you gain <:cupcake:845632403405012992> **+30%** in `ami mine`!")
            
            if petname == "Ice Golem":
                if pet[0]["wallet"] < 75000:
                    return await ctx.send("<:redTick:596576672149667840> You don't have sufficent <:cupcake:845632403405012992> to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 75000, author_id)
                await ctx.send(f"<:greenTick:596576670815879169> Congratulations! You've bought **{petname}**! This pet will make you gain <:cupcake:845632403405012992> **+50%** in `ami mine`!")

            if petname == "Super Roo":
                if pet[0]["wallet"] < 125000:
                    return await ctx.send("<:redTick:596576672149667840> You don't have sufficent <:cupcake:845632403405012992> to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 125000, author_id)
                await ctx.send(f"<:greenTick:596576670815879169> Congratulations! You've bought **{petname}**! This pet will make you gain <:cupcake:845632403405012992> **+55%** in `ami mine`!")

            if petname == "Silver Cat":
                if pet[0]["wallet"] < 150000:
                    return await ctx.send("<:redTick:596576672149667840> You don't have sufficent <:cupcake:845632403405012992> to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 150000, author_id)
                await ctx.send(f"<:greenTick:596576670815879169> Congratulations! You've bought **{petname}**! This pet will make you gain <:cupcake:845632403405012992> **+60%** in `ami mine`!")

            if petname == "Iron Turtle":
                if pet[0]["wallet"] < 200000:
                    return await ctx.send("<:redTick:596576672149667840> You don't have sufficent <:cupcake:845632403405012992> to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 200000, author_id)
                await ctx.send(f"<:greenTick:596576670815879169> Congratulations! You've bought **{petname}**! This pet will make you gain <:cupcake:845632403405012992> **+65%** in `ami mine`!")

            if petname == "Primordial Butterfly":
                if pet[0]["wallet"] < 300000:
                    return await ctx.send("<:redTick:596576672149667840> You don't have sufficent <:cupcake:845632403405012992> to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 300000, author_id)
                await ctx.send(f"<:greenTick:596576670815879169> Congratulations! You've bought **{petname}**! This pet will make you gain **+70%** coins in `ami mine`!")

            if petname == "Mystic Pig":
                if pet[0]["wallet"] < 350000:
                    return await ctx.send("<:redTick:596576672149667840> You don't have sufficent <:cupcake:845632403405012992> to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 350000, author_id)
                await ctx.send(f"<:greenTick:596576670815879169> Congratulations! You've bought **{petname}**! This pet will make you gain <:cupcake:845632403405012992> **+75%** in `ami mine`!")

            if petname == "Gold Crocodile":
                if pet[0]["wallet"] < 400000:
                    return await ctx.send("<:redTick:596576672149667840> You don't have sufficent <:cupcake:845632403405012992> to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 400000, author_id)
                await ctx.send(f"<:greenTick:596576670815879169> Congratulations! You've bought **{petname}**! This pet will make you gain <:cupcake:845632403405012992> **+80%** in `ami mine`!")
        else:
            return await ctx.reply("Dude, idk what are you searching but this pet isn't in the petshop", mention_author=False)

    @commands.command(help="This command is mostly used as a developer tool, this wont affect any balance.\nThis command just say the total <:cupcake:845632403405012992> cupcakes stored in our databse.")
    async def glbc(self,ctx,x = 5):
        gblcs = await self.bot.pg_con.fetchval("SELECT SUM(COALESCE(wallet,0) + COALESCE(bank,0)) FROM users")
        em = discord.Embed(title=f"<:cupcake:845632403405012992> storage!", description = f"```py\n» {gblcs}\n```", color = 0xffcff1)
        em.timestamp = datetime.datetime.utcnow()
        em.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=em)

    @commands.command(help="Talk with me and earn <:cupcake:845632403405012992> for total talked time.", aliases = ["oc"])
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def openchat(self, ctx):
        member_id = str(ctx.author.id)
        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", member_id)

        cleverbot = ac.Cleverbot("W.UQ2.O[ewxop*;3M'qa") # Create the Cleverbot client
        await ctx.reply("Started a chat, type `closechat` to end the conversation.\nHow it work? Just, talk with me as much more time you can:\n- **`> or = at 60 seconds`** = from __100__ to __1200__ <:cupcake:845632403405012992> (random).\n- **`between 60 & 120 seconds`** = from __400__ to __2300__ <:cupcake:845632403405012992> (random)\n- **`= or > of 120 seconds`** = from __1600__ to __12000__ <:cupcake:845632403405012992> (random)\n(You can't start the chat and not type, after 1 minute without messages, the chat will be automatically closed.)")
        start = time.time()

        while True:
            try:
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel, timeout=60.0)
            except asyncio.TimeoutError:
                end = time.time()
                tot = end - start

                if tot <= 60:
                    earn = random.randint(100, 1000)
                elif tot <= 5:
                    earn = random.randint(1, 5)
                elif tot >= 60 and tot <= 120:
                    earn = random.randint(400, 2300)
                elif tot >= 120:
                    earn = random.randint(1600, 12000)

                await ctx.send(f"**{ctx.author.name}**, ending your chat with me because you didn't send a message for `1 minute`.\nYou talked with me for **`{round(tot)} seconds`**, so you got **<:cupcake:845632403405012992> `{earn}`**, but because you ran out of time, the earn will be the half of the half of the total, so you got **<:cupcake:845632403405012992> `{round(earn/4)}`**!")
                await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", user["bank"] +1*earn/4, member_id)
                return await cleverbot.close()

            if msg.content == "closechat":
                end = time.time()
                tots = end-start

                if tots <= 60:
                    earn = random.randint(100, 1000)
                elif tots <= 5:
                    earn = random.randint(1, 5)
                elif tots >= 60 and tots <= 120:
                    earn = random.randint(400, 2300)
                elif tots >= 120:
                    earn = random.randint(1600, 12000)

                await msg.reply(f"Closing the chat, also you talked with me for **`{round(tots)} seconds`**, so you won **<:cupcake:845632403405012992> `{round(earn)}`** as a reward!")
                await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", user["bank"] +1*earn, member_id)
                return await cleverbot.close()
            else:
                response = await cleverbot.ask(msg.content)
                await msg.reply(response.text.lower())


    @commands.command(help="Take a look on our items shop, and buy items with your <:cupcake:845632403405012992>!\nThe shop is still in beta, more items will be added soon:tm:.")
    async def shop(self, ctx, page=None):
        if page == None:
            page = str(1)

        if page >= str(3):
            return await ctx.reply("<:redTick:596576672149667840> Dude, this page doesn't exist in the shop", mention_author=False)

        if page == str(1):
            em = discord.Embed(title="Items Shop", description="Use `ami buyitem <itemname> / <itemnumber>` to buy something.\n`<itemname>` must be also with capital letters.\nYou can buy more at once, like `ami buyitem Weed 5` to buy `5g` of weed" , color = 0xffcff1)
            em.add_field(name="1) <:waterbottle:831186859056562277> Water Bottle (<:cupcake:845632403405012992> 25000)", value="Drink a water bottle would be drinking a water bottle? ^^\n`Usage` : **ami drink 1**", inline = False)
            em.add_field(name="2) <:redrum:831182405444173855> RedRum (<:cupcake:845632403405012992> 75000)", value="This rum will make you a little bit drunky ^^\n`Usage` : **ami drink 2**", inline = False)
            em.add_field(name="3) <:huntingrifle:831182405686657034> Hunting Rifle (<:cupcake:845632403405012992> 125000)", value="Buy this and go hunt!\n`Usage` : **ami hunt**", inline = False)
            em.add_field(name="4) <:8680_Weed_shinier:819689872750280775> Weed (<:cupcake:845632403405012992> 150000)", value="Smoking is bad, don't buy weed.\n`Usage` : **ami smoke weed**", inline = False)
            em.set_footer(text="Page Index 1/2", icon_url=ctx.author.avatar_url)
            em.timestamp = datetime.datetime.utcnow()
            await ctx.reply(embed=em, mention_author=False)
        elif page == str(2):
            em = discord.Embed(title="Items Shop", description="Use `ami buyitem <itemname> / <itemnumber>` to buy something.\n`<itemname>` must be also with capital letters.\nYou can buy more at once, like `ami buyitem Weed 5` to buy `5g` of weed" , color = 0xffcff1)
            em.add_field(name="5) <:fishingpole:831182405717065729> Fishing Rod (<:cupcake:845632403405012992> 200000)", value="Go fishing with this super-rare fishing rod..\n`Usage` : **ami fish**", inline = False)
            em.add_field(name="6) <:computer:831186859287642122> Computer (<:cupcake:845632403405012992> 400000)", value="Want to hack the bank of someone? Use this pc!\n`Usage` : **ami bankrob @member**", inline = False)
            em.add_field(name="7) <:pixel_flower:831186859055906847> Ami's Flower (<:cupcake:845632403405012992> 10000000)", value="Ami's favourite flower, just a trophy.\n`Usage` : **No usages for this item**", inline = False)
            em.set_footer(text="Page Index 2/2", icon_url=ctx.author.avatar_url)
            em.timestamp = datetime.datetime.utcnow()
            await ctx.reply(embed=em, mention_author=False)


    @commands.command(help="Open your personal garage, where you can store your items.\nPeople can't rob you items, don't worry ;)")
    async def buygarage(self, ctx):
        author_id = str(ctx.author.id)
        d = await self.bot.pg_con.fetchrow("SELECT user_id FROM items WHERE user_id = $1", author_id)
        if not d:
            await self.bot.pg_con.execute("INSERT INTO items (user_id, water_bottles, redrums, rifles, weed, fish_rods, computers, ami_flowers, common_chests, rare_chests, epic_chests) VALUES ($1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)", author_id)
            await ctx.reply("Your garage is now ready! You can now buy and store items from the shop. Use `ami garage` to take a look on your garage!", mention_author=False)
        else:
            return await ctx.reply("<:redTick:596576672149667840> You already have a garage dude, go sleep.", mention_author=False)


    @commands.command(help="Buy items from the shop with your <:cupcake:845632403405012992>!\nThis items will be stored in your personal garage, and no one can steal it.")
    async def buyitem(self, ctx, item=None, amount=None):
        author_id = str(ctx.author.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM items WHERE user_id = $1", author_id)
        if not data:
            return await ctx.reply("<:redTick:596576672149667840> Dude, you can't buy items if you don't buy a place where store it.. use `ami buygarage` to setup your personal garage!", mention_author=False)

        items_names = ["Water Bottle", "RedRum", "Hunting Rifle", "Weed", "Fishing Rod", "Computer", "Ami Flower"]
        items_numbers = ["1", "2", "3", "4", "5", "6", "7"]

        if amount == None:
            amount = 1

        price = 0
        its = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        if item in items_names:
            if item == 'Water Bottle':
                price = 25000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't buy this item because you don't have <:cupcake:845632403405012992> **`{price}`** in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET water_bottles = $1 WHERE user_id = $2", data['water_bottles'] + int(amount), author_id)
            elif item == 'RedRum':
                price = 75000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't buy this item because you don't have <:cupcake:845632403405012992> **`{price}`** in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET redrums = $1 WHERE user_id = $2", data['redrums'] + int(amount), author_id)
            elif item == 'Hunting Rifle':
                if data['rifles'] >= 1:
                    return await ctx.reply("<:redTick:596576672149667840> You already have a rifle, you can't buy another one.", mention_author=False)
                price = 125000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't buy this item because you don't have <:cupcake:845632403405012992> **`{price}`** in your bank.", mention_author=False)
                amount = 1
                await self.bot.pg_con.execute("UPDATE items SET rifles = $1 WHERE user_id = $2", data['rifles'] + int(amount), author_id)
            elif item == 'Weed':
                price = 150000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't buy this item because you don't have <:cupcake:845632403405012992> **`{price}`** in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET weed = $1 WHERE user_id = $2", data['weed'] + int(amount), author_id)
            elif item == 'Fishing Rod':
                if data['fish_rods'] >= 1:
                    return await ctx.reply("<:redTick:596576672149667840> You already have a fishing rod, you can't buy another one.", mention_author=False)
                price = 200000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't buy this item because you don't have <:cupcake:845632403405012992> **`{price}`** in your bank.", mention_author=False)
                amount = 1
                await self.bot.pg_con.execute("UPDATE items SET fish_rods = $1 WHERE user_id = $2", data['fish_rods'] + int(amount), author_id)
            elif item == 'Computer':
                price = 400000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't buy this item because you don't have <:cupcake:845632403405012992> **`{price}`** in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET computers = $1 WHERE user_id = $2", data['computers'] + int(amount), author_id)
            elif item == 'Ami Flower':
                price = 10000000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't buy this item because you don't have <:cupcake:845632403405012992> **`{price}`** in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET ami_flowers = $1 WHERE user_id = $2", data['ami_flowers'] + int(amount), author_id)


        elif item in items_numbers:
            if item == '1':
                item = "Water Bottle"
                price = 25000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't buy this item because you don't have <:cupcake:845632403405012992> **`{price}`** in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET water_bottles = $1 WHERE user_id = $2", data['water_bottles'] + int(amount), author_id)
            elif item == '2':
                item = "RedRum"
                price = 75000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't buy this item because you don't have <:cupcake:845632403405012992> **`{price}`** in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET redrums = $1 WHERE user_id = $2", data['redrums'] + int(amount), author_id)
            elif item == '3':
                item = "Hunting Rifle"
                if data['rifles'] >= 1:
                    return await ctx.reply("<:redTick:596576672149667840> You already have a rifle, you can't buy another one.", mention_author=False)
                price = 125000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't buy this item because you don't have <:cupcake:845632403405012992> **`{price}`** in your bank.", mention_author=False)
                amount = 1
                await self.bot.pg_con.execute("UPDATE items SET rifles = $1 WHERE user_id = $2", data['rifles'] + int(amount), author_id)
            elif item == '4':
                item = "Weed"
                price = 150000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't buy this item because you don't have <:cupcake:845632403405012992> **`{price}`** in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET weed = $1 WHERE user_id = $2", data['weed'] + int(amount), author_id)
            elif item == '5':
                item = 'Fishing Rod'
                if data['fish_rods'] >= 1:
                    return await ctx.reply("<:redTick:596576672149667840> You already have a fishing rod, you can't buy another one.", mention_author=False)
                price = 200000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't buy this item because you don't have <:cupcake:845632403405012992> **`{price}`** in your bank.", mention_author=False)
                amount = 1
                await self.bot.pg_con.execute("UPDATE items SET fish_rods = $1 WHERE user_id = $2", data['fish_rods'] + int(amount), author_id)
            elif item == '6':
                item = "Computer"
                price = 400000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't buy this item because you don't have <:cupcake:845632403405012992> **`{price}`** in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET computers = $1 WHERE user_id = $2", data['computers'] + int(amount), author_id)
            elif item == '7':
                item = "Ami Flower"
                price = 10000000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't buy this item because you don't have <:cupcake:845632403405012992> **`{price}`** in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET ami_flowers = $1 WHERE user_id = $2", data['ami_flowers'] + int(amount), author_id)
        else:
            return await ctx.reply("<:redTick:596576672149667840> I didn't found this itemname / itemnumber in the shop.", mention_author=False)

        await ctx.reply(f"🌟 Well done, you've bought `{amount}` **{item}** for <:cupcake:845632403405012992> **{price}**!", mention_author=False)
        await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", its['bank'] - price, author_id)


    @commands.command(help="Check what items you have in your personal garage!\nItems will stay forever here, until you use it.")
    async def garage(self, ctx):
        author_id = str(ctx.author.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM items WHERE user_id = $1", author_id)
        if not data:
            return await ctx.reply("<:redTick:596576672149667840> You don't have a garage, and for consequent no items. Use `ami buygarage` to can use this command.", mention_author=False)

        a_bottles = 0
        a_redrums = 0
        a_rifles = 0
        a_weed = 0
        a_fishrods = 0
        a_computers = 0
        a_flowers = 0
        a_common_chests = 0
        a_rare_chests = 0
        a_epic_chests = 0

        if data['water_bottles'] >= 1:
            a_bottles = data['water_bottles']

        if data['redrums'] >= 1:
            a_redrums = data['redrums']

        if data['rifles'] == 1:
            a_rifles = "Bought"

        if data['weed'] >= 1:
            a_weed = data['weed']

        if data['fish_rods'] == 1:
            a_fishrods = "Bought"

        if data['computers'] >= 1:
            a_computers = data['computers']

        if data['ami_flowers'] >= 1:
            a_flowers = data['ami_flowers']

        if data['common_chests'] >= 1:
            a_common_chests = data['common_chests']

        if data['rare_chests'] >= 1:
            a_rare_chests = data['rare_chests']

        if data['epic_chests'] >= 1:
            a_epic_chests = data['epic_chests']

        em = discord.Embed(description=f"**`Items you can buy`**:\n<:waterbottle:831186859056562277> **Water Bottles** = **`{a_bottles}`**\n<:redrum:831182405444173855> **RedRums** = **`{a_redrums}`**\n<:huntingrifle:831182405686657034> **Rifle** = **`{a_rifles}`**\n<:8680_Weed_shinier:819689872750280775> **Weed** = **`{a_weed}g`**\n<:fishingpole:831182405717065729> **Fishing Rod** = **`{a_fishrods}`**\n<:computer:831186859287642122> **Computers** = **`{a_computers}`**\n<:pixel_flower:831186859055906847> **Ami Flowers** = **`{a_flowers}`**\n\n**`You can find chest fishing`**:\n<:common_chest:838028933920325633> **Common Chests** = **`{a_common_chests}`**\n<:rare_chest:838028934598885417> **Rare Chests** = **`{a_rare_chests}`**\n<:epic_chest:838028935479820319> **Epic Chests** = **`{a_epic_chests}`**", color = 0xffcff1)
        em.set_author(name=f"{ctx.author.name}'s' garage", icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=em, mention_author=False)


    @commands.command(help="Drink something bought from our shop!\nSee the items usage's in the shop to know what you can drink.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def drink(self, ctx, item):
        author_id = str(ctx.author.id)
        ite = await self.bot.pg_con.fetchrow("SELECT * FROM items WHERE user_id = $1", author_id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)

        if not ite:
            return await ctx.reply("<:redTick:596576672149667840> Dude, you don't have a garage, and in consequent no items. Use `ami buygarage` to open your personal garage and store items bought.", mention_author=False)

        if not data:
            return await ctx.reply("<:redTick:596576672149667840> You don't have a balance, open one with `ami bal` to can store <:cupcake:845632403405012992>.", mention_author=False)

        drinks = ["Water Bottle", "RedRum", "1", "2"]

        if item not in drinks:
            return await ctx.reply("<:redTick:596576672149667840> To drink something, use `ami drink <item_name>` or `ami drink <shop_item_number>`. You can drink only the items with `drink` in usage.", mention_author=False)

        water = ite['water_bottles']
        rum = ite['redrums']

        if item == "1":
            item = "Water Bottle"

        if item == "2":
            item = "RedRum"

        if item == "Water Bottle":
            if not water:
                return await ctx.reply("<:redTick:596576672149667840> You don't have any water bottle to drink.", mention_author=False)
            else:
                d = ['yes', 'no']
                f = random.choice(d)
                if f == "yes":
                    r = random.randint(0, 12000)
                    await ctx.reply(f"You drinked a <:waterbottle:831186859056562277> **water bottle** and you accidentally found <:cupcake:845632403405012992> **`{r}`** O.o/", mention_author=False)
                    await self.bot.pg_con.execute("UPDATE items SET water_bottles = $1 WHERE user_id = $2", ite['water_bottles'] - 1, author_id)
                    await asyncio.sleep(2)
                    await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data['wallet'] + r, author_id)
                else:
                    await ctx.reply(f"You drinked a <:waterbottle:831186859056562277> **water bottle** but this time you found **nothing**.", mention_author=False)
                    await self.bot.pg_con.execute("UPDATE items SET water_bottles = $1 WHERE user_id = $2", ite['water_bottles'] - 1, author_id)

        if item == "RedRum":
            if not rum:
                return await ctx.reply("<:redTick:596576672149667840> You don't have any red rum to drink.", mention_author=False)
            else:
                d = ['yes', 'no']
                f = random.choice(d)
                if f == "yes":
                    r = random.randint(0, 12000)
                    await ctx.reply(f"You drinked a <:redrum:831182405444173855> **RedRum**, you got a little bit drunky and you accidentally found <:cupcake:845632403405012992> **`{r}`** O.o/", mention_author=False)
                    await self.bot.pg_con.execute("UPDATE items SET redrums = $1 WHERE user_id = $2", ite['redrums'] - 1, author_id)
                    await asyncio.sleep(2)
                    await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data['wallet'] + r, author_id)
                else:
                    tot = data["wallet"] + data["bank"]
                    await ctx.reply(f"You drinked a <:redrum:831182405444173855> **RedRum**, you got a little bit drunky and you get sleep, losing **__all__** your balance (**<:cupcake:845632403405012992> `{tot}`**).", mention_author=False)
                    await self.bot.pg_con.execute("UPDATE items SET redrums = $1 WHERE user_id = $2", ite['redrums'] - 1, author_id)
                    await asyncio.sleep(1)
                    await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", 0, author_id)
                    await asyncio.sleep(1)
                    await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", 0, author_id)


    @commands.command(help="Go hunting with your hunting rifle!\nYou can buy one in our shop, without hunting rifle, you can't hunt.")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def hunt(self, ctx):
        author_id = str(ctx.author.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        ite = await self.bot.pg_con.fetchrow('SELECT * FROM items WHERE user_id = $1', author_id)

        if not ite:
            return await ctx.reply("<:redTick:596576672149667840> Dude, you don't have a garage, and in consequent no items. Use `ami buygarage` to open your personal garage and store items bought.", mention_author=False)

        if not ite['rifles']:
            return await ctx.reply("<:redTick:596576672149667840> You are without a rifle, you can't hunt with your hands, stupid dumbass.", mention_author=False)

        if not data:
            return await ctx.reply("<:redTick:596576672149667840> You don't have a balance, open one with `ami bal` to can store <:cupcake:845632403405012992>.", mention_author=False)

        animals = ['🕊 bird', '🦁 lion', '🐧 penguin', '🐀 mouse', '🐯 tiger', '🦌 deer', '🐻 bear', 'nothing']
        animals2 = random.choice(animals)
        reward = 0
        if animals2 == 'nothing':
            reward = 0
            await ctx.reply("You went hunting with your <:huntingrifle:831182405686657034> **rifle** but you shoot on a tree.", mention_author=False)
        else:
            reward = random.randint(1, 10000)
            await ctx.reply(f"You went hunting with your <:huntingrifle:831182405686657034> **hunting rifle** and you shot a **{animals2}**, you got <:cupcake:845632403405012992> **`{reward}`** as a reward!", mention_author=False)
            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data['wallet'] + reward, author_id)


    @commands.command(help="Smoke the weed you have in your garage!\nWeed are bad, be careful when smoke: something bad can happen.")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def smoke(self, ctx, item, g=None):
        author_id = str(ctx.author.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        ite = await self.bot.pg_con.fetchrow('SELECT * FROM items WHERE user_id = $1', author_id)

        can_smoke = ['weed', 'Weed']
        if item not in can_smoke:
            return await ctx.reply("<:redTick:596576672149667840> I didn't found a smokable item with this name.", mention_author=False)

        if not ite:
            return await ctx.reply("<:redTick:596576672149667840> Dude, you don't have a garage, and in consequent no items. Use `ami buygarage` to open your personal garage and store items bought.", mention_author=False)

        if not ite['weed']:
            return await ctx.reply("<:redTick:596576672149667840> You are out of weed, you can't smoke the air, go buy weed and come back here", mention_author=False)

        if not data:
            return await ctx.reply("<:redTick:596576672149667840> You don't have a balance, open one with `ami bal` to can store <:cupcake:845632403405012992>.", mention_author=False)

        if not item:
            return self.bot.get_command("smoke").reset_cooldown(ctx)

        if g == None:
            g = 1

        if int(g) > ite['weed']:
            return await ctx.reply(f"<:redTick:596576672149667840> You don't have **`{g}g`** of <:8680_Weed_shinier:819689872750280775> **weed**, go buy more weed.", mention_author=False)

        status = ['good', 'normal', 'bad']
        cstatus = random.choice(status)
        
        if cstatus == "good":
            await ctx.reply(f"You smoked **`{g}g`** of <:8680_Weed_shinier:819689872750280775> **{item}**. you take it so good, and you've sent **all** your bank amount to your mom! What a good son 😍", mention_author=False)
            await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", data['bank'] - data['bank'], author_id)
            await self.bot.pg_con.execute("UPDATE items SET weed = $1 WHERE user_id = $2", ite['weed'] - int(g), author_id)
            return

        if cstatus == "normal":
            amount = random.randint(0, data['wallet'])
            await ctx.reply(f"You smoked **`{g}g`** of <:8680_Weed_shinier:819689872750280775> **{item}**. you take it normal, but you got confused and you lost <:cupcake:845632403405012992> **`{amount}`** from your wallet, maybe you dropped your portfolio somewhere..", mention_author=False)
            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data['wallet'] - amount, author_id)
            await self.bot.pg_con.execute("UPDATE items SET weed = $1 WHERE user_id = $2", ite['weed'] - int(g), author_id)
            return

        if cstatus == "bad":
            member = random.choice(ctx.message.guild.members)
            mfetch = await self.bot.fetch_user(member.id)
            amount = random.randint(0, data['bank'])
            await ctx.reply(f"You smoked **`{g}g`** of <:8680_Weed_shinier:819689872750280775> **{item}**. you take it really bad, and you killed **{mfetch.name}**, after you get sended in jail, but you've paid <:cupcake:845632403405012992> **{amount}** to be released.", mention_author=False)
            await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", data['bank'] - amount, author_id)
            await self.bot.pg_con.execute("UPDATE items SET weed = $1 WHERE user_id = $2", ite['weed'] - int(g), author_id)
            return

    @commands.command(help="Go fishing with your fishing rod as a pro fisher!\nFishing can be so annoying, since you find a chest.")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def fish(self, ctx):
        author_id = str(ctx.author.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        ite = await self.bot.pg_con.fetchrow('SELECT * FROM items WHERE user_id = $1', author_id)

        if not ite:
            return await ctx.reply("<:redTick:596576672149667840> Dude, you don't have a garage, and in consequent no items. Use `ami buygarage` to open your personal garage and store items bought.", mention_author=False)

        if not ite['fish_rods']:
            return await ctx.reply("<:redTick:596576672149667840> You don't have a fucking fishing rod, get out of here and go buy one, and after come back to fish lmao.", mention_author=False)

        if not data:
            return await ctx.reply("<:redTick:596576672149667840> You don't have a balance, open one with `ami bal` to can store <:cupcake:845632403405012992>.", mention_author=False)

        fishes = ['🐟', '🐠', '🐡', '🦐', '🦑', '🐙', '🦞', '🦀', '🐚', '🐋', '🐬', '🦈', '🐢', '🦠', '🥽', '🥾']
        crates = ['<:common_chest:838028933920325633> Common Chest', '<:rare_chest:838028934598885417> Rare Chest', '<:epic_chest:838028935479820319> Epic Chest']

        probs = ['yes', 'maybe', 'idk', 'pheraps', 'no', 'nono', 'no.', 'fuck', 'die']
        s = random.choice(probs)

        if s == "yes":
            d = random.choice(crates)

            if d == "<:common_chest:838028933920325633> Common Chest":
                await ctx.reply(f"You went fishing with your <:fishingpole:831182405717065729> **Fishing Rod**, and you got __so lucky__! You found a **{d}**! You can open it with `ami openchest common`!", mention_author=False)
                await self.bot.pg_con.execute("UPDATE items SET common_chests = $1 WHERE user_id = $2", ite['common_chests'] + 1, author_id)
            
            if d == "<:rare_chest:838028934598885417> Rare Chest":
                await ctx.reply(f"You went fishing with your <:fishingpole:831182405717065729> **Fishing Rod**, and you got __fucking lucky__! You found a **{d}**! You can open it with `ami openchest rare`!", mention_author=False)
                await self.bot.pg_con.execute("UPDATE items SET rare_chests = $1 WHERE user_id = $2", ite['rare_chests'] + 1, author_id)

            if d == "<:epic_chest:838028935479820319> Epic Chest":
                await ctx.reply(f"You went fishing with your <:fishingpole:831182405717065729> **Fishing Rod**, and you got __extremely lucky__! You found a **{d}**! You can open it with `ami openchest epic`!", mention_author=False)
                await self.bot.pg_con.execute("UPDATE items SET epic_chests = $1 WHERE user_id = $2", ite['epic_chests'] + 1, author_id)

        else:
            d = random.choice(fishes)
            earn = random.randint(1, 300)
            await ctx.reply(f"You went fishing with your <:fishingpole:831182405717065729> **Fishing Rod**, and you got __so **`unlucky`**__! You found a **{d}** and you sold it for <:cupcake:845632403405012992> **{earn}** O.o/", mention_author=False)
            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data['wallet'] + earn, author_id)


    @commands.command(help="Became an hacker with the computer you've bought from the shop, and hack the bank of a member.\nThis is so risky, there's a chance to lose all your balance.")
    @commands.cooldown(1, 180, commands.BucketType.user)
    async def bankrob(self, ctx, member: discord.Member):
        author_id = str(ctx.author.id)
        member_id = str(member.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        data1 = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", member_id)
        ite = await self.bot.pg_con.fetchrow('SELECT * FROM items WHERE user_id = $1', author_id)

        if not ite:
            return await ctx.reply("<:redTick:596576672149667840> Dude, you don't have a garage, and in consequent no items. Use `ami buygarage` to open your personal garage and store items bought.", mention_author=False)

        if not ite['computers']:
            return await ctx.reply("<:redTick:596576672149667840> You don't have a fucking computer, go back to watch horny stuff.", mention_author=False)

        if not data:
            return await ctx.reply("<:redTick:596576672149667840> You don't have a balance, open one with `ami bal` to can store <:cupcake:845632403405012992>.", mention_author=False)
        
        if not data1:
            return await ctx.reply("<:redTick:596576672149667840> This member doesn't have a balance opened.", mention_author=False)

        if data1['bank'] < 100000:
            self.bot.get_command("bankrob").reset_cooldown(ctx)
            return await ctx.reply("<:redTick:596576672149667840> This member have less than **100k** coins in the bank: member with <:cupcake:845632403405012992> **100k** or less in the bank have the **`hack-protection`**.", mention_author=False)

        chs = ['yes', 'no']
        ddf = random.choice(chs)
        if ddf == "yes":
            hacked = random.randint(0, data1['bank'])
            nudes = random.randint(1, 100)
            await ctx.reply(f"You became a __professional__ hacker with your <:computer:831186859287642122> **Computer**, and in the meanwhile you've **found & got**:\n\n⁕ `{nudes}` **{member.name}** nudes 😏\n⁕ `{hacked}` <:cupcake:845632403405012992> hacked from the **{member.name}** bank 😎")
            await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", data['bank'] + hacked, author_id)
            await asyncio.sleep(2)
            await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", data1['bank'] - hacked, member_id)
            await asyncio.sleep(2)
            await self.bot.pg_con.execute("UPDATE items SET computers = $1 WHERE user_id = $2", ite['computers'] - 1, author_id)
        else:
            hacked = random.randint(0, data1['bank'])
            losed = random.randint(0, data['bank'])
            await ctx.reply(f"You became a __professional__ hacker with your <:computer:831186859287642122> **Computer**, and **you've got**:\n\n<:cupcake:845632403405012992> **{hacked*1000}** 🤩🤩🤩\n\n**`Joking`**, you failed to hack the member bank, and you got **arrested**, losing <:cupcake:845632403405012992> **{losed}**.")
            await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", data['bank'] - losed, author_id)
            await asyncio.sleep(2)
            await self.bot.pg_con.execute("UPDATE items SET computers = $1 WHERE user_id = $2", ite['computers'] - 1, author_id)


    @commands.command(help="Found a chest fishing? Open it with this command!\nChest have always amazing loots.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def openchest(self, ctx, chest):
        author_id = str(ctx.author.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        ite = await self.bot.pg_con.fetchrow('SELECT * FROM items WHERE user_id = $1', author_id)

        if not ite:
            return await ctx.reply("<:redTick:596576672149667840> Dude, you don't have a garage, and in consequent no items. Use `ami buygarage` to open your personal garage and store items bought.", mention_author=False)

        if not data:
            return await ctx.reply("<:redTick:596576672149667840> You don't have a balance, open one with `ami bal` to can store coins.", mention_author=False)

        chests = ['common', 'rare', 'epic']
        common_coins = random.randint(10000, 35000)
        rare_coins = random.randint(35000, 75000)
        epic_coins = random.randint(75000, 200000)

        coins = 0
        if chest in chests:
            if chest == "common":
                if not ite['common_chests']:
                    return await ctx.reply("<:redTick:596576672149667840> You don't have <:common_chest:838028933920325633> **Common Chests** to open.", mention_author=False)
                coins = common_coins
                msg = await ctx.reply("<a:chest_opening:838028934708592650> Opening a <:common_chest:838028933920325633> **Common Chest**.", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content="<a:chest_opening:838028934708592650> Opening a <:common_chest:838028933920325633> **Common Chest**..", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content="<a:chest_opening:838028934708592650> Opening a <:common_chest:838028933920325633> **Common Chest**...", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content=f"<a:chest_opening:838028934708592650> Opened <:common_chest:838028933920325633> **Common Chest**!\n\n× <:cupcake:845632403405012992> **`{coins}`** found!", mention_author=False)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data['wallet'] + coins, author_id)
                await asyncio.sleep(2)
                await self.bot.pg_con.execute("UPDATE items SET common_chests = $1 WHERE user_id = $2", ite['common_chests'] - 1, author_id)
            
            if chest == "rare":
                if not ite['rare_chests']:
                    return await ctx.reply("<:redTick:596576672149667840> You don't have <:rare_chest:838028934598885417> **Rare Chests** to open.", mention_author=False)
                coins = rare_coins
                msg = await ctx.reply("<a:chest_opening:838028934708592650> Opening a <:rare_chest:838028934598885417> **Rare Chest**.", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content="<a:chest_opening:838028934708592650> Opening a <:rare_chest:838028934598885417> **Rare Chest**..", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content="<a:chest_opening:838028934708592650> Opening a <:rare_chest:838028934598885417> **Rare Chest**...", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content=f"<a:chest_opening:838028934708592650> Opened <:rare_chest:838028934598885417> **Rare Chest**!\n\n× <:cupcake:845632403405012992> **`{coins}`** found!", mention_author=False)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data['wallet'] + coins, author_id)
                await asyncio.sleep(2)
                await self.bot.pg_con.execute("UPDATE items SET rare_chests = $1 WHERE user_id = $2", ite['rare_chests'] - 1, author_id)

            if chest == "epic":
                if not ite['epic_chests']:
                    return await ctx.reply("<:redTick:596576672149667840> You don't have <:epic_chest:838028935479820319> **Epic Chests** to open.", mention_author=False)
                coins = epic_coins
                items = ["**<:pixel_flower:831186859055906847> Ami Flower**", "**<:waterbottle:831186859056562277> Water Bottle**", "**<:redrum:831182405444173855> RedRum**", "**<:8680_Weed_shinier:819689872750280775> Weed**"]
                eee = random.choice(items)

                z = ""

                if eee == "**<:pixel_flower:831186859055906847> Ami Flower**":
                    z = ite["ami_flowers"]
                    await self.bot.pg_con.execute("UPDATE items SET ami_flowers = $1 WHERE user_id = $2", z + 1, author_id)

                elif eee == "**<:waterbottle:831186859056562277> Water Bottle**":
                    z = ite["water_bottles"]
                    await self.bot.pg_con.execute("UPDATE items SET water_bottles = $1 WHERE user_id = $2", z + 1, author_id)

                elif eee == "**<:redrum:831182405444173855> RedRum**":
                    z = ite["redrums"]
                    await self.bot.pg_con.execute("UPDATE items SET redrums = $1 WHERE user_id = $2", z + 1, author_id)

                elif eee == "**<:8680_Weed_shinier:819689872750280775> Weed**":
                    z = ite["weed"]
                    await self.bot.pg_con.execute("UPDATE items SET weed = $1 WHERE user_id = $2", z + 1, author_id)


                msg = await ctx.reply("<a:chest_opening:838028934708592650> Opening a <:epic_chest:838028935479820319> **Epic Chest**.", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content="<a:chest_opening:838028934708592650> Opening a <:epic_chest:838028935479820319> **Epic Chest**..", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content="<a:chest_opening:838028934708592650> Opening a <:epic_chest:838028935479820319> **Epic Chest**...", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content=f"<a:chest_opening:838028934708592650> Opened <:epic_chest:838028935479820319> **Epic Chest**!\n\n× <:cupcake:845632403405012992> **`{coins}`** found!\n**x1** {eee}", mention_author=False)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data['wallet'] + coins, author_id)
                await asyncio.sleep(2)
                await self.bot.pg_con.execute("UPDATE items SET epic_chests = $1 WHERE user_id = $2", ite['epic_chests'] - 1, author_id)
        else:
            return await ctx.reply("This chest doesn't exist. Chests avilable are:\n\n<:common_chest:838028933920325633> **Common Chest** (`ami openchest common`)\n<:rare_chest:838028934598885417> **Rare Chest** (`ami openchest rare`)\n<:epic_chest:838028935479820319> **Epic Chest** (`ami openchest epic`)", mention_author=False)

    @commands.command()
    @is_team()
    async def givc(self,ctx,member:discord.Member,amount=None):
        member_id = str(member.id)
        author_id = str(ctx.author.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)
        amount=int(amount)

        if member == None:
            member = ctx.author

        if amount == None:
            em = discord.Embed(description="Specify an amount!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", member_id)
        await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", user["bank"] +1*amount, member_id)
        await ctx.send(f"Added <:cupcake:845632403405012992> {amount} at {member} balance!")


    @commands.command()
    @is_team()
    async def remc(self,ctx,member:discord.Member,amount=None):
        member_id = str(member.id)
        author_id = str(ctx.author.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)
        amount=int(amount)

        if member == None:
            member = ctx.author

        if amount == None:
            em = discord.Embed(description="Specify an amount!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", member_id)
        await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", user["bank"] -1*amount, member_id)
        await ctx.send(f"Removed <:cupcake:845632403405012992> {amount} at {member} balance!")


def setup(bot):
    bot.add_cog(Eco(bot))

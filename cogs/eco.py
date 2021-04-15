import discord
from discord.ext import commands
import datetime
import asyncio
import random
from PIL import Image,ImageDraw, ImageFont

from discord.member import Member
from wonderwords import RandomWord
import humanize

class Eco(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Eco Loaded")

    # Economy system commands
    @commands.command(help="See/Open your/a balance")
    async def bal(self, ctx, member: discord.User = None):
        author_id = str(ctx.author.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        if not user:
            await self.bot.pg_con.execute("INSERT INTO users (user_id, wallet, bank) VALUES ($1, 100, 100)", author_id)
            em = discord.Embed(description="Ayo, i've open a balance for you: have fun!", color = 0xffcff1)
            await ctx.send(embed=em)
            return

        member = member or ctx.author

        if member:
            member_id = str(member.id)
            user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", member_id)

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

            z = f"You actually have <:money:819700505147342900> **`{user[0]['wallet']} coins`** in the **pocket** and <:money:819700505147342900> **`{user[0]['bank']} coins`** in the **bank**. You've got <:stats:819702267850260480> **`{invest} investments`** with a profit and you've earned <:money:819700505147342900> **`{earned} coins`** from when you opened your balance. {phrase}"
            user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", member_id)
            em=discord.Embed(color=0xffcff1)
            em.add_field(name="<a:9123_red_circle:819689872821583960> Balance", value =f"{z}", inline = False)
            em.set_author(name=f"{member.name}", icon_url=f"{member.avatar_url}")
            em.set_thumbnail(url=member.avatar_url)
            em.set_footer(text="Ami S.R.L Bank ®", icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=em)



    @commands.command(help="Swing your pickaxe and mine coins")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def mine(self, ctx):
        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        users = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        if not users:
            await self.bot.pg_con.execute("INSERT INTO users (user_id, wallet, bank) VALUES ($1, 100, 100)", author_id)
            em = discord.Embed(description="Seems you're trying to mine without a balance.. i've opened one for you, now you can earn and store coins", color = 0xffcff1)
            await ctx.send(embed=em)

        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        user1 = await self.bot.pg_con.fetchrow("SELECT * FROM levels WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)
        await self.bot.pg_con.execute("UPDATE users SET wallet = 1 WHERE user_id = $1", author_id)

        earnings=random.randrange(400, 1000)
        pickaxe=random.randrange(1, 100)

        pet = user["pet_name"]
        level = user1["level"]
        earning = 0
        earning1 = 0
        perc = ""
        perclvl = ""
        s = (0/100)*earnings

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

            if level < 10:
                perclvl = "0%"
                s = (0/100)*earnings
                earning1 = earnings + s
            elif level >= 10 and level <= 20:
                perclvl = "5%"
                s = (5/100)*earnings
                earning1 = earnings + s
            elif level >= 20 and level <= 50:
                perclvl = "10%"
                s = (10/100)*earnings
                earning1 = earnings + s
            elif level >= 50 and level <= 100:
                perclvl = "15%"
                s = (15/100)*earnings
                earning1 = earnings + s
            elif level >= 100 and level <= 150:
                perclvl = "20%"
                s = (20/100)*earnings
                earning1 = earnings + s
            elif level >= 150 and level <= 300:
                perclvl = "30%"
                s = (30/100)*earnings
                earning1 = earnings + s
            elif level > 300:
                perclvl = "50%"
                s = (50/100)*earnings
                earning1 = earnings + s
    

            pett = users[0]["pet_tag"]
            if pett == None:
                pett = pet
            em = discord.Embed(description=f"⛏️ You used the **{pickaxe}%** of your pickaxe power, and earned **{earnings}** coins!\n<:maeHeart:820992680808939520> Thanks to **`{pett}`**, you've got **{perc}** of coins (**`{round(e)} coins`**)!\n<a:thankyou:820999194907115541> You are **`Lvl. {level}`**, so you got **+{perclvl}** of mined coins (**`{round(s)} coins`**)", color = 0xffcff1)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)

            await self.bot.pg_con.execute("UPDATE users SET wallet = wallet + $1, total_earn = total_earn + $1 WHERE user_id = $2", 1*earning, author_id)

        else:
            if level < 10:
                perclvl = "0%"
                s = (0/100)*earnings
                earning1 = earnings + s
            elif level >= 10 and level <= 20:
                perclvl = "5%"
                s = (5/100)*earnings
                earning1 = earnings + s
            elif level >= 20 and level <= 50:
                perclvl = "10%"
                s = (10/100)*earnings
                earning1 = earnings + s
            elif level >= 50 and level <= 100:
                perclvl = "15%"
                s = (15/100)*earnings
                earning1 = earnings + s
            elif level >= 100 and level <= 150:
                perclvl = "20%"
                s = (20/100)*earnings
                earning1 = earnings + s
            elif level >= 150 and level <= 300:
                perclvl = "30%"
                s = (30/100)*earnings
                earning1 = earnings + s
            elif level > 300:
                perclvl = "50%"
                s = (50/100)*earnings
                earning1 = earnings + s
            em = discord.Embed(description=f"⛏️ You used the **{pickaxe}%** of your pickaxe power, and earned **{earnings}** coins!\n(Seems you didn't have a pet.. why not? Check it in `ami petshop`!)\n<a:thankyou:820999194907115541> You are **`Lvl. {level}`**, so you got **+{perclvl}** of the coins (**`{round(s)} coins`**)", color = 0xffcff1)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)

            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user["wallet"] + 1*earnings + 1*earning1, author_id)  
            await self.bot.pg_con.execute("UPDATE users SET total_earn = $1 WHERE user_id = $2", user["total_earn"] + 1*earnings + 1*earning1, author_id)  

    @commands.command(help="Invest coins to earn more coins!")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def invest(self, ctx, amount):
        if amount == None:
            self.bot.get_command("invest").reset_cooldown(ctx)
            return await ctx.send("Argument `<amount>` required. Example: `ami trade 100`")

        author_id = str(ctx.author.id)
        data = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        wallet = str(data[0]["wallet"])

        if not data:
            self.bot.get_command("invest").reset_cooldown(ctx)
            return await ctx.send("Seems you don't have a balance: open one with `ami bal` to can trade coins.")

        if amount == "all":
            amount = wallet

        if amount > wallet:
            self.bot.get_command("invest").reset_cooldown(ctx)
            return await ctx.send("You don't have so much coins in your pocket.")

        if amount < str(0):
            self.bot.get_command("invest").reset_cooldown(ctx)
            return await ctx.send("You can't trade negative imports. (0, -1)")

        s = RandomWord()
        answer = s.word()
        earn = random.randint(int(amount), int(amount)*2)
        profit = int(earn) - int(amount)
        both = ["yes", "no"]
        pon = random.choice(both)

        if pon == "yes":
            em = discord.Embed(description=f"<a:ayamecloser:820999193199509554> You've invested **`{amount}`** coins in **`{answer}`** and earned **`{earn}`** coins, with a profit of **`{profit}`** coins! You can invest again in **`1 hour`**!", color = 0xffcff1)
            em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=em)
            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data[0]["wallet"] - int(amount), author_id)
            await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", data[0]["bank"] + int(earn), author_id)
            await self.bot.pg_con.execute("UPDATE users SET total_earn = $1 WHERE user_id = $2", data[0]["total_earn"] + int(earn), author_id)
            await self.bot.pg_con.execute("UPDATE users SET investments = $1 WHERE user_id = $2", data[0]["investments"] + 1, author_id)

        elif pon == "no":
            em = discord.Embed(description=f"<a:ayamecloser:820999193199509554> You've invested **`{amount}`** coins in **`{answer}`** but your investment was a total mistake and u lost all. You can invest again in **`1 hour`**!", color = 0xffcff1)
            em.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            await ctx.send(embed=em)
            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data[0]["wallet"] - int(amount), author_id)


    @commands.command(help="Get your daily reward")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        author_id = str(ctx.author.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        if not user:
            await self.bot.pg_con.execute("INSERT INTO users (user_id, wallet, bank) VALUES ($1, 100, 100)", author_id)
            em = discord.Embed(description="Ayo, i've open a balance for you: now you can redeem your daily gift and go to mine!", color = 0xffcff1)
            await ctx.send(embed=em)
            self.bot.get_command("daily").reset_cooldown(ctx)
            return

        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)

        earnings=random.randrange(1500, 20000)
        await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user["wallet"] + earnings, author_id)
        await self.bot.pg_con.execute("UPDATE users SET total_earn = $1 WHERE user_id = $2", user["total_earn"] + earnings, author_id)

        await ctx.send(f"<a:Coin:819701071630958602>{ctx.author.mention}, you've earned **{earnings}** coins from the daily gift!\n<:statisticicon8546:819702267850260480> I added them to your balance, you can redeem your next gift in **24h!**")



    @commands.command(help="Withdraw coins from your bank", aliases = ["wd"])
    async def withdraw(self, ctx, amount=None):
        author_id = str(ctx.author.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        if not user:
            await self.bot.pg_con.execute("INSERT INTO users (user_id, wallet, bank) VALUES ($1, 100, 100)", author_id)
            em = discord.Embed(description="Seems you haven't open a balance.. no problem, i've opened one for you, have fun!", color = 0xffcff1)
            await ctx.send(embed=em)

        if amount == None:
            em = discord.Embed(description="Specify an amount!", color = 0xffcff1)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        bal=user["bank"]

        if amount == "all":
            amount=user["bank"]

        amount=int(amount)
        if amount > user["bank"]:
                em = discord.Embed(description="You don't have enough coins!", color = 0xffcff1)
                em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                await ctx.send(embed=em)
                return
        if amount < 0:
            em = discord.Embed(description="You can't preleve negative imports (0, -1 ecc)", color = 0xffcff1)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", user["bank"] -1*amount, author_id)
        await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user["wallet"] + amount, author_id)

        em = discord.Embed(description=f"You have **withdrawn** `{amount}` coins!", color = 0xffcff1)
        em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
        await ctx.send(embed=em)


    @commands.command(help="Deposit coins in your bank", aliases = ["dep"])
    async def deposit(self, ctx, amount=None):
        author_id = str(ctx.author.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        if not user:
            await self.bot.pg_con.execute("INSERT INTO users (user_id, wallet, bank) VALUES ($1, 100, 100)", author_id)
            em = discord.Embed(description="You didn't open a balance, so i'll opened one new for you, have fun!", color = 0xffcff1)
            await ctx.send(embed=em)

        if amount == None:
            em = discord.Embed(description="Specify an amount!", color = 0xffcff1)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        bal=user["wallet"]

        if amount == "all":
            amount=bal

        amount=int(amount)
        if amount > bal:
                em = discord.Embed(description="You don't have enough coins!", color = 0xffcff1)
                em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                await ctx.send(embed=em)
                return
        if amount < 0:
            em = discord.Embed(description="You can't deposit negative imports (0, -1 ecc)", color = 0xffcff1)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user["wallet"] - 1*amount, author_id)
        await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", user["bank"] + amount, author_id)

        em = discord.Embed(description=f"You have **deposited** `{amount}` coins!", color = 0xffcff1)
        em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
        await ctx.send(embed=em)


    @commands.command(help="Send coins to a member")
    async def send(self, ctx, member: discord.Member, amount=None):
        author_id = str(ctx.author.id)
        member_id = str(member.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        if not user:
            await self.bot.pg_con.execute("INSERT INTO users (user_id, wallet, bank) VALUES ($1, 100, 100)", member_id)
            em = discord.Embed(description="From now you have a balance! Start to earn some coins with mining!", color = 0xffcff1)
            await ctx.send(embed=em)

        if amount == None:
            em = discord.Embed(description="Specify an amount!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        user1 = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", member_id)
        if not user1:
            return await ctx.send(f"{ctx.author.mention}, this member doesn't have a balance, so you can't send money at him.")
            
        bal=user["bank"]

        if amount == "all":
            amount=bal

        amount=int(amount)
        if amount > bal:
                em = discord.Embed(description="You don't have enough coins!", color = 0xffcff1)
                em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                await ctx.send(embed=em)
                return
        if amount < 0:
            em = discord.Embed(description="You can't deposit negative imports (0, -1 ecc)", color = 0xffcff1)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        if member == ctx.author:
            em = discord.Embed(description="You can't send money at yourself.", color = 0xffcff1)
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", user["bank"] -1*amount, author_id)


        em = discord.Embed(description=f"You've sent `{amount}` coins at {member.name}!", color = 0xffcff1)
        em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
        await ctx.send(embed=em)
        await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user1["wallet"] + amount, member_id)


    @commands.command(help="Rob coins to a member")
    @commands.cooldown(1, 14400, commands.BucketType.user)
    async def rob(self, ctx, member: discord.Member):
        author_id = str(ctx.author.id)
        member_id = str(member.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", member_id)

        if not user:
            await self.bot.pg_con.execute("INSERT INTO users (user_id, wallet, bank) VALUES ($1, 100, 100)", member_id)
            em = discord.Embed(description="OK, you're trying to rob someone, but where you store the coins?.. I've opened a balance for you, use it.", color = 0xffcff1)
            await ctx.send(embed=em)

        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", member_id)
        bal=user["wallet"]


        if bal < 100:
                em = discord.Embed(description=f"No profit, {member.name} is really poor.")
                em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                await ctx.send(embed=em)
                return

        if member == ctx.author:
            await ctx.send("You can't rob at yourself.")
            return

        earnings=random.randrange(0, int(bal))

        await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user["wallet"] - earnings, member_id)
        await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", user["wallet"] + earnings, author_id)

        em = discord.Embed(description=f"You've robbed {earnings} coins at {member.name}!")
        em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
        await ctx.send(embed=em)

        await self.bot.pg_con.execute("UPDATE users SET total_earn = $1 WHERE user_id = $2", user["total_earn"] + earnings, author_id)


    @commands.command(help="See the global leaderboard (Coins,Level & XP)", aliases = ["lb"])
    async def leaderboard(self,ctx,limit:int=10):
        if limit > 10:
            return await ctx.send("I can't fetch over 10 people.")

        user = await self.bot.pg_con.fetch("SELECT user_id, sum(wallet+bank) AS total, RANK() OVER (ORDER BY sum(bank+wallet) DESC) FROM users GROUP BY user_id LIMIT $1", limit)
        top = []
        for i in user:
            users = await self.bot.fetch_user(i["user_id"])
            userst = i["total"]
            top.append("{}) {} - {}".format(i['rank'], str(users.name), humanize.intword(str(userst))))

        final = "\n".join(top)
        em = discord.Embed(color = discord.Color(0xfa43ee))
        em.add_field(name=f"<a:Coin:819701071630958602> HERE IT IS THE LEADERBOARD (TOP {limit})!", value=f"```py\n{final}\n```")
        em.set_footer(text="Global Leaderboard.", icon_url=self.bot.user.avatar_url)
        em.timestamp = datetime.datetime.utcnow()
        em.set_author(name=f"{ctx.author.name} - {ctx.author.guild}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed = em)
        return

    @commands.command(help="Change the name of your pet!")
    async def petname(self, ctx, *, petname):
        author_id = str(ctx.author.id)

        if len(petname) > 10:
            return await ctx.send("Your pet name can't be over 10 letters.")

        if petname == None:
            return await ctx.send("Pet name not provided. Usage: `ami petname <newpetname>`")

        author_id = str(ctx.author.id)
        pet = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)
        petn = pet[0]["pet_name"]
        if not petn:
            return await ctx.send("You don't have a pet, buy one before try to set a name to it.")

        await self.bot.pg_con.execute("UPDATE users SET pet_tag = $1 WHERE user_id = $2", petname, author_id)
        await ctx.send(f"Perfect! Your pet (**`{petn}`**) from now have the name **{petname}**")

    @commands.command(help="Check your current pet and what boost gave to you!")
    async def mypet(self, ctx):
        author_id = str(ctx.author.id)
        pet = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)
        petn = pet[0]["pet_name"]
        pett = pet[0]["pet_tag"]
        
        if petn == None:
            return await ctx.send("You don't have a pet, check what pets are aviable in `ami petshop`!")
        
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
        await ctx.send(f"{ctx.author.mention}, here it is your __pet__ info:\n**{petn}** (`{pett}`)\nThis pet will make you gain **+{perc}** coins from `ami mine`!")

    @commands.command(help="Check what pet's can you buy!")
    async def petshop(self, ctx):
        em = discord.Embed(title="<:status_streaming:596576747294818305> Pet Shop", description="**<:status_idle:596576773488115722> Artic Husky** : `3000 Coins - +5% Mining`\n**<:status_idle:596576773488115722> White Ocelot** : `20000 Coins - +20% Mining`\n**<:status_idle:596576773488115722> Baby Dragon** : `35000 Coins - +25% Mining`\n**<:status_idle:596576773488115722> Black Rabbit** : `50000 Coins - +30% Mining`\n**<:status_idle:596576773488115722> Ice Golem** : `75000 Coins - +50% Mining`\n**<:status_idle:596576773488115722> Super Roo** : `125000 Coins - +55% Mining`\n**<:status_idle:596576773488115722> Silver Cat** : `150000 Coins - +60% Mining`\n**<:status_idle:596576773488115722> Iron Turtle** : `200000 Coins - +65% Mining`\n**<:status_idle:596576773488115722> Primordial Butterfly** : `300000 Coins - +70% Mining`\n**<:status_idle:596576773488115722> Mystic Pig** : `350000 Coins - +75% Mining`\n**<:status_idle:596576773488115722> Gold Crocodile** : `400000 Coins - +80% Mining`\n\n<:status_streaming:596576747294818305> Buy one of this with `ami buypet <petname>`!", color = 0xffcff1)
        em.set_footer(text='You can change your pet name with "ami petname <petname>"')
        await ctx.send(embed=em)

    @commands.command(help="Buy a pet (must be inside 'ami petshop')")
    async def buypet(self, ctx, *, petname):
        author_id = str(ctx.author.id)
        n = str(petname)
        pet = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        if petname == None:
            return await ctx.send("Missing the name of the pet you want to buy, check in `ami petshop`.")

        if pet == None:
            return await ctx.send("I didn't found you in my database: try to send `ami bal` and see if you have a balance.")

        pets = ["Artic Husky", "White Ocelot", "Baby Dragon", "Black Rabbit", "Ice Golem", "Super Roo", "Silver Cat", "Iron Turtle", "Primordial Butterfly", "Mystic Pig", "Gold Crocodile"]
        if petname in pets:
            if petname == "Artic Husky":
                if pet[0]["wallet"] < 3000:
                    return await ctx.send("You don't have sufficent coins to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", n, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 3000, author_id)
                await ctx.send(f"Congratulations! You've bought **{petname}**!")

            if petname == "White Ocelot":
                if pet[0]["wallet"] < 20000:
                    return await ctx.send("You don't have sufficent coins to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", n, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 20000, author_id)
                await ctx.send(f"Congratulations! You've bought **{petname}**!")
            
            if petname == "Baby Dragon":
                if pet[0]["wallet"] < 35000:
                    return await ctx.send("You don't have sufficent coins to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 35000, author_id)
                await ctx.send(f"Congratulations! You've bought **{petname}**!")
            
            if petname == "Black Rabbit":
                if pet[0]["wallet"] < 50000:
                    return await ctx.send("You don't have sufficent coins to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 50000, author_id)
                await ctx.send(f"Congratulations! You've bought **{petname}**!")
            
            if petname == "Ice Golem":
                if pet[0]["wallet"] < 75000:
                    return await ctx.send("You don't have sufficent coins to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 75000, author_id)
                await ctx.send(f"Congratulations! You've bought **{petname}**!")

            if petname == "Super Roo":
                if pet[0]["wallet"] < 125000:
                    return await ctx.send("You don't have sufficent coins to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 125000, author_id)
                await ctx.send(f"Congratulations! You've bought **{petname}**!")

            if petname == "Silver Cat":
                if pet[0]["wallet"] < 150000:
                    return await ctx.send("You don't have sufficent coins to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 150000, author_id)
                await ctx.send(f"Congratulations! You've bought **{petname}**!")

            if petname == "Iron Turtle":
                if pet[0]["wallet"] < 200000:
                    return await ctx.send("You don't have sufficent coins to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 200000, author_id)
                await ctx.send(f"Congratulations! You've bought **{petname}**!")

            if petname == "Primordial Butterfly":
                if pet[0]["wallet"] < 300000:
                    return await ctx.send("You don't have sufficent coins to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 300000, author_id)
                await ctx.send(f"Congratulations! You've bought **{petname}**!")

            if petname == "Mystic Pig":
                if pet[0]["wallet"] < 350000:
                    return await ctx.send("You don't have sufficent coins to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 350000, author_id)
                await ctx.send(f"Congratulations! You've bought **{petname}**!")

            if petname == "Gold Crocodile":
                if pet[0]["wallet"] < 400000:
                    return await ctx.send("You don't have sufficent coins to buy this pet.")

                await self.bot.pg_con.execute("UPDATE users SET pet_name = $1 WHERE user_id = $2", petname, author_id)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", pet[0]["wallet"] - 400000, author_id)
                await ctx.send(f"Congratulations! You've bought **{petname}**!")
        else:
            return await ctx.send("The pet isn't in the shop.")

    @commands.command(help="Check how many coins ami has stored")
    async def glbc(self,ctx,x = 5):
        user = await self.bot.pg_con.fetch("SELECT * FROM users")
        gblcs = await self.bot.pg_con.fetchval("SELECT SUM(COALESCE(wallet,0) + COALESCE(bank,0)) FROM users")
        em = discord.Embed(title=f"<a:Coin:819701071630958602> Coins storage!", description = f"```py\n! Coins stored » {gblcs}\n```", color = 0xffcff1)
        em.set_footer(text=f"Global data, means the total data stored!")
        em.timestamp = datetime.datetime.utcnow()
        em.set_thumbnail(url=self.bot.user.avatar_url)
        await ctx.send(embed=em)



    @commands.command(help="See the shop, and check what you can buy with your coins")
    async def shop(self, ctx, page=None):
        if page == None:
            page = str(1)

        if page >= str(3):
            return await ctx.reply("Dude, this page doesn't exist in the shop", mention_author=False)

        if page == str(1):
            em = discord.Embed(title="Items Shop", description="Use `ami buyitem <itemname> / <itemnumber>` to buy something.\n`<itemname>` must be also with capital letters.\nYou can buy more at once, like `ami buyitem Weed 5` to buy `5g` of weed" , color = 0xffcff1)
            em.add_field(name="1) <:waterbottle:831186859056562277> Water Bottle (25000 coins)", value="Drink a water bottle can't be dangerous.. right? ^^\n`Usage` : **ami drink 1**", inline = False)
            em.add_field(name="2) <:redrum:831182405444173855> RedRum (75000 coins)", value="This rum will make you a little bit drunky ^^\n`Usage` : **ami drink 2**", inline = False)
            em.add_field(name="3) <:huntingrifle:831182405686657034> Hunting Rifle (125000 coins)", value="Buy this and go hunt!\n`Usage` : **ami hunt**", inline = False)
            em.add_field(name="4) <:8680_Weed_shinier:819689872750280775> Weed (150000 coins)", value="Smoke is bad, don't buy this weed.\n`Usage` : **ami smoke weed**", inline = False)
            em.set_footer(text="Page Index 1/2", icon_url=ctx.author.avatar_url)
            em.timestamp = datetime.datetime.utcnow()
            await ctx.reply(embed=em, mention_author=False)
        elif page == str(2):
            em = discord.Embed(title="Items Shop", description="Use `ami buyitem <itemname> / <itemnumber>` to buy something.\n`<itemname>` must be also with capital letters.\nYou can buy more at once, like `ami buyitem Weed 5` to buy `5g` of weed" , color = 0xffcff1)
            em.add_field(name="5) <:fishingpole:831182405717065729> Fishing Rod (200000 coins)", value="Fishing is the chillness.\n`Usage` : **ami fish**", inline = False)
            em.add_field(name="6) <:computer:831186859287642122> Computer (400000 coins)", value="Want to hack the bank of someone? Use this pc!\n`Usage` : **ami bankrob @member**", inline = False)
            em.add_field(name="7) <:pixel_flower:831186859055906847> Ami Flower (10000000 coins)", value="Ami favourite flower, just a trophy.\n`Usage` : **No usages for this item**", inline = False)
            em.set_footer(text="Page Index 2/2", icon_url=ctx.author.avatar_url)
            em.timestamp = datetime.datetime.utcnow()
            await ctx.reply(embed=em, mention_author=False)


    @commands.command(help="Open your personal garage, where you can store your items")
    async def buygarage(self, ctx):
        author_id = str(ctx.author.id)
        d = await self.bot.pg_con.fetchrow("SELECT user_id FROM items WHERE user_id = $1", author_id)
        if not d:
            await self.bot.pg_con.execute("INSERT INTO items (user_id, water_bottles, redrums, rifles, weed, fish_rods, computers, ami_flowers, common_chests, rare_chests, epic_chests) VALUES ($1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)", author_id)
            await ctx.reply("Your garage is now ready! You can now buy and store items from the shop.", mention_author=False)
        else:
            return await ctx.reply("You already have a garage dude, go sleep.", mention_author=False)


    @commands.command(help="Buy items from the shop")
    async def buyitem(self, ctx, item=None, amount=None):
        author_id = str(ctx.author.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM items WHERE user_id = $1", author_id)
        if not data:
            return await ctx.reply("Dude, you can't buy items if you don't buy a place where store it.. use `ami buygarage` to setup your personal garage!", mention_author=False)

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
                    return await ctx.reply(f"You can't buy this item because you don't have **`{price}`** coins in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET water_bottles = $1 WHERE user_id = $2", data['water_bottles'] + int(amount), author_id)
            elif item == 'RedRum':
                price = 75000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"You can't buy this item because you don't have **`{price}`** coins in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET redrums = $1 WHERE user_id = $2", data['redrums'] + int(amount), author_id)
            elif item == 'Hunting Rifle':
                if data['rifles'] >= 1:
                    return await ctx.reply("You already have a rifle, you can't buy another one.", mention_author=False)
                price = 125000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"You can't buy this item because you don't have **`{price}`** coins in your bank.", mention_author=False)
                amount = 1
                await self.bot.pg_con.execute("UPDATE items SET rifles = $1 WHERE user_id = $2", data['rifles'] + int(amount), author_id)
            elif item == 'Weed':
                price = 150000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"You can't buy this item because you don't have **`{price}`** coins in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET weed = $1 WHERE user_id = $2", data['weed'] + int(amount), author_id)
            elif item == 'Fishing Rod':
                if data['fish_rods'] >= 1:
                    return await ctx.reply("You already have a fishing rod, you can't buy another one.", mention_author=False)
                price = 200000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"You can't buy this item because you don't have **`{price}`** coins in your bank.", mention_author=False)
                amount = 1
                await self.bot.pg_con.execute("UPDATE items SET fish_rods = $1 WHERE user_id = $2", data['fish_rods'] + int(amount), author_id)
            elif item == 'Computer':
                price = 400000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"You can't buy this item because you don't have **`{price}`** coins in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET computers = $1 WHERE user_id = $2", data['computers'] + int(amount), author_id)
            elif item == 'Ami Flower':
                price = 10000000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"You can't buy this item because you don't have **`{price}`** coins in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET ami_flowers = $1 WHERE user_id = $2", data['ami_flowers'] + int(amount), author_id)


        elif item in items_numbers:
            if item == '1':
                item = "Water Bottle"
                price = 25000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"You can't buy this item because you don't have **`{price}`** coins in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET water_bottles = $1 WHERE user_id = $2", data['water_bottles'] + int(amount), author_id)
            elif item == '2':
                item = "RedRum"
                price = 75000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"You can't buy this item because you don't have **`{price}`** coins in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET redrums = $1 WHERE user_id = $2", data['redrums'] + int(amount), author_id)
            elif item == '3':
                item = "Hunting Rifle"
                if data['rifles'] >= 1:
                    return await ctx.reply("You already have a rifle, you can't buy another one.", mention_author=False)
                price = 125000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"You can't buy this item because you don't have **`{price}`** coins in your bank.", mention_author=False)
                amount = 1
                await self.bot.pg_con.execute("UPDATE items SET rifles = $1 WHERE user_id = $2", data['rifles'] + int(amount), author_id)
            elif item == '4':
                item = "Weed"
                price = 150000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"You can't buy this item because you don't have **`{price}`** coins in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET weed = $1 WHERE user_id = $2", data['weed'] + int(amount), author_id)
            elif item == '5':
                item = 'Fishing Rod'
                if data['fish_rods'] >= 1:
                    return await ctx.reply("You already have a fishing rod, you can't buy another one.", mention_author=False)
                price = 200000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"You can't buy this item because you don't have **`{price}`** coins in your bank.", mention_author=False)
                amount = 1
                await self.bot.pg_con.execute("UPDATE items SET fish_rods = $1 WHERE user_id = $2", data['fish_rods'] + int(amount), author_id)
            elif item == '6':
                item = "Computer"
                price = 400000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"You can't buy this item because you don't have **`{price}`** coins in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET computers = $1 WHERE user_id = $2", data['computers'] + int(amount), author_id)
            elif item == '7':
                item = "Ami Flower"
                price = 10000000*int(amount)
                if its['bank'] < price:
                    return await ctx.reply(f"You can't buy this item because you don't have **`{price}`** coins in your bank.", mention_author=False)
                amount = amount
                await self.bot.pg_con.execute("UPDATE items SET ami_flowers = $1 WHERE user_id = $2", data['ami_flowers'] + int(amount), author_id)
        else:
            return await ctx.reply("I didn't found this itemname / itemnumber in the shop.", mention_author=False)

        await ctx.reply(f"🌟 Well done, you've bought `{amount}` **{item}** for **{price}** coins!", mention_author=False)
        await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", its['bank'] - price, author_id)


    @commands.command(help="Check what you have in your garage")
    async def garage(self, ctx):
        author_id = str(ctx.author.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM items WHERE user_id = $1", author_id)
        if not data:
            return await ctx.reply("You don't have a garage, and for consequent no items. Use `ami buygarage` to can use this command.", mention_author=False)

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

        em = discord.Embed(description=f"**`Items you can buy`**:\n<:waterbottle:831186859056562277> **Water Bottles** = **`{a_bottles}`**\n<:redrum:831182405444173855> **RedRums** = **`{a_redrums}`**\n<:huntingrifle:831182405686657034> **Rifle** = **`{a_rifles}`**\n<:8680_Weed_shinier:819689872750280775> **Weed** = **`{a_weed}g`**\n<:fishingpole:831182405717065729> **Fishing Rod** = **`{a_fishrods}`**\n<:computer:831186859287642122> **Computers** = **`{a_computers}`**\n<:pixel_flower:831186859055906847> **Ami Flowers** = **`{a_flowers}`**\n\n**`You can found chest fishing`**:\n<:discchest:831308791370743858> **Common Chests** = **`{a_common_chests}`**\n<:unnamed1:831309048329797662> **Rare Chests** = **`{a_rare_chests}`**\n<:unnamed:831308791836442635> **Epic Chests** = **`{a_epic_chests}`**", color = 0xffcff1)
        em.set_author(name=f"{ctx.author.name}'s' garage", icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=em, mention_author=False)


    @commands.command(help="Drink something buyed from the shop")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def drink(self, ctx, item):
        author_id = str(ctx.author.id)
        ite = await self.bot.pg_con.fetchrow("SELECT * FROM items WHERE user_id = $1", author_id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)

        if not ite:
            return await ctx.reply("Dude, you don't have a garage, and in consequent no items. Use `ami buygarage` to open your personal garage and store items bought.", mention_author=False)

        if not data:
            return await ctx.reply("You don't have a balance, open one with `ami bal` to can store coins.", mention_author=False)

        drinks = ["Water Bottle", "RedRum", "1", "2"]

        if item not in drinks:
            return await ctx.reply("To drink something, use `ami drink <item_name>` or `ami drink <shop_item_number>`. You can drink only the items with `drink` in usage.", mention_author=False)

        water = ite['water_bottles']
        rum = ite['redrums']

        if item == "1":
            item = "Water Bottle"

        if item == "2":
            item = "RedRum"

        if item == "Water Bottle":
            if not water:
                return await ctx.reply("You don't have any water bottle to drink.", mention_author=False)
            else:
                d = ['yes', 'no']
                f = random.choice(d)
                if d == "yes":
                    r = random.randint(0, 12000)
                    await ctx.reply(f"You drinked a <:waterbottle:831186859056562277> **water bottle** and you accidentally found **`{r}`** coins O.o/", mention_author=False)
                    await self.bot.pg_con.execute("UPDATE items SET water_bottles = $1 WHERE user_id = $2", ite['water_bottles'] - 1, author_id)
                    await asyncio.sleep(2)
                    await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data['wallet'] + r, author_id)
                else:
                    await ctx.reply(f"You drinked a <:waterbottle:831186859056562277> **water bottle** but this time you found **nothing**.", mention_author=False)
                    await self.bot.pg_con.execute("UPDATE items SET water_bottles = $1 WHERE user_id = $2", ite['water_bottles'] - 1, author_id)

        if item == "RedRum":
            if not rum:
                return await ctx.reply("You don't have any red rum to drink.", mention_author=False)
            else:
                d = ['yes', 'no']
                f = random.choice(d)
                if d == "yes":
                    r = random.randint(0, 12000)
                    await ctx.reply(f"You drinked a <:redrum:831182405444173855> **RedRum**, you got a little bit drunky and you accidentally found **`{r}`** coins O.o/", mention_author=False)
                    await self.bot.pg_con.execute("UPDATE items SET redrums = $1 WHERE user_id = $2", ite['redrums'] - 1, author_id)
                    await asyncio.sleep(2)
                    await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data['wallet'] + r, author_id)
                else:
                    await ctx.reply(f"You drinked a <:redrum:831182405444173855> **RedRum**, you got a little bit drunky and you get sleep.", mention_author=False)
                    await self.bot.pg_con.execute("UPDATE items SET redrums = $1 WHERE user_id = $2", ite['redrums'] - 1, author_id)

    @commands.command(help="Go hunt with your hunting rifle")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def hunt(self, ctx):
        author_id = str(ctx.author.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        ite = await self.bot.pg_con.fetchrow('SELECT * FROM items WHERE user_id = $1', author_id)

        if not ite:
            return await ctx.reply("Dude, you don't have a garage, and in consequent no items. Use `ami buygarage` to open your personal garage and store items bought.", mention_author=False)

        if not ite['rifles']:
            return await ctx.reply("You are without a rifle, you can't hunt with your hands, stupid dumbass.", mention_author=False)

        if not data:
            return await ctx.reply("You don't have a balance, open one with `ami bal` to can store coins.", mention_author=False)

        animals = ['bird', 'lion', 'penguin', 'mouse', 'tiger', 'deer', 'bear', 'nothing']
        animals2 = random.choice(animals)
        reward = 0
        if animals2 == 'nothing':
            reward = 0
            await ctx.reply("You went hunting with your <:huntingrifle:831182405686657034> **rifle** but you shoot on a tree, you didn't got any animal.", mention_author=False)
        else:
            reward = random.randint(1, 10000)
            await ctx.reply(f"You went hunting with your <:huntingrifle:831182405686657034> **hunting rifle** and you got a **{animals2}**, you got **`{reward}`** coins as a reward!", mention_author=False)
            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data['wallet'] + reward, author_id)


    @commands.command(help="Smoke the weed you've bought from the shop")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def smoke(self, ctx, item, g=None):
        author_id = str(ctx.author.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        ite = await self.bot.pg_con.fetchrow('SELECT * FROM items WHERE user_id = $1', author_id)

        can_smoke = ['weed', 'Weed']
        if item not in can_smoke:
            return await ctx.reply("I didn't found a smokable item with this name.", mention_author=False)

        if not ite:
            return await ctx.reply("Dude, you don't have a garage, and in consequent no items. Use `ami buygarage` to open your personal garage and store items bought.", mention_author=False)

        if not ite['weed']:
            return await ctx.reply("You are out of weed, you can't smoke the air, go buy weed and come back here", mention_author=False)

        if not data:
            return await ctx.reply("You don't have a balance, open one with `ami bal` to can store coins.", mention_author=False)

        if not item:
            return self.bot.get_command("smoke").reset_cooldown(ctx)

        if g == None:
            g = 1

        if int(g) > ite['weed']:
            return await ctx.reply(f"You don't have **`{g}g`** of <:8680_Weed_shinier:819689872750280775> **weed**, go buy more weed.", mention_author=False)

        status = ['good', 'normal', 'bad']
        cstatus = random.choice(status)
        
        if cstatus == "good":
            await ctx.reply(f"You smoked **`{g}g`** of <:8680_Weed_shinier:819689872750280775> **{item}**. you take it so good, and you've sent **all** your bank amount to your mom! What a good son 😍", mention_author=False)
            await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", data['bank'] - data['bank'], author_id)
            await self.bot.pg_con.execute("UPDATE items SET weed = $1 WHERE user_id = $2", ite['weed'] - int(g), author_id)
            return

        if cstatus == "normal":
            amount = random.randint(0, data['wallet'])
            await ctx.reply(f"You smoked **`{g}g`** of <:8680_Weed_shinier:819689872750280775> **{item}**. you take it normal, but you got confused and you lost **`{amount}`** coins from your wallet, maybe you dropped your portfolio somewhere..", mention_author=False)
            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data['wallet'] - amount, author_id)
            await self.bot.pg_con.execute("UPDATE items SET weed = $1 WHERE user_id = $2", ite['weed'] - int(g), author_id)
            return

        if cstatus == "bad":
            member = random.choice(ctx.message.guild.members)
            mfetch = await self.bot.fetch_user(member.id)
            amount = random.randint(0, data['bank'])
            await ctx.reply(f"You smoked **`{g}g`** of <:8680_Weed_shinier:819689872750280775> **{item}**. you take it really bad, and you killed **{mfetch.name}**, after you get sended in jail, but you've paid **{amount}** coins to be released.", mention_author=False)
            await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", data['bank'] - amount, author_id)
            await self.bot.pg_con.execute("UPDATE items SET weed = $1 WHERE user_id = $2", ite['weed'] - int(g), author_id)
            return

    @commands.command(help="Go fishing with your fishing rod")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def fish(self, ctx):
        author_id = str(ctx.author.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        ite = await self.bot.pg_con.fetchrow('SELECT * FROM items WHERE user_id = $1', author_id)

        if not ite:
            return await ctx.reply("Dude, you don't have a garage, and in consequent no items. Use `ami buygarage` to open your personal garage and store items bought.", mention_author=False)

        if not ite['fish_rods']:
            return await ctx.reply("You don't have a fucking fishing rod, get out of here and go buy one, and after come back to fish lmao.", mention_author=False)

        if not data:
            return await ctx.reply("You don't have a balance, open one with `ami bal` to can store coins.", mention_author=False)

        fishes = ['🐟', '🐠', '🐡', '🦐', '🦑', '🐙', '🦞', '🦀', '🐚', '🐋', '🐬', '🦈', '🐢', '🦠', '🥽', '🥾']
        crates = ['<:discchest:831308791370743858> Common Chest', '<:unnamed1:831309048329797662> Rare Chest', '<:unnamed:831308791836442635> Epic Chest']

        probs = ['yes', 'maybe', 'idk', 'pheraps', 'no', 'nono', 'no.', 'fuck', 'die']
        s = random.choice(probs)

        if s == "yes":
            d = random.choice(crates)

            if d == "<:discchest:831308791370743858> Common Chest":
                await ctx.reply(f"You went to fish with your <:fishingpole:831182405717065729> **Fishing Rod**, and you got __so lucky__! You found a **{d}**! You can open it with `ami openchest common`!", mention_author=False)
                await self.bot.pg_con.execute("UPDATE items SET common_chests = $1 WHERE user_id = $2", ite['common_chests'] + 1, author_id)
            
            if d == "<:unnamed1:831309048329797662> Rare Chest":
                await ctx.reply(f"You went to fish with your <:fishingpole:831182405717065729> **Fishing Rod**, and you got __fucking lucky__! You found a **{d}**! You can open it with `ami openchest rare`!", mention_author=False)
                await self.bot.pg_con.execute("UPDATE items SET rare_chests = $1 WHERE user_id = $2", ite['rare_chests'] + 1, author_id)

            if d == "<:unnamed:831308791836442635> Epic Chest":
                await ctx.reply(f"You went to fish with your <:fishingpole:831182405717065729> **Fishing Rod**, and you got __extremely lucky__! You found a **{d}**! You can open it with `ami openchest epic`!", mention_author=False)
                await self.bot.pg_con.execute("UPDATE items SET epic_chests = $1 WHERE user_id = $2", ite['epic_chests'] + 1, author_id)

        else:
            d = random.choice(fishes)
            earn = random.randint(1, 300)
            await ctx.reply(f"You went to fish with your <:fishingpole:831182405717065729> **Fishing Rod**, and you got __so **`unlucky`**__! You found a **{d}** and you sold it for **{earn}** coins O.o/", mention_author=False)
            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data['wallet'] + earn, author_id)


    @commands.command(help="Became an hacker with the computer you've bought from the shop, and hack the bank of a member")
    @commands.cooldown(1, 180, commands.BucketType.user)
    async def bankrob(self, ctx, member: discord.Member):
        author_id = str(ctx.author.id)
        member_id = str(member.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        data1 = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", member_id)
        ite = await self.bot.pg_con.fetchrow('SELECT * FROM items WHERE user_id = $1', author_id)

        if not ite:
            return await ctx.reply("Dude, you don't have a garage, and in consequent no items. Use `ami buygarage` to open your personal garage and store items bought.", mention_author=False)

        if not ite['computers']:
            return await ctx.reply("You don't have a fucking fishing rod, get out of here and go buy one, and after come back to fish lmao.", mention_author=False)

        if not data:
            return await ctx.reply("You don't have a balance, open one with `ami bal` to can store coins.", mention_author=False)
        
        if not data1:
            return await ctx.reply("This member doesn't have a balance opened.", mention_author=False)

        if data1['bank'] < 100000:
            self.bot.get_command("bankrob").reset_cooldown(ctx)
            return await ctx.reply("This member have less than **100k** coins in the bank: member with **100k or <** in the bank have the **`hack-protection`**.", mention_author=False)

        chs = ['yes', 'no']
        if chs == "yes":
            hacked = random.randint(0, data1['bank'])
            nudes = random.randint(1, 100)
            await ctx.reply(f"You became a __professional__ hacker with your <:computer:831186859287642122> **Computer**, and in the meanwhile you've **found & got**:\n\n⁕ `{nudes}` **{member.name}** nudes 😏\n⁕ `{hacked} coins` hacked from the **{member.name}** bank 😎")
            await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", data['bank'] + hacked, author_id)
            await asyncio.sleep(2)
            await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", data['bank'] - hacked, member_id)
            await asyncio.sleep(2)
            await self.bot.pg_con.execute("UPDATE items SET computers = $1 WHERE user_id = $2", ite['computers'] - 1, author_id)
        else:
            hacked = random.randint(0, data1['bank'])
            losed = random.randint(0, data['bank'])
            await ctx.reply(f"You became a __professional__ hacker with your <:computer:831186859287642122> **Computer**, and **you've got**:\n\n**{hacked*1000} coins** 🤩🤩🤩\n\n**`Joking`**, you failed to hack the member bank, and you got **arrested**, losing **{losed}** coins.")
            await self.bot.pg_con.execute("UPDATE users SET bank = $1 WHERE user_id = $2", data['bank'] - losed, author_id)
            await asyncio.sleep(2)
            await self.bot.pg_con.execute("UPDATE items SET computers = $1 WHERE user_id = $2", ite['computers'] - 1, author_id)


    @commands.command(help="Open the chests you've found fishing with your fishing rod")
    async def openchest(self, ctx, chest):
        author_id = str(ctx.author.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE user_id = $1", author_id)
        ite = await self.bot.pg_con.fetchrow('SELECT * FROM items WHERE user_id = $1', author_id)

        if not ite:
            return await ctx.reply("Dude, you don't have a garage, and in consequent no items. Use `ami buygarage` to open your personal garage and store items bought.", mention_author=False)

        if not data:
            return await ctx.reply("You don't have a balance, open one with `ami bal` to can store coins.", mention_author=False)

        chests = ['common', 'rare', 'epic']
        common_coins = random.randint(10000, 200000)
        rare_coins = random.randint(35000, 350000)
        epic_coins = random.randint(65000, 1000000)

        coins = 0
        if chest in chests:
            if chest == "common":
                if not ite['common_chests']:
                    return await ctx.reply("You don't have <:discchest:831308791370743858> **Common Chests** to open.", mention_author=False)
                coins = common_coins
                msg = await ctx.reply("<a:chest_opening:831640530256396348> Opening a <:discchest:831308791370743858> **Common Chest**.", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content="<a:chest_opening:831640530256396348> Opening a <:discchest:831308791370743858> **Common Chest**..", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content="<a:chest_opening:831640530256396348> Opening a <:discchest:831308791370743858> **Common Chest**...", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content=f"<a:chest_opening:831640530256396348> Opened <:discchest:831308791370743858> **Common Chest**!\n\n× **`{coins} coins`** founded!", mention_author=False)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data['wallet'] + coins, author_id)
                await asyncio.sleep(2)
                await self.bot.pg_con.execute("UPDATE items SET common_chests = $1 WHERE user_id = $2", ite['common_chests'] - 1, author_id)
            
            if chest == "rare":
                if not ite['rare_chests']:
                    return await ctx.reply("You don't have <:unnamed1:831309048329797662> **Rare Chests** to open.", mention_author=False)
                coins = rare_coins
                msg = await ctx.reply("<a:chest_opening:831640530256396348> Opening a <:unnamed1:831309048329797662> **Rare Chest**.", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content="<a:chest_opening:831640530256396348> Opening a <:unnamed1:831309048329797662> **Rare Chest**..", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content="<a:chest_opening:831640530256396348> Opening a <:unnamed1:831309048329797662> **Rare Chest**...", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content=f"<a:chest_opening:831640530256396348> Opened <:unnamed1:831309048329797662> **Rare Chest**!\n\n× **`{coins} coins`** founded!", mention_author=False)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data['wallet'] + coins, author_id)
                await asyncio.sleep(2)
                await self.bot.pg_con.execute("UPDATE items SET rare_chests = $1 WHERE user_id = $2", ite['rare_chests'] - 1, author_id)

            if chest == "epic":
                if not ite['epic_chests']:
                    return await ctx.reply("You don't have <:unnamed:831308791836442635> **Epic Chests** to open.", mention_author=False)
                coins = epic_coins
                msg = await ctx.reply("<a:chest_opening:831640530256396348> Opening a <:unnamed:831308791836442635> **Epic Chest**.", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content="<a:chest_opening:831640530256396348> Opening a <:unnamed:831308791836442635> **Epic Chest**..", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content="<a:chest_opening:831640530256396348> Opening a <:unnamed:831308791836442635> **Epic Chest**...", mention_author=False)
                await asyncio.sleep(1)
                await msg.edit(content=f"<a:chest_opening:831640530256396348> Opened <:unnamed:831308791836442635> **Epic Chest**!\n\n× **`{coins} coins`** founded!", mention_author=False)
                await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", data['wallet'] + coins, author_id)
                await asyncio.sleep(2)
                await self.bot.pg_con.execute("UPDATE items SET epic_chests = $1 WHERE user_id = $2", ite['epic_chests'] - 1, author_id)
        else:
            return await ctx.reply("This chest doesn't exist. Chests avilable are:\n\n<:discchest:831308791370743858> **Common Chest** (`ami openchest common`)\n<:unnamed1:831309048329797662> **Rare Chest** (`ami openchest rare`)\n<:unnamed:831308791836442635> **Epic Chest** (`ami openchest epic`)", mention_author=False)

    @commands.command()
    @commands.is_owner()
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
        await ctx.send(f"Added {amount} coins at {member} balance!")


    @commands.command()
    @commands.is_owner()
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
        await ctx.send(f"Removed {amount} coins at {member} balance!")


    @commands.command()
    @commands.is_owner()
    async def givxp(self,ctx,member:discord.Member,amount=None):
        member_id = str(member.id)
        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM levels WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)
        amount=int(amount)

        if member == None:
            member = ctx.author

        if amount == None:
            em = discord.Embed(description="Specify an amount!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        user = await self.bot.pg_con.fetchrow("SELECT * FROM levels WHERE user_id = $1 AND guild_id = $2", member_id, guild_id)
        await self.bot.pg_con.execute("UPDATE levels SET xp = $1 WHERE user_id = $2 AND guild_id = $3", user["xp"] + amount, member_id, guild_id)
        await ctx.send(f"Added {amount} XP at {member}!")


    @commands.command()
    @commands.is_owner()
    async def remxp(self,ctx,member:discord.Member,amount=None):
        member_id = str(member.id)
        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM levels WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)
        amount=int(amount)

        if member == None:
            member = ctx.author

        if amount == None:
            em = discord.Embed(description="Specify an amount!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        user = await self.bot.pg_con.fetchrow("SELECT * FROM levels WHERE user_id = $1 AND guild_id = $2", member_id, guild_id)
        await self.bot.pg_con.execute("UPDATE levels SET xp = $1 WHERE user_id = $2 AND guild_id = $3", user["xp"] - amount, member_id, guild_id)
        await ctx.send(f"Removed {amount} XP at {member}!")

    @commands.command()
    @commands.is_owner()
    async def givlvl(self,ctx,member:discord.Member,amount=None):
        member_id = str(member.id)
        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM levels WHERE user_id = $1 AND guild_id = $3", author_id, guild_id)
        amount=int(amount)

        if member == None:
            member = ctx.author

        if amount == None:
            em = discord.Embed(description="Specify an amount!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        user = await self.bot.pg_con.fetchrow("SELECT * FROM levels WHERE user_id = $1 AND guild_id = $2", member_id, guild_id)
        await self.bot.pg_con.execute("UPDATE levels SET level = $1 WHERE user_id = $2 AND guild_id = $3", user["level"] + amount, member_id, guild_id)
        await ctx.send(f"Added {amount} levels at {member}!")


    @commands.command()
    @commands.is_owner()
    async def remlvl(self,ctx,member:discord.Member,amount=None):
        member_id = str(member.id)
        author_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        user = await self.bot.pg_con.fetch("SELECT * FROM levels WHERE user_id = $1 AND guild_id = $2", author_id, guild_id)
        amount=int(amount)

        if member == None:
            member = ctx.author

        if amount == None:
            em = discord.Embed(description="Specify an amount!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await ctx.send(embed=em)
            return

        user = await self.bot.pg_con.fetchrow("SELECT * FROM levels WHERE user_id = $1 AND guild_id = $2", member_id, guild_id)
        await self.bot.pg_con.execute("UPDATE levels SET level = $1 WHERE user_id = $2 AND guild_id = $3", user["level"] - amount, member_id, guild_id)
        await ctx.send(f"Removed {amount} levels at {member}!")


def setup(bot):
    bot.add_cog(Eco(bot))

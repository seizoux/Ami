import discord
from discord.ext import commands, tasks
import datetime
import random
import asyncio
import humanize

class Mineral:
    def emoji(mineral:str):
        emo = {
            "bronze": "<:bronze:867815549144530944>",
            "silver": "<:silver:867815548950413313>",
            "gold": "<:gold:867815549042819113>",
            "diamond": "<:diamond:867815548862332969>"
        }

        return emo[mineral]

    def name(mineral:str):
        name = {
            "bronze": "Bronze",
            "silver": "Silver",
            "gold": "Gold",
            "diamond": "Diamond"
        }

        return name[mineral]

    def amount(mineral_name:str):
        rates = {
            "bronze": random.randint(1, 100),
            "silver": random.randint(1, 50),
            "gold": random.randint(1, 20),
            "diamond": random.randint(1, 5)
        }

        return rates[mineral_name]

    def luck_cupcake():
        r = random.randint(1, 100)
        return r in range(1, 10)

class Pickaxe:
    def calculate_charge(pick_type:str):
        pickaxes_recharges = {
            "wood": 1,
            "golden": 2,
            "ephemeral": 5,
            "candy": 10,
            "sky": 20,
            "nebula": 50,
            "divine": 100
        }

        return pickaxes_recharges[pick_type]

    def use(pick_type:str):
        """
        Durability usage based on
        each pickaxe.
        """
        pickaxes_rates_durability = {
            "wood": random.choice(range(1, 10)),
            "golden": random.choice(range(1, 8)),
            "ephemeral": random.choice(range(1, 6)),
            "candy": random.choice(range(1, 4)),
            "sky": random.choice(range(1, 3)),
            "nebula": random.choice(range(1, 2)),
            "divine": 1
        }

        return pickaxes_rates_durability[pick_type]

    def add_xp(pick_type:str):
        """
        Adding xp on each mine
        command invoked based on
        the pickaxe of the user.
        """
        pickaxes_rates_xp = {
            "wood": random.randint(1, 23),
            "golden": random.randint(1, 20),
            "ephemeral": random.randint(1, 18),
            "candy": random.randint(1, 15),
            "sky": random.randint(1, 14),
            "nebula": random.randint(1, 12),
            "divine": random.randint(1, 10)
        }

        exp = pickaxes_rates_xp[pick_type]
        return exp

    def check_durability(dur:int):
        """
        Checking if the pickaxe durability isn't 0.
        """
        return dur != 0

    def upgrade_pick(pick_type:str):
        """
        Simple function to get the upgraded
        pickaxe with the actual one. Everything
        is managed after in the command.
        """
        pickaxes_upgrade = {
            "wood": "golden",
            "golden": "ephemeral",
            "ephemeral": "candy",
            "candy": "sky",
            "sky": "nebula",
            "nebula": "divine"
        }

        if pick_type not in pickaxes_upgrade:
            return "Your pickaxe is already upgraded to its maximum!"

        return pickaxes_upgrade[pick_type]

    def check_xp(pick_xp:int, pick_needed_xp:int):
        """
        XP Pickaxe checker for upgrade.
        """
        return pick_xp >= pick_needed_xp

    def emoji(pick_type:str):
        """
        Pickaxe emojis.
        """
        pickaxes_emoji = {
            "wood": "<:wood_pickaxe:862694657845755924>",
            "golden": "<:golden_pickaxe:862694657833304094>",
            "ephemeral": "<:ephemeral_pickaxe:862694657820721182>",
            "candy": "<:candy_pickaxe:862694657916928030>",
            "sky": "<:sky_pickaxe:862694658055340032>",
            "nebula": "<:nebula_pickaxe:862694657959395348>",
            "divine": "<:divine_pickaxe:862694657891631114>"
        }

        return pickaxes_emoji[pick_type]

    def name(pick_type:str):
        """
        Pickaxe readable names.
        """
        pickaxes_names = {
            "wood": "Wooden Pickaxe",
            "golden": "Golden Pickaxe",
            "ephemeral": "Ephemeral Pickaxe",
            "candy": "Candy Pickaxe",
            "sky": "Sky Pickaxe",
            "nebula": "Nebula Pickaxe",
            "divine": "Divine Pickaxe"
        }

        return pickaxes_names[pick_type]

    def perks(pick_type:str):
        """
        Pickaxe perks.
        """
        pickaxes_perks = {
            "wood": "<:alert_pink:867758260707000380> No Special Perks.\n<:xp:867817838941437974> `1` > `23`.\n<:durability:867818581864218654> `1` > `10`.\n<:cupcake:845632403405012992> `1`",
            "golden": "<:alert_pink:867758260707000380> +5% Gold Drop.\n<:xp:867817838941437974> `1` > `20`.\n<:durability:867818581864218654> `1` > `8`.\n<:cupcake:845632403405012992> `2`",
            "ephemeral": "<:alert_pink:867758260707000380> +10% Gold Drop.\n<:xp:867817838941437974> `1` > `18`.\n<:durability:867818581864218654> `1` > `6`.\n<:cupcake:845632403405012992> `5`",
            "candy": "<:alert_pink:867758260707000380> +20% Gold Drop.\n<:xp:867817838941437974> `1` > `15`.\n<:durability:867818581864218654> `1` > `4`.\n<:cupcake:845632403405012992> `10`",
            "sky": "<:alert_pink:867758260707000380> +5% Diamond Drop.\n<:xp:867817838941437974> `1` > `14`.\n<:durability:867818581864218654> `1` > `3`.\n<:cupcake:845632403405012992> `20`",
            "nebula": "<:alert_pink:867758260707000380> +10% Diamond Drop.\n<:xp:867817838941437974> `1` > `12`.\n<:durability:867818581864218654> `1` > `2`.\n<:cupcake:845632403405012992> `50`",
            "divine": "<:alert_pink:867758260707000380> +20% Diamond Drop.\n<:xp:867817838941437974> `1` > `10`.\n<:durability:867818581864218654> `1` > `1`.\n<:cupcake:845632403405012992> `100`"
        }

        return pickaxes_perks[pick_type]

class Lootbox:
    def can_drop(l_type:str):
        """
        What each lootbox can drop.
        """
        lootbox_can_drop = {
            "common": ["bronze"],
            "uncommon": ["bronze", "silver"],
            "rare": ["bronze", "silver", "gold"],
            "epic": ["bronze", "silver", "gold", "diamond"]
        }

        return lootbox_can_drop[l_type]
    
    def emoji(l_type:str):
        """
        Lootboxes emojis.
        """
        lootboxes = {
            "common": "<:lootbox:867758260622590002>",
            "uncommon": "<:uncommon:867764757733834793>",
            "rare": "<:rare:867764757670002698>",
            "epic": "<:epic:867764757708406824>"
        }

        return lootboxes[l_type]

    def name(l_type:str):
        """
        Lootboxes full names.
        """
        lootboxes = {
            "common": "Common Lootbox",
            "uncommon": "Uncommon Lootbox",
            "rare": "Rare Lootbox",
            "epic": "Epic Lootbox"
        }

        return lootboxes[l_type]


    def coins(l_type:str):
        """
        How many cupcakes can drop
        each lootbox.
        """
        lootboxes_drop_cupcakes = {
            "common": random.randint(10, 35),
            "uncommon": random.randint(35, 75),
            "rare": random.randint(75, 125),
            "epic": random.randint(125, 250)
        }

        return lootboxes_drop_cupcakes[l_type]

    def minerals(l_type:str):
        """
        How many minerals can drop
        each lootbox.
        """
        lootboxes_drop_minerals = {
            "common": {"bronze" : random.randint(1, 45)},
            "uncommon": {"bronze" : random.randint(1, 45), "silver" : random.randint(1, 20)},
            "rare": {"bronze" : random.randint(1, 45), "silver" : random.randint(1, 20), "gold" : random.randint(1, 10)},
            "epic": {"bronze" : random.randint(1, 45), "silver" : random.randint(1, 20), "gold" : random.randint(1, 10), "diamond" : random.randint(1, 5)}
        }

        return lootboxes_drop_minerals[l_type]

class Cuppy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cuppy Loaded")

    
    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def test_balance(self, ctx):
        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
        if not data:
            await self.bot.db.execute("INSERT INTO cuppy (user_id, balance, pickaxe_type, pickaxe_exp, pickaxe_durability, pickaxe_earnings, pickaxe_diamonds, pickaxe_golds, pickaxe_silvers, pickaxe_bronzes, pickaxe_needed_xp, bronze, silver, gold, diamond) VALUES ($1, 10, $2, 0, 100, 0, 0, 0, 0, 0, $3, 0, 0, 0, 0)", ctx.author.id, "wood", 3500)
            return await ctx.send(f"{ctx.author.mention} **your balance is now ready!**\n<:alert_pink:867758260707000380> Earn minerals mining with your pickaxe using `ami mine`!\n"
                        f"<:alert_pink:867758260707000380> Vote to get <:lootbox:867758260622590002> and (**luckly**) <:uncommon:867764757733834793> <:rare:867764757670002698> or <:epic:867764757708406824> with `ami vote`!\n"
                        f"<:alert_pink:867758260707000380> Upgrade your pickaxe to even more good ones (<:nebula_pickaxe:862694657959395348> <:sky_pickaxe:862694658055340032> <:divine_pickaxe:862694657891631114>) with `ami pickaxe upgrade`!\n"
                        f"<:alert_pink:867758260707000380> Exchange the minerals you've got for <:cupcake:845632403405012992> with `ami exchange <mineral_name> <amount>`! Check `ami minerals values` for values of minerals!\n"
                        f"<:alert_pink:867758260707000380> Create your own clan, invite friends into it and raise it to the top!")

        bal = data[0]["balance"]
        await ctx.send(f"<:cupcake:845632403405012992> **{ctx.author.name}** balance is **{humanize.intcomma(bal)} Cupcakes!**")

    @commands.group(help="Open your lootboxes <:lootbox:867758260622590002> <:uncommon:867764757733834793> <:rare:867764757670002698> <:epic:867764757708406824>", aliases=["op"], invoke_without_command=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def open(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command":"open"})

    @open.command(help="Choose what box")
    async def box(self, ctx, lootbox_rarity, flag=None):
        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
        if not data:
            return await ctx.invoke(self.test_balance)

        if flag:
            if flag != "all":
                return await ctx.send(f"<:4318crossmark:848857812565229601> {ctx.author.mention} you passed an invalid argument in `flag`. Valid flag is `all`, to open all of the choosed lootbox rarity you have.")

        valid_lbs = ["common", "uncommon", "rare", "epic"]
        if lootbox_rarity.lower() not in valid_lbs:
            return await ctx.send(f"<:4318crossmark:848857812565229601> {ctx.author.mention} this is not a valid lootbox.")

        cups = Lootbox.coins(lootbox_rarity.lower())
        mins = Lootbox.minerals(lootbox_rarity.lower())
        emoji = Lootbox.emoji(lootbox_rarity.lower())
        name = Lootbox.name(lootbox_rarity.lower())
        drops = Lootbox.can_drop(lootbox_rarity.lower())

        lb = data[0][f"lootbox_{lootbox_rarity.lower()}"]
        if lb == 0:
            return await ctx.send("<:4318crossmark:848857812565229601> You don't have any {emoji} **{name}** to open.")

        amount = 1
        if flag == "all":
            amount = lb

        final_min = {}

        for drop in drops:
            if drop in mins:
                final_min[drop] = mins[drop]

        s = []
        for k,v in final_min.items():
            await self.bot.db.execute(f"UPDATE cuppy SET {k} = $1 WHERE user_id = $2", data[0][k] + v*amount, ctx.author.id)
            m_emoji = Mineral.emoji(k)
            s.append(f"{m_emoji} {v*amount}x ")

        vcd = '\n'.join(s)
        await ctx.send(f"**{ctx.author.name}** opened a {emoji} **{name}** and found:\n{vcd}\n<:cupcake:845632403405012992> {cups}x")
        await self.bot.db.execute("UPDATE cuppy SET balance = $1 WHERE user_id = $2", data[0]["balance"] + cups, ctx.author.id)

    @commands.group(help="Check your pickaxe stats, upgrade it, and much more!", aliases=["pcx"], invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pickaxe(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command":"pickaxe"})

    @pickaxe.command()
    async def stats(self, ctx):
        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
        if not data:
            return await ctx.invoke(self.test_balance)

        pick = data[0]["pickaxe_type"]
        pick_exp = data[0]["pickaxe_exp"]
        pick_needed_xp = data[0]["pickaxe_needed_xp"]
        pick_dur = data[0]["pickaxe_durability"]
        pick_earns = data[0]["pickaxe_earnings"]
        pick_diam = data[0]["pickaxe_diamonds"]
        pick_golds = data[0]["pickaxe_golds"]
        pick_silvers = data[0]["pickaxe_silvers"]
        pick_bronzes = data[0]["pickaxe_bronzes"]

        emoji = Pickaxe.emoji(pick)
        name = Pickaxe.name(pick)

        await ctx.send(embed = discord.Embed(
                        title = f"{ctx.author.name} pickaxe's stats!",
                        description = f"__**Pickaxe Cupcakes**__\nYou've earned <:cupcake:845632403405012992> **{humanize.intcomma(pick_earns)}** since started!\n\n"
                                    f"__**Pickaxe**__\n{emoji} **{name}**\n<:durability:867818581864218654> **Durability**: {pick_dur}\n<:xp:867817838941437974> **XP**: {humanize.intcomma(pick_exp)} / {humanize.intcomma(pick_needed_xp)}\n\n"
                                    f"__**Pickaxe Stats**__\n"
                                    f"<:bronze:867815549144530944> **Bronze Earned**: {humanize.intcomma(pick_bronzes)}\n"
                                    f"<:silver:867815548950413313> **Silver Earned**: {humanize.intcomma(pick_silvers)}\n"
                                    f"<:gold:867815549042819113> **Gold Earned**: {humanize.intcomma(pick_golds)}\n"
                                    f"<:diamond:867815548862332969> **Diamonds Earned**: {humanize.intcomma(pick_diam)}",
                        color = self.bot.color
        ))

    @pickaxe.command()
    async def upgrade(self, ctx):
        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
        if not data:
            return await ctx.invoke(self.test_balance)

        pick = data[0]["pickaxe_type"]
        pick_exp = data[0]["pickaxe_exp"]
        pick_needed_xp = data[0]["pickaxe_needed_xp"]

        can_upgrade = Pickaxe.check_xp(pick_exp, pick_needed_xp)

        if can_upgrade:
            upgrade_it = Pickaxe.upgrade_pick(pick)
            if upgrade_it == "Your pickaxe is already upgraded to its maximum!":
                return await ctx.send("<:alert_pink:867758260707000380> Your pickaxe is already upgraded to its maximum!")

            await self.bot.db.execute("UPDATE cuppy SET pickaxe_type = $1, pickaxe_exp = $2, pickaxe_durability = $3, pickaxe_needed_xp = $4 WHERE user_id = $5", upgrade_it, pick_exp-pick_needed_xp, 100, pick_exp + 750, ctx.author.id)
            await asyncio.sleep(1)
            data2 = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
            pick2 = data2[0]["pickaxe_type"]
            emoji = Pickaxe.emoji(pick2)
            name = Pickaxe.name(pick2)
            await ctx.send(f"<:alert_pink:867758260707000380> Congratulasions, **{ctx.author.name}**! You pickaxe was upgraded to {emoji} **{name}!**")
        else:
            return await ctx.reply(f"<:alert_pink:867758260707000380> Your pickaxe has <:xp:867817838941437974> **{humanize.intcomma(pick_exp)} / {humanize.intcomma(pick_needed_xp)}**, you can't upgrade it now.")

    @pickaxe.command()
    async def list(self, ctx):
        types = ["wood", "golden", "ephemeral", "candy", "sky", "nebula", "divine"]


        em = discord.Embed(title="All Pickaxes List", description = "<:xp:867817838941437974> Will tell you what is the XP drop range for each pickaxe\n<:durability:867818581864218654> Will tell you what is the usage range of durability for each pickaxe\n<:cupcake:845632403405012992> Will tell you how many cupcakes are needed to recharge it", color=self.bot.color)
        for pick in types:
            name = Pickaxe.name(pick)
            emoji = Pickaxe.emoji(pick)
            perks = Pickaxe.perks(pick)
            em.add_field(name=f"{emoji} {name}", value=perks)

        await ctx.send(embed=em)

    @pickaxe.command()
    async def recharge(self, ctx):
        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
        if not data:
            return await ctx.invoke(self.test_balance)

        pick = data[0]["pickaxe_type"]
        pick_dur = data[0]["pickaxe_durability"]

        balance = data[0]["balance"]

        emoji = Pickaxe.emoji(pick)
        name = Pickaxe.name(pick)
        recharge_amount = Pickaxe.calculate_charge(pick)

        if pick_dur != 0:
            return await ctx.send(f"<:alert_pink:867758260707000380> Your {emoji} **{name}** has <:durability:867818581864218654> **{humanize.intcomma(pick_dur)} / 100**, you can recharge only at <:durability:867818581864218654> **0 / 100**.")

        if balance < recharge_amount:
            return await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.name}, recharging your {emoji} **{name}** requires <:cupcake:845632403405012992> **{recharge_amount}**, you have only <:cupcake:845632403405012992> **{balance}**.")

        await self.bot.db.execute("UPDATE cuppy SET pickaxe_durability = $1, balance = $2 WHERE user_id = $3", 100, data[0]["balance"] - recharge_amount, ctx.author.id)
        await ctx.send(f"**{ctx.author.name}**, you've spent <:cupcake:845632403405012992> **{recharge_amount}** to refill your {emoji} **{name}** durability!")

    @commands.command()
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def test_mine(self, ctx):
        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
        if not data:
            return await ctx.invoke(self.test_balance)

        pick = data[0]["pickaxe_type"]
        pick_exp = data[0]["pickaxe_exp"]
        pick_upgrade = data[0]["pickaxe_needed_xp"]
        pick_durability = data[0]["pickaxe_durability"]

        emoji = Pickaxe.emoji(pick)
        name = Pickaxe.name(pick)

        info = Pickaxe.check_durability(pick_durability)
        if info is False:
            return await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.name}, your {emoji} **{name}** durability is **0 / 100**, recharge it with `ami picaxe recharge`!")

        message = ""
        mineral = ""
        query = ""

        cc = random.randint(1, 100)
        if cc in range(1, 50):
            mineral = "bronze"
            query = "bronze"
            query2 = "bronzes"
        elif cc in range(50, 75):
            mineral = "silver"
            query = "silver"
            query2 = "silvers"
        elif cc in range(75, 95):
            mineral = "gold"
            query = "gold"
            query2 = "golds"
        elif cc in range(95, 100):
            mineral = "diamond"
            query = "diamond"
            query2 = "diamonds"

        fc = Mineral.amount(mineral)
        full_emoji = Mineral.emoji(mineral)
        full_name = Mineral.name(mineral)

        await self.bot.db.execute(f"UPDATE cuppy SET {query} = $1 WHERE user_id = $2", data[0][query] + fc, ctx.author.id)

        data2 = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)

        bronze = data2[0]["bronze"]
        silver = data2[0]["silver"]
        gold = data2[0]["gold"]
        diamond = data2[0]["diamond"]

        message = f"<:alert_pink:867758260707000380> **{ctx.author.name}** you've earned {full_emoji} **{fc}x {full_name}** thanks to your {emoji} **{name}**!\n<:alert_pink:867758260707000380> Now you have <:bronze:867815549144530944> {humanize.intcomma(bronze)}x <:silver:867815548950413313> {humanize.intcomma(silver)}x <:gold:867815549042819113> {humanize.intcomma(gold)}x <:diamond:867815548862332969> {humanize.intcomma(diamond)}x"

        luck = Mineral.luck_cupcake()
        if luck:
            fg = random.randint(1, 5)
            message += f"\n<:alert_pink:867758260707000380> You were a bit lucky and you got also <:cupcake:845632403405012992> **{fg}x**!"
            await self.bot.db.execute("UPDATE cuppy SET balance = $1, pickaxe_earnings = $2 WHERE user_id = $3", data2[0]["balance"] + fg, data2[0]["pickaxe_earnings"] + fg, ctx.author.id)
            
        experience = Pickaxe.add_xp(pick)
        await self.bot.db.execute("UPDATE cuppy SET pickaxe_exp = $1 WHERE user_id = $2", data[0]["pickaxe_exp"] + experience, ctx.author.id)

        if (experience + pick_exp) >= pick_upgrade:
            message += f"\n<:alert_pink:867758260707000380> Oh! You pickaxe has <:xp:867817838941437974> **{humanize.intcomma(experience)} / {humanize.intcomma(pick_upgrade)}**, you can upgrade it!"
        else:
            message += f"\n<:alert_pink:867758260707000380> Your pickaxe gained <:xp:867817838941437974> **{humanize.intcomma(experience)}**!"

        await ctx.send(message)
        cvf = Pickaxe.use(pick)

        if cvf > pick_durability:
            cvf = pick_durability

        await self.bot.db.execute(f"UPDATE cuppy SET pickaxe_{query2} = $1, pickaxe_durability = $2 WHERE user_id = $3", data2[0][query], data2[0]["pickaxe_durability"] - cvf, ctx.author.id)

def setup(bot):
    bot.add_cog(Cuppy(bot))

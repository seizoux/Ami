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
            "wood": "No Special Perks.",
            "golden": "+5% chance to get gold.",
            "ephemeral": "+10% chance to get gold.",
            "candy": "+20% chance to get gold.",
            "sky": "+5% chance to get diamonds.",
            "nebula": "+10% chance to get diamonds.",
            "divine": "+20% chance to get diamonds."
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

    def minerals(self, l_type:str):
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
    async def test_balance(self, ctx):
        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
        if not data:
            await self.bot.db.execute("INSERT INTO cuppy (user_id, balance, pickaxe_type, pickaxe_exp, pickaxe_durability, pickaxe_earnings, pickaxe_diamonds, pickaxe_golds, pickaxe_silvers, pickaxe_bronzes, pickaxe_needed_xp, bronze, silver, gold, diamond) VALUES ($1, 10, $2, 0, 100, 0, 0, 0, 0, 0, $3, 0, 0, 0, 0)", ctx.author.id, "wood", 2000)
            return await ctx.send(f"{ctx.author.mention} **your balance is now ready!**\n<:alert_pink:867758260707000380> Earn minerals mining with your pickaxe using `ami mine`!\n"
                        f"<:alert_pink:867758260707000380> Vote to get <:lootbox:867758260622590002> and (**luckly**) <:uncommon:867764757733834793> <:rare:867764757670002698> or <:epic:867764757708406824> with `ami vote`!\n"
                        f"<:alert_pink:867758260707000380> Upgrade your pickaxe to even more good ones (<:nebula_pickaxe:862694657959395348> <:sky_pickaxe:862694658055340032> <:divine_pickaxe:862694657891631114>) with `ami pickaxe upgrade`!\n"
                        f"<:alert_pink:867758260707000380> Exchange the minerals you've got for <:cupcake:845632403405012992> with `ami exchange <mineral_name> <amount>`! Check `ami minerals values` for values of minerals!\n"
                        f"<:alert_pink:867758260707000380> Create your own clan, invite friends into it and raise it to the top!")

        bal = data[0]["balance"]
        await ctx.send(f"<:cupcake:845632403405012992> **{ctx.author.name}** balance is **{humanize.intcomma(bal)} Cupcakes!**")

    @commands.group(help="Check your pickaxe stats, upgrade it, and much more!", aliases=["pcx"], invoke_without_command=True)
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

            await self.bot.db.execute("UPDATE cuppy SET pickaxe_type = $1, pickaxe_exp = $2, pickaxe_durability = $3, pickaxe_needed_xp = $4 WHERE user_id = $5", upgrade_it, pick_exp-pick_needed_xp, 100, pick_exp + 500, ctx.author.id)
            await asyncio.sleep(1)
            data2 = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
            pick2 = data2[0]["pickaxe_type"]
            emoji = Pickaxe.emoji(pick2)
            name = Pickaxe.name(pick2)
            await ctx.send(f"<:alert_pink:867758260707000380> Congratulasions, **{ctx.author.name}**! You pickaxe was upgraded to {emoji} **{name}!**")
        else:
            return await ctx.reply(f"<:alert_pink:867758260707000380> Your pickaxe has **{humanize.intcomma(pick_exp)} / {humanize.intcomma(pick_needed_xp)}** <:xp:867817838941437974>, you can't upgrade it now.")

    @pickaxe.command()
    async def list(self, ctx):
        types = ["wood", "golden", "ephemeral", "candy", "sky", "nebula", "divine"]


        em = discord.Embed(title="All Pickaxes List", color=self.bot.color)
        for pick in types:
            name = Pickaxe.name(pick)
            emoji = Pickaxe.emoji(pick)
            perks = Pickaxe.perks(pick)
            em.add_field(name=f"{emoji} {name}", value=perks, inline=False)

        await ctx.send(embed=em)

    @commands.command()
    async def test_mine(self, ctx):
        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
        if not data:
            return await ctx.invoke(self.test_balance)

        pick = data[0]["pickaxe_type"]

        emoji = Pickaxe.emoji(pick)
        name = Pickaxe.name(pick)
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

        message = f"<:alert_pink:867758260707000380> **{ctx.author.name}** you've earned {full_emoji} **{fc}x {full_name}** thanks to your {emoji} **{name}**!\n<:alert_pink:867758260707000380> Now you have <:bronze:867815549144530944> {bronze}x <:silver:867815548950413313> {silver}x <:gold:867815549042819113> {gold}x <:diamond:867815548862332969> {diamond}x"

        luck = Mineral.luck_cupcake()
        if luck:
            fg = random.randint(1, 5)
            message + "\n" + f"<:alert_pink:867758260707000380> You were a bit lucky and you got also <:cupcake:845632403405012992> **{fg}x**!"
            await self.bot.db.execute("UPDATE cuppy SET balance = $1 WHERE user_id = $2", data2[0]["balance"] + fg, ctx.author.id)
            
        await ctx.send(message)
        await self.bot.db.execute(f"UPDATE cuppy SET pickaxe_{query2} = $1 WHERE user_id = $2", data2[0][query], ctx.author.id)

def setup(bot):
    bot.add_cog(Cuppy(bot))

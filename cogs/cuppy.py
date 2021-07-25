import discord
from discord.ext import commands, tasks
import datetime
import random
import asyncio
import humanize

class Team:
    def get_moves(team_name:str):
        moves = {
            "kury": {"base": ["punch", "kick"], "special" : ["energy beam", "tails smash"]},
            "anny": {"base": ["punch", "kick"], "special" : ["tsunami", "wave sonar"]},
            "fatima": {"base": ["punch", "kick"], "special" : ["energy ball", "fairy fate"]},
            "lilly": {"base": ["punch", "kick"], "special" : ["loud cry", "crying punch"]},
            "luna": {"base": ["punch", "kick"], "special" : ["angry fist", "power fist"]},
            "celia": {"base": ["punch", "kick"], "special" : ["black hole", "big bang"]},
            "micky": {"base": ["punch", "kick"], "special" : ["hammer smash", "pick-tick"]},
            "vanessa": {"base": ["punch", "kick"], "special" : ["last flame", "subzero flame"]},
            "ornella": {"base": ["punch", "kick"], "special" : ["ZzZ", "ZzZ 2"]},
        }

        return moves[team_name]

    def move_emoji(move_name:str):
        emojis = {
            "punch": "👊",
            "kick": "🦵",
            "energy beam": "<:energy_beam:868620834577711164>",
            "tails smash": "<:tails_smash:868620834602897458>",
            "tsunami": "<:tsunami:868620834837782578>",
            "wave sonar": "<:wave_sonar:868620834737094666>",
            "energy ball": "<:energy_ball:868620834560942132>",
            "fairy fate": "<:fairy_fate:868620834472874014>",
            "loud cry": "<:loud_cry:868620834569351198>",
            "crying punch": "<:cry_punch:868620834531590194>",
            "angry fist": "<:cry_punch:868620834531590194>",
            "power fist": "<:cry_punch:868620834531590194>",
            "black hole": "<:black_hole:868620834468659250>",
            "big bang": "<:big_bang:868620835483697192>",
            "hammer smash": "<:hammer_smash:868620834183446559>",
            "pick-tick": "<:pick_tick:868620834749693992>",
            "last flame": "<:last_flame:868620834753900635>",
            "subzero flame": "<:subzero_flame:868620834657411072>",
            "ZzZ": "<:zzz:868622437636522015>",
            "ZzZ 2": "<:zzz:868622437636522015>"
        }

        return emojis[move_name]

    def get_move_name(move_name:str):
        name = {
            "punch": "Punch",
            "kick": "Kick",
            "energy beam": "Energy Beam",
            "tails smash": "Tails Smash",
            "tsunami": "Tsunami",
            "wave sonar": "Wave Sonar",
            "energy ball": "Energy Ball",
            "fairy fate": "Fairy Fate",
            "loud cry": "Loud Cry",
            "crying punch": "Crying Punch",
            "angry fist": "Angry Fist",
            "power fist": "Power Fist",
            "black hole": "Black Hole",
            "big bang": "Big Bang",
            "hammer smash": "Hammer Smash",
            "pick-tick": "Pick-Tick",
            "last flame": "Last Flame",
            "subzero flame": "Subzero Flame",
            "ZzZ": "ZzZ",
            "ZzZ 2": "ZzZ 2.0"
        }        

        return name[move_name]

    def get_move_base_damage(move_name:str):
        damage = {
            "punch": 12,
            "kick": 12,
            "energy beam": 17,
            "tails smash": 26,
            "tsunami": 31,
            "wave sonar": 21,
            "energy ball": 15,
            "fairy fate": 50,
            "loud cry": 34,
            "crying punch": 38,
            "angry fist": 51,
            "power fist": 70,
            "black hole": 65,
            "big bang": 72,
            "hammer smash": 56,
            "pick-tick": 44,
            "last flame": 70,
            "subzero flame": 63,
            "ZzZ": 20,
            "ZzZ 2": 61
        }        

        return damage[move_name]

    def get_story(team_name:str):
        story = {
            "kury": "An adventurous girl, has defied the laws of nature obtaining a divine power, still still unable to fully master it, is looking for the unbeatable opponent, the one who does not go down with a single blow.",
            "anny": "The sea has always been his home, he has never left it, he loves living with the animals that live there and respects them from the first to the last, woe to those who harm him.",
            "fatima": "She has never been able to fully understand her generation, but she has always loved the fact that she has a power that only 2% of creatures in the universe have: being a fairy! Its spells are as bad as a tank.",
            "lilly": "She has the bad habit of crying even for nonsense, she never ends .. she loves to sleep and eat from morning to night, woe to those who disturb her.",
            "luna": "Not much is known about her, she appeared in town one day by chance and never revealed her origins .. the only sure thing we know is that her fists really hurt.",
            "celia": "It is said that she is the daughter of the universe, her powers allow her to stop time and space for a few seconds, no one has ever dared to harm her since she was born.",
            "micky": "This girl was once a professional mechanic, until a meteorite fell on her workshop and since she woke up she found herself with supernatural powers, like a force equal to 200 men.",
            "vanessa": "She is a mystery, she came here through a very badly tanned dimensional portal, since she recovered she has not wanted to mention anything that had happened to her: she is thought to have challenged the gods to prove herself.",
            "ornella": "Quiet, a normal country girl who loves to do absolutely nothing except look after her rebellious hair, except that she has practically infinite magical power, and a cheeky fortune."
        }

        return story[team_name]

    def images(team_name:str):
        imag = {
            "kury": "https://cdn.discordapp.com/attachments/800189588127612979/868561058032418847/62089ee9672198cd380b938aec5f1577.gif",
            "anny": "https://cdn.discordapp.com/attachments/800189588127612979/868561062381887519/2900920e2ac0a0c8f16eba53c837315b.gif",
            "fatima": "https://cdn.discordapp.com/attachments/800189588127612979/868561049102737408/3f66bea314d5ed8dc7355c98c8e2bdf5.gif",
            "lilly": "https://cdn.discordapp.com/attachments/800189588127612979/868561077598838794/ff986c4116c1551007ff0152e2a4d85e.gif",
            "luna": "https://cdn.discordapp.com/attachments/800189588127612979/868561067528323072/AW4101957_01.gif",
            "celia": "https://cdn.discordapp.com/attachments/800189588127612979/868561064651001947/61343192396756773fb4f0162ff03f7f.gif",
            "micky": "https://cdn.discordapp.com/attachments/800189588127612979/868561054257545286/95aa2d1da0354a42226b09f6b91dde0f.gif",
            "vanessa": "https://cdn.discordapp.com/attachments/800189588127612979/868561073580675152/de4e57e4e2cdf53dba84a026fe61086e.gif",
            "ornella": "https://cdn.discordapp.com/attachments/800189588127612979/868561069948428408/AW4101957_03.gif"
        }

        return imag[team_name]

    def calc_needed_xp(acxp:int):
        f = acxp + random.choice([500, 750, 1000])
        return f

    def friendship_calc(fr:int):

        needed = 10
        actual = int(fr/10)
        mex = ('■' * actual) + ('□' * (needed - actual))
        return mex

    def emoji(team_name:str):
        emojis = {
            "kury": "<a:Kury_Team:868398859766857749>",
            "anny": "<a:Anny_Team:868398861759172608>",
            "fatima": "<a:Fatima_Team:868398860601552927>",
            "lilly": "<a:Lilly_Team:868398860815446036>",
            "luna": "<a:Luna_Team:868398860660244490>",
            "celia": "<a:Celia_Team:868398861624946708>",
            "micky": "<a:Micky_Team:868398859796234290>",
            "vanessa": "<a:Vanessa_Team:868398860911931423>",
            "ornella": "<a:Ornella_Team:868398859989160006>"
        }

        return emojis[team_name]

    def name(team_name:str):
        names = {
            "kury": "Kury",
            "anny": "Anny",
            "fatima": "Fatima",
            "lilly": "Lilly",
            "luna": "Luna",
            "celia": "Celia",
            "micky": "Micky",
            "vanessa": "Vanessa",
            "ornella": "Ornella"
        }

        return names[team_name]

    def ivs(team_name:str):
        team_ivs = {
            "kury": {"atk": 150, "def": 107, "spd": 108, "hp": 105, "mag": 102, "luck": 105},
            "anny": {"atk": 106, "def": 104, "spd": 105, "hp": 103, "mag": 108, "luck": 109},
            "fatima": {"atk": 102, "def": 100, "spd": 104, "hp": 103, "mag": 100, "luck": 101},
            "lilly": {"atk": 104, "def": 100, "spd": 100, "hp": 106, "mag": 105, "luck": 102},
            "luna": {"atk": 105, "def": 103, "spd": 105, "hp": 108, "mag": 101, "luck": 107},
            "celia": {"atk": 103, "def": 108, "spd": 103, "hp": 102, "mag": 105, "luck": 100},
            "micky": {"atk": 105, "def": 105, "spd": 100, "hp": 107, "mag": 100, "luck": 105},
            "vanessa": {"atk": 105, "def": 103, "spd": 104, "hp": 106, "mag": 105, "luck": 106},
            "ornella": {"atk": 105, "def": 101, "spd": 105, "hp": 100, "mag": 105, "luck": 103}
        }

        return team_ivs[team_name]

class Exchange:
  def calculate_exc(mineral:str, amount:int):
    exc = {
      "bronze": 250,
      "silver": 125,
      "gold": 25,
      "diamond": 5
    }
  
    return int(amount / exc[mineral])

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
            "divine": 100,
            "orc": 250,
            "earth": 500
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
            "divine": 1,
            "orc": 1,
            "earth": 1
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
            "divine": random.randint(1, 10),
            "orc": random.randint(1, 8),
            "earth": random.randint(1, 5)
        }

        exp = pickaxes_rates_xp[pick_type]
        return exp

    def check_durability(dur:int):
        """
        Checking if the pickaxe durability isn't 0.
        """
        return dur != 0

    def durability_set(pick_type:str):
        pickaxes_durabilites = {
            "wood": 100,
            "golden": 150,
            "ephemeral": 200,
            "candy": 250,
            "sky": 300,
            "nebula": 350,
            "divine": 400,
            "orc": 450,
            "earth": 500
        }

        return pickaxes_durabilites[pick_type]

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
            "nebula": "divine",
            "divine": "orc",
            "orc": "earth",
            "earth": None
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
            "divine": "<:divine_pickaxe:862694657891631114>",
            "orc": "<:orc_pickaxe:868209126558294096>",
            "earth": "<:earth_pickaxe:868209126503759992>"
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
            "divine": "Divine Pickaxe",
            "orc": "Orc Pickaxe",
            "earth": "Earth Pickaxe"
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
            "divine": "<:alert_pink:867758260707000380> +20% Diamond Drop.\n<:xp:867817838941437974> `1` > `10`.\n<:durability:867818581864218654> `1` > `1`.\n<:cupcake:845632403405012992> `100`",
            "orc": "<:alert_pink:867758260707000380> +5% Cupcake Drop.\n<:xp:867817838941437974> `1` > `8`.\n<:durability:867818581864218654> `1` > `1`.\n<:cupcake:845632403405012992> `250`",
            "earth": "<:alert_pink:867758260707000380> +10% Cupcake Drop.\n<:xp:867817838941437974> `1` > `5`.\n<:durability:867818581864218654> `1` > `1`.\n<:cupcake:845632403405012992> `500`"
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

    async def cog_check(self, ctx):
        team = [144126010642792449, 410452466631442443, 711057339360477184, 590323594744168494, 691406006277898302, 343019667511574528]
        return ctx.author.id in team

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
        await ctx.send(f"{ctx.author.mention} you currently have <:cupcake:845632403405012992> **{humanize.intcomma(bal)} Cupcakes!**")

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def exchange(self, ctx, mineral_name, amount=None):
        valid_mins = ["bronze", "silver", "gold", "diamond"]
        if mineral_name.lower() not in valid_mins:
            return await ctx.send(f"<:4318crossmark:848857812565229601> {ctx.author.mention} **{mineral_name}** is not a valid mineral.")

        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
        if not data:
            return await ctx.invoke(self.test_balance)
        
        min = data[0][mineral_name.lower()]
        if amount is None:
            amount = min

        emoji = Mineral.emoji(mineral_name.lower())
        name = Mineral.name(mineral_name.lower())

        if amount > min:
            return await ctx.send(f"<:4318crossmark:848857812565229601> {ctx.author.mention} you have {emoji} **{min}x**, you can't exchange {emoji} **{amount}x**.")

        exc = Exchange.calculate_exc(mineral_name.lower(), amount)
        await self.bot.db.execute(f"UPDATE cuppy SET {mineral_name.lower()} = $1, balance = $2 WHERE user_id = $3", data[0][mineral_name.lower()] - amount, data[0]["balance"] + exc, ctx.author.id)
        await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} exchanged {emoji} **{humanize.intcomma(amount)}x {name}** and earned <:cupcake:845632403405012992> **{humanize.intcomma(exc)}x Cupcakes**!")

    @commands.group(help="Open your lootboxes <:lootbox:867758260622590002> <:uncommon:867764757733834793> <:rare:867764757670002698> <:epic:867764757708406824>", aliases=["op"], invoke_without_command=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def open(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command":"open"})

    @open.command(help="Choose what box")
    @commands.cooldown(1, 10, commands.BucketType.user)
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
        if not lb:
            return await ctx.send(f"<:4318crossmark:848857812565229601> You don't have any {emoji} **{name}** to open.")

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
    @commands.cooldown(1, 5, commands.BucketType.user)
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

            dur_calc = Pickaxe.durability_set(upgrade_it)

            await self.bot.db.execute("UPDATE cuppy SET pickaxe_type = $1, pickaxe_exp = $2, pickaxe_durability = $3, pickaxe_needed_xp = $4 WHERE user_id = $5", upgrade_it, pick_exp-pick_needed_xp, dur_calc, pick_exp + 750, ctx.author.id)
            await asyncio.sleep(1)
            data2 = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
            pick2 = data2[0]["pickaxe_type"]
            emoji = Pickaxe.emoji(pick2)
            name = Pickaxe.name(pick2)
            await ctx.send(f"<:alert_pink:867758260707000380> Congratulasions, **{ctx.author.name}**! You pickaxe was upgraded to {emoji} **{name}!**")
        else:
            return await ctx.reply(f"<:alert_pink:867758260707000380> Your pickaxe has <:xp:867817838941437974> **{humanize.intcomma(pick_exp)} / {humanize.intcomma(pick_needed_xp)}**, you can't upgrade it now.")

    @pickaxe.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def list(self, ctx):
        types = ["wood", "golden", "ephemeral", "candy", "sky", "nebula", "divine", "orc", "earth"]

        em = discord.Embed(title="All Pickaxes List", description = "<:xp:867817838941437974> Will tell you what is the XP drop range for each pickaxe\n<:durability:867818581864218654> Will tell you what is the usage range of durability for each pickaxe\n<:cupcake:845632403405012992> Will tell you how many cupcakes are needed to recharge it", color=self.bot.color)
        for pick in types:
            name = Pickaxe.name(pick)
            emoji = Pickaxe.emoji(pick)
            perks = Pickaxe.perks(pick)
            em.add_field(name=f"{emoji} {name}", value=perks)

        await ctx.send(embed=em)

    @pickaxe.command(aliases=["rc", "r"])
    @commands.cooldown(1, 5, commands.BucketType.user)
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
        await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.name}, you've spent <:cupcake:845632403405012992> **{recharge_amount}** to refill your {emoji} **{name}** durability!")

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

        await self.bot.db.execute(f"UPDATE cuppy SET pickaxe_{query2} = $1, pickaxe_durability = $2 WHERE user_id = $3", data2[0][f'pickaxe_{query2}'] + fc, data2[0]["pickaxe_durability"] - cvf, ctx.author.id)

    @commands.group(help="Build a squad with a teammate, check your team stats, upgrade the stats, and much more!", invoke_without_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def team(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command":"team"})

    @team.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def recruit(self, ctx, teammate_name:str):
        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
        if not data:
            return await ctx.invoke(self.test_balance)

        teammates = ["kury", "anny", "fatima", "lilly", "luna", "celia", "micky", "vanessa", "ornella"]

        if teammate_name.lower() not in teammates:
            return await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} this is not a valid teammate.")

        bal = data[0]["balance"]
        name = Team.name(teammate_name.lower())
        emoji = Team.emoji(teammate_name.lower())
        ivs = Team.ivs(teammate_name.lower())

        atk = ivs["atk"]
        defe = ivs["def"]
        speed = ivs["spd"]
        hp = ivs["hp"]
        magic = ivs["mag"]
        luck = ivs["luck"]

        if bal < 500:
            return await ctx.send(f"<:alert_pink:867758260707000380> You have only <:cupcake:845632403405012992> **{bal}**, you can't buy {emoji} **{name}**.")

        d = data[0]["team_name"]

        if d:
            if teammate_name.lower() == d:
                return await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} your current teammate is already {emoji} **{name}**")
    
            t_name = Team.name(d)
            t_emoji = Team.emoji(d)
            msg_b = await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} are you sure you want to replace {t_emoji} **{t_name}** × {emoji} **{name}** ?\n"
            f"<:alert_pink:867758260707000380> This will reset the IVs to the new teammate base IVs.\n<:alert_pink:867758260707000380> Reply in 30 seconds with \"CONFIRM\" to continue or with \"DECLINE\" to abort.")

            try:
                msg = await self.bot.wait_for("message", check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout = 30)
            except asyncio.TimeoutError:
                await msg_b.delete()
                return

            if msg.content.lower() == "confirm":
                fcg = Team.calc_needed_xp(0)
                await self.bot.db.execute("UPDATE cuppy SET team_name = $1, team_needed_xp = $2, balance = $3 WHERE user_id = $4", teammate_name.lower(), fcg, data[0]["balance"] - 500, ctx.author.id)

                await ctx.send(f"{ctx.author.mention} you've succesfully replaced your {t_emoji} **{t_name}** with {emoji} **{name}** for <:cupcake:845632403405012992> **500**!\n⚔ `{atk}` 🛡 `{defe}`\n👟 `{speed}` ❤ `{hp}`\n✨ `{magic}` 🍀 `{luck}`")

                for k,v in ivs.items():
                    await self.bot.db.execute(f"UPDATE cuppy SET team_{k} = $1 WHERE user_id = $2", v, ctx.author.id)

                return

            elif msg.content.lower() == "decline":
                await msg_b.delete()
                try:
                    await msg.delete()
                except Exception:
                    pass

                return
            else:
                pass

        fcg = Team.calc_needed_xp(0)
        await self.bot.db.execute("UPDATE cuppy SET team_name = $1, team_needed_xp = $2, balance = $3 WHERE user_id = $4", teammate_name.lower(), fcg, data[0]["balance"] - 500, ctx.author.id)

        await ctx.send(f"{ctx.author.mention} you've succesfully recruited {emoji} **{name}** for <:cupcake:845632403405012992> **500**!\n⚔ `{atk}` 🛡 `{defe}`\n👟 `{speed}` ❤ `{hp}`\n✨ `{magic}` 🍀 `{luck}`")

        for k,v in ivs.items():
            await self.bot.db.execute(f"UPDATE cuppy SET team_{k} = $1 WHERE user_id = $2", v, ctx.author.id)

    @team.command(name="stats")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def team_stats(self, ctx, member : discord.Member = None):
        if member is None:
            member = ctx.author

        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", member.id)
        if not data:
            return await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} this member is not a cuppy player.")

        teammate = data[0]["team_name"]
        if not teammate:
            return await ctx.send(f"<:alert_pink:867758260707000380> Teammate not found.")

        name = Team.name(teammate)
        emoji = Team.emoji(teammate)
        moves = Team.get_moves(teammate)
        basic = moves["base"]
        special = moves["special"]

        special_final = []
        basic_final = []

        for move in basic:
            name = Team.get_move_name(move)
            emoji = Team.move_emoji(move)
            damage = Team.get_move_base_damage(move)
            basic_final.append(f"{emoji} **{name}** | 💥 {damage}")

        for move in special:
            name2 = Team.get_move_name(move)
            emoji2 = Team.move_emoji(move)
            damage2 = Team.get_move_base_damage(move)
            special_final.append(f"{emoji2} **{name2}** | 💥 {damage2}")

        b_final = '\n'.join(basic_final)
        s_final = '\n'.join(special_final)

        atk = data[0]["team_atk"]
        defe = data[0]["team_def"]
        speed = data[0]["team_spd"]
        hp = data[0]["team_hp"]
        magic = data[0]["team_mag"]
        luck = data[0]["team_luck"]
        exp = data[0]["team_xp"]
        level = data[0]["team_level"]
        needed_xp = data[0]["team_needed_xp"]
        wins = data[0]["team_wins"]
        loses = data[0]["team_loses"]
        draws = data[0]["team_ties"]
        friendship = data[0]["team_friendship"]

        f_calc = Team.friendship_calc(friendship)
        img = Team.images(teammate)
        story = Team.get_story(teammate)

        em = discord.Embed(
                title=f"{ctx.author.name}'s Teammate",
                description=f"<:alert_pink:867758260707000380> {emoji} **{name}**\n{story}",
                color = self.bot.color)
        em.add_field(name="IVs", value=f"⚔ `{atk}` 🛡 `{defe}`\n👟 `{speed}` ❤ `{hp}`\n✨ `{magic}` 🍀 `{luck}`")
        em.add_field(name="Progress", 
        value=f"<:xp:867817838941437974> **EXP**: {humanize.intcomma(exp)} / {humanize.intcomma(needed_xp)}\n"
        f"<:level:868426330293821450> **Level**: {humanize.intcomma(level)}\n"
        f"🏅 **Wins**: {humanize.intcomma(wins)}\n"
        f"🥈 **Loses**:{humanize.intcomma(loses)}\n"
        f"🥉 **Draws**: {humanize.intcomma(draws)}")
        em.add_field(name="Moveset", value=f"{b_final}\n{s_final}")
        em.set_thumbnail(url=img)
        em.set_footer(text=f"× Friendship: 0% {f_calc} 100%")

        await ctx.send(embed=em)


    @team.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shop(self, ctx):
        em = discord.Embed(title="Teammates Shop", description="Recruiting one of them will cost you <:cupcake:845632403405012992> **500**\n`ami team recruit <teammate_name>` to recruit one of these teammates.\n`ami team stats` to check your actual teammate stats.\nIVs will became higher leveling up your teammate.\n⚔ Attack, 🛡 Defense, 👟 Speed, ❤ HP, ✨ Magic, 🍀 Luck", color = self.bot.color)

        teammates = ["kury", "anny", "fatima", "lilly", "luna", "celia", "micky", "vanessa", "ornella"]
        for teams in teammates:
            name = Team.name(teams)
            emoji = Team.emoji(teams)
            ivs = Team.ivs(teams)

            atk = ivs["atk"]
            defe = ivs["def"]
            speed = ivs["spd"]
            hp = ivs["hp"]
            magic = ivs["mag"]
            luck = ivs["luck"]

            em.add_field(name=f"{emoji} {name}", value=f"⚔ `{atk}` 🛡 `{defe}`\n👟 `{speed}` ❤ `{hp}`\n✨ `{magic}` 🍀 `{luck}`")

        await ctx.send(embed=em)

    @commands.command()
    async def battle(self, ctx, opponent: discord.Member):
        data1 = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
        data2 = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", opponent.id)

        if not data1:
            return await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} you are not registered into cuppy, type `ami balance` to register yourself.")

        if not data2:
            return await ctx.send(f"<:alert_pink:867758260707000380> {opponent.mention} is not registered into cuppy.")

        team_author = data1[0]["team_name"]
        team_opponent = data2[0]["team_name"]

        if not team_author:
            return await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} you don't have a teammate to battle, check `ami team shop`.")

        if not team_opponent:
            return await ctx.send(f"<:alert_pink:867758260707000380> {opponent.mention} has not a teammate to battle.")

        n_team_author = Team.name(team_author)
        n_team_opponent = Team.name(team_opponent)

        e_team_author = Team.emoji(team_author)
        e_team_opponent = Team.emoji(team_opponent)

        m_team_author = Team.get_moves(team_author)
        m_team_opponent = Team.get_moves(team_opponent)

        atk_team_author = data1[0]["team_atk"]
        atk_team_opponent = data2[0]["team_atk"]

        def_team_author = data1[0]["team_def"]
        def_team_opponent = data2[0]["team_def"]

        hp_team_author = data1[0]["team_hp"] * 10
        hp_team_opponent = data2[0]["team_hp"] * 10

        basic_moves_author = m_team_author["base"]
        basic_moves_opponent = m_team_opponent["base"]

        special_moves_author = m_team_author["special"]
        special_moves_opponent = m_team_opponent["special"]

        level_team_author = data1[0]["team_level"]
        level_team_opponent = data2[0]["team_level"]

        b_msg = await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} challenged {opponent.mention} to a battle!\n"
                    "----------------------------------------------------------\n"
                    f"<:level:868426330293821450> **{level_team_author}** <:level:868426330293821450>         <:level:868426330293821450> **{level_team_opponent}** <:level:868426330293821450>\n"
                    f"{e_team_author} **{n_team_author}** VS {e_team_opponent} **{n_team_opponent}**\n"
                    "----------------------------------------------------------\n"
                    f"<:alert_pink:867758260707000380> {opponent.mention} in 30 seconds type \"CONFIRM\" to accept or \"DECLINE\" to abort.")

        try:
            msg = await self.bot.wait_for("message", check=lambda m: m.author.id == opponent.id and m.channel.id == ctx.channel.id, timeout = 30)
        except asyncio.TimeoutError:
            await b_msg.delete()
            return

        if msg.content.lower() not in ["confirm", "decline"]:
            pass

        current_hp_author = hp_team_author
        current_hp_opponent = hp_team_author

        while True:
            cc_1 = random.choice(range(1, 10))
            if cc_1 in range(1,7):
                move_author = random.choice(basic_moves_author)
            else:
                move_author = random.choice(special_moves_author)

            cc_2 = random.choice(range(1, 10))
            if cc_2 in range(1,7):
                move_opponent = random.choice(basic_moves_opponent)
            else:
                move_opponent = random.choice(special_moves_opponent)

            author_move_name = Team.get_move_name(move_author)
            author_move_emoji = Team.move_emoji(move_author)
            author_move_damage = Team.get_move_base_damage(move_author)

            opponent_move_name = Team.get_move_name(move_opponent)
            opponent_move_emoji = Team.move_emoji(move_opponent)
            opponent_move_damage = Team.get_move_base_damage(move_opponent)

            critical_author = False
            critical_opponent = False

            cf_1 = random.choice([1, 2])
            if cf_1 in range(1, 50):
                pass
            elif cf_1 in range(50, 75):
                critical_author = True
            else:
                critical_opponent = True

            final_damage_author = 0
            final_damage_opponent = 0

            if critical_author:
                final_damage_author = author_move_damage + (atk_team_author/10) + random.randint(1, 15) - (def_team_opponent/10)
            else:
                final_damage_author = author_move_damage + (atk_team_author/10)

            if critical_opponent:
                final_damage_opponent = opponent_move_damage + (atk_team_opponent/10) + random.randint(1, 15) - (def_team_author/10)
            else:
                final_damage_opponent = opponent_move_damage + (atk_team_opponent/10)

            await ctx.send(f"{e_team_author} **{n_team_author}** landed a {author_move_emoji} **{author_move_name}**: that felt 💥 {final_damage_author}!\n"
                            f"{e_team_opponent} **{n_team_opponent}** landed a {opponent_move_emoji} **{opponent_move_name}**: that felt 💥 {final_damage_opponent}!")

            current_hp_author = current_hp_author - final_damage_author
            current_hp_opponent = current_hp_opponent - final_damage_opponent

            em = discord.Embed(color = self.bot.color)
            em.add_field(name=f"{e_team_author} {n_team_author}", value=f"❤ {current_hp_author} / {hp_team_author} ❤")
            em.add_field(name=f"{e_team_opponent} {n_team_opponent}", value=f"❤ {current_hp_opponent} / {hp_team_opponent} ❤")
            em.set_footer(text="Next moves land in 5 seconds.")
            await ctx.send(embed=em)

            if current_hp_opponent <= 0:
                xp_amount = random.randint(20, 75)
                await self.bot.db.execute("UPDATE cuppy SET team_xp = $1 WHERE user_id = $2", data1[0]["team_xp"] + xp_amount, ctx.author.id)
                data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)

                if data[0]["team_xp"] >= data[0]["team_needed_xp"]:
                    c_nxp = Team.calc_needed_xp(data[0]["team_xp"])
                    await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} {e_team_author} **{n_team_author}** won this battle and gained **{xp_amount}**!\n"
                                    f"<:alert_pink:867758260707000380> Oh! {e_team_author} **{n_team_author}** leveled up to <:level:868426330293821450> **{data[0]['team_level'] + 1}**!")
                    await self.bot.db.execute("UPDATE cuppy SET team_needed_xp = $1, team_level = $2, team_xp = $3 WHERE user_id = $4", c_nxp, data[0]["team_level"] + 1, 0, ctx.author.id)
                    break

                await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} {e_team_author} **{n_team_author}** won this battle and gained **{xp_amount}**!")
                break

            elif current_hp_author <= 0:
                xp_amount = random.randint(20, 75)
                await self.bot.db.execute("UPDATE cuppy SET team_xp = $1 WHERE user_id = $2", data2[0]["team_xp"] + xp_amount, opponent.id)
                data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", opponent.id)

                if data[0]["team_xp"] >= data[0]["team_needed_xp"]:
                    c_nxp = Team.calc_needed_xp(data[0]["team_xp"])
                    await ctx.send(f"<:alert_pink:867758260707000380> {opponent.mention} {e_team_opponent} **{n_team_opponent}** won this battle and gained **{xp_amount}**!\n"
                                    f"<:alert_pink:867758260707000380> Oh! {e_team_opponent} **{n_team_opponent}** leveled up to <:level:868426330293821450> **{data[0]['team_level'] + 1}**!")
                    await self.bot.db.execute("UPDATE cuppy SET team_needed_xp = $1, team_level = $2, team_xp = $3 WHERE user_id = $4", c_nxp, data[0]["team_level"] + 1, 0, opponent.id)
                    break

                await ctx.send(f"<:alert_pink:867758260707000380> {opponent.mention} {e_team_opponent} **{n_team_opponent}** won this battle and gained **{xp_amount}**!")
                break

            await asyncio.sleep(5)
            continue

def setup(bot):
    bot.add_cog(Cuppy(bot))

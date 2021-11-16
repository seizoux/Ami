import discord
from discord.ext import commands, tasks, menus
import datetime
import random
import asyncio
import humanize
from util.defs import is_team
import uuid
import typing
from captcha.image import ImageCaptcha
from io import BytesIO
import os
from millify import millify

from aiohttp import ClientSession
from PIL import Image, ImageDraw, ImageFont

from discord import Color, File

class XpRoom:
    def parse_upgrade(upgrade_type: str, upgrade_level: int):
        """
        Parse the cost upgrade for xpr stats based on
        upgrade type and current level + 1, basic implementation.
        """
        vfc = {
            "cost": {
                2: 3000,
                3: 6000,
                4: 10000,
                5: 15000,
                6: 30000,
                7: 60000,
                8: 120000,
                9: 240000,
                10: 480000,
            },
            "farm": {
                2: 1500,
                3: 3000,
                4: 7000,
                5: 13000,
                6: 26000,
                7: 48000,
                8: 96000,
                9: 192000,
                10: 384000,
            },
            "duration": {
                2: 5000,
                3: 10000,
                4: 20000,
                5: 40000,
                6: 80000,
                7: 160000,
                8: 320000,
                9: 640000,
                10: 1280000,
            },
        }

        return vfc[upgrade_type][upgrade_level]

    def time_parser(duration_level: int):
        """
        Parse the time that the xpr can run for the
        current level.
        """
        calcs = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11, 11: 12}

        return calcs[duration_level]

    def farm_parser(farm_level: int):
        """
        Returns a list(range()) object based on the
        farm current level.
        """
        facts = {
            1: list(range(1000, 3500)),
            2: list(range(3000, 7500)),
            3: list(range(5000, 16500)),
            4: list(range(7000, 22500)),
            5: list(range(9000, 28500)),
            6: list(range(11000, 34500)),
            7: list(range(13000, 40500)),
            8: list(range(15000, 46000)),
            9: list(range(17000, 52500)),
            10: list(range(20000, 60000)),
        }

        return facts[farm_level]

    def cost_parser(cost_level: int, duration: int):
        """
        Cost parser for xpr, basic implementation.
        """
        base_cost = 1550
        return int((base_cost / cost_level) * (XpRoom.time_parser(duration) * 10) / 10)


class BattleRenderer:
    BACKGROUND_URL = "https://cdn.discordapp.com/attachments/851875804945973330/870696897311023204/battle_arena.png"
    FONT_PATH = "./fonts/coolvetica rg.ttf"

    def __init__(
        self,
        char_1="https://cdn.discordapp.com/attachments/851875804945973330/870696969364996156/celia.gif",
        char_2="https://cdn.discordapp.com/attachments/851875804945973330/870696985714376734/vanessa.gif",
        *,
        char_1_stats,
        char_2_stats,
        loop=None,
    ):
        self._char_1 = char_1
        self._char_2 = char_2
        self._font = None
        self._small_font = None
        self._vs_font = None

        self._c1_stats = char_1_stats
        self._c2_stats = char_2_stats
        self._loop = loop or asyncio.get_event_loop()

    async def read(self):
        # Replace instances of this with your bot's session if you have one
        async with ClientSession() as session:
            async with session.get(self.BACKGROUND_URL) as response:
                background = await response.read()

            async with session.get(self._char_1) as response:
                char_1 = await response.read()

            async with session.get(self._char_2) as response:
                char_2 = await response.read()

        with open(self.FONT_PATH, "rb") as fp:
            self._font = ImageFont.truetype(BytesIO(fp.read()), size=64)
            fp.seek(0)
            self._small_font = ImageFont.truetype(BytesIO(fp.read()), size=38)
            fp.seek(0)
            self._vs_font = ImageFont.truetype(BytesIO(fp.read()), size=200)

        return background, char_1, char_2

    def _render(self, background, char_1, char_2, char_1_hp, char_2_hp):
        with Image.open(BytesIO(background)) as image:
            image = image.convert("RGBA")

            with Image.open(BytesIO(char_1)) as asset:
                # (1920, 1080)
                asset = asset.convert("RGBA").resize((700, 700))
                image.paste(asset, (50, 350), asset)

            with Image.open(BytesIO(char_2)) as asset:
                asset = asset.convert("RGBA").resize((700, 700))
                image.paste(asset, (1920 - 750, 350), asset)

            draw = ImageDraw.Draw(image)
            points = ((50, 50), (750, 50), (600, 300), (50, 300))
            draw.polygon(points, (244, 244, 244, 255))
            draw.line(
                points + ((50, 43),), (244, 244, 244, 230), width=15, joint="curve"
            )

            points = (
                (1920 - 50, 50),
                (1920 - 750, 50),
                (1920 - 600, 300),
                (1920 - 50, 300),
            )
            draw.polygon(points, (244, 244, 244, 255))
            draw.line(
                points + ((1920 - 50, 43),),
                (244, 244, 244, 230),
                width=15,
                joint="curve",
            )

            w, h = self._vs_font.getsize("VS")
            draw.text(
                (int(image.width / 2 - w / 2), 75),
                "VS",
                (255, 255, 255, 255),
                font=self._vs_font,
            )

            ratio = char_1_hp / self._c1_stats["max_hp"]
            color = Color.from_hsv(0.3 * ratio, 1, 1).to_rgb()

            draw.text((75, 65), self._c1_stats["name"], (0, 0, 0, 255), self._font)
            draw.text(
                (75, 140),
                f'Level {self._c1_stats["level"]:,}',
                (0, 0, 0, 255),
                self._small_font,
            )
            draw.text(
                (75, 185),
                f'{char_1_hp:,} / {self._c1_stats["max_hp"]} HP',
                (0, 0, 0, 255),
                self._small_font,
            )

            hp_width = 350
            draw.rectangle((75, 240, 75 + hp_width, 280), (233, 233, 233))
            draw.rectangle((80, 245, 80 + int(ratio * (hp_width - 10)), 275), color)

            ratio = char_2_hp / self._c2_stats["max_hp"]
            color = Color.from_hsv(0.3 * ratio, 1, 1).to_rgb()

            text = self._c2_stats["name"]
            draw.text(
                (1920 - 75 - self._font.getsize(text)[0], 65),
                text,
                (0, 0, 0, 255),
                self._font,
            )
            text = f'Level {self._c2_stats["level"]:,}'
            draw.text(
                (1920 - 75 - self._small_font.getsize(text)[0], 140),
                text,
                (0, 0, 0, 255),
                self._small_font,
            )
            text = f'{char_2_hp:,} / {self._c2_stats["max_hp"]} HP'
            draw.text(
                (1920 - 75 - self._small_font.getsize(text)[0], 185),
                text,
                (0, 0, 0, 255),
                self._small_font,
            )

            draw.rectangle((1920 - 75, 240, 1920 - 75 - hp_width, 280), (233, 233, 233))
            draw.rectangle(
                (1920 - 80, 245, 1920 - (80 + int(ratio * (hp_width - 10))), 275), color
            )

            buffer = BytesIO()
            image.save(buffer, "png")
            buffer.seek(0)
            return buffer

    async def render(self, char_1_hp, char_2_hp) -> File:
        buffer = await self._loop.run_in_executor(
            None, self._render, *await self.read(), char_1_hp, char_2_hp
        )
        return File(buffer, "battle.png")


class Paginate(menus.ListPageSource):
    def __init__(self, entries, *, per_page=15):
        entries = [f"{name}" for name in entries]
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        embed = discord.Embed(
            title="Monsters List",
            description="That's a list of all the "
            "currently spottable monster "
            "into `monsterhunt`!\n<:common:870289549052477450> `Common` <:rare:870289549543215144> `Rare` <:super_rare:870289549400616980> `Super Rare` <:mystic:870289549153165332> `Mystic` 🌟 `Special`\n\n"
            + "\n".join(page)
            + "\n\n═════ **Reactions Info**═════ \n⏮ `first` ◀ `back` ▶ `next` ⏩ `end` ⏹ `stop`\n"
            "*This message expires in 45.5 seconds!*",
            color=0xFFCFF1,
        )

        return embed


class Clan:
    def next_league(actual: str):
        next = {"silver": "gold", "gold": "diamond", "diamond": None}

        return next[actual]

    def max_members(league: str):
        mem = {"silver": 50, "gold": 75, "diamond": 125}

        return mem[league]

    def league_emoji(league: str):
        leg = {
            "silver": "<:silver_league:870741139039322134>",
            "gold": "<:gold_league:870741138343088129>",
            "diamond": "<:diamond_league:870741137873334315>",
        }

        return leg[league]

    def league_image(league: str):
        im = {
            "silver": "https://cdn.discordapp.com/attachments/869970935015419967/870741335840268328/silver_league.png",
            "gold": "https://cdn.discordapp.com/attachments/869970935015419967/870741332010876998/gold_league.png",
            "diamond": "https://cdn.discordapp.com/attachments/869970935015419967/870741328324091924/diamond_league.png",
        }

        return im[league]

    def league_name(league: str):
        nam = {"silver": "Silver", "gold": "Gold", "diamond": "Diamond"}

        return nam[league]

    def needed_xp(league: str):
        xp = {"silver": 500000, "gold": 1000000, "diamond": 2000000}

        return xp[league]


class Rarity:
    def find_rarity(type: int):
        rarity = {
            1: "Common (50% encounter rate)",
            2: "Rare (25% encounter rate)",
            3: "Super Rare (20% encounter rate)",
            4: "Mystic (4% encounter rate)",
            5: "Special (1% encounter rate)",
        }

        return rarity[type]

    def emoji(rare: str):
        emojis = {
            1: "<:common:870289549052477450>",
            2: "<:rare:870289549543215144>",
            3: "<:super_rare:870289549400616980>",
            4: "<:mystic:870289549153165332>",
            5: "🌟",
        }

        return emojis[rare]


class Monster:
    def rarity_ordered(rarity: str):
        rare_ord = {
            "common": [
                "skull slime",
                "shadow",
                "pumpkin witch",
                "bat",
                "silver crocodile",
                "ancient golem",
                "zombie",
                "slime",
                "skeleton",
                "oricorio",
                "fire magician",
                "devil octopus",
                "chica",
                "fat reaper",
            ],
            "rare": [
                "orc tauros",
                "demon spirit",
                "dark dragon",
                "blue dragon",
                "red oricorio",
                "minotaur",
                "ice dragon",
                "grodd gorilla",
                "cthulhu",
                "wolf fighter",
                "ice dino",
                "ice golem",
                "gtruo",
                "magician",
                "demon horse",
                "bugbear",
                "olione",
            ],
            "super rare": [
                "minotaur king",
                "stone golem",
                "sea girl",
                "sam",
                "rathian",
                "nergigante",
                "kukulkan",
                "demon girl",
                "crystal golem",
                "t-rex",
                "platinum dragon",
                "norroth",
            ],
            "mystic": [
                "molten iron golem",
                "magala",
                "imperial dragon",
                "godzilla",
                "galaxy dragon",
                "decalion",
                "holidoom",
                "quetzalcoatl",
                "magala final form",
                "laymon",
                "chaos dragon",
                "wyvern",
                "magala (gore)",
            ],
            "special": [
                "naruto",
                "luffy",
                "rin",
                "nezuko",
                "saitama",
                "deku",
                "goku",
                "natsu",
                "monokuma",
                "mega lucario",
                "thor",
            ],
        }

        return rare_ord[rarity]

    def get_rarity(monster: str):
        rare = {
            "skull slime": 1,
            "silver crocodile": 1,
            "shadow": 1,
            "pumpkin witch": 1,
            "orc tauros": 2,
            "demon spirit": 2,
            "dark dragon": 2,
            "blue dragon": 2,
            "bat": 1,
            "ancient golem": 1,
            "zombie": 1,
            "slime": 1,
            "skeleton": 1,
            "red oricorio": 2,
            "oricorio": 1,
            "molten iron golem": 4,
            "minotaur king": 3,
            "minotaur": 2,
            "magala": 4,
            "imperial dragon": 4,
            "ice dragon": 2,
            "grodd gorilla": 2,
            "godzilla": 4,
            "galaxy dragon": 4,
            "fire magician": 1,
            "devil octopus": 1,
            "decalion": 4,
            "cthulhu": 2,
            "chica": 1,
            "holidoom": 4,
            "quetzalcoatl": 4,
            "wolf fighter": 2,
            "stone golem": 3,
            "sea girl": 3,
            "sam": 3,
            "rathian": 3,
            "nergigante": 3,
            "magician": 2,
            "magala final form": 4,
            "laymon": 4,
            "kukulkan": 3,
            "ice golem": 2,
            "ice dino": 2,
            "gtruo": 2,
            "fat reaper": 1,
            "demon horse": 2,
            "demon girl": 3,
            "crystal golem": 3,
            "bugbear": 2,
            "chaos dragon": 4,
            "magala (gore)": 4,
            "wyvern": 4,
            "t-rex": 3,
            "platinum dragon": 3,
            "norroth": 3,
            "olione": 2,
            "naruto": 5,
            "luffy": 5,
            "rin": 5,
            "nezuko": 5,
            "saitama": 5,
            "deku": 5,
            "goku": 5,
            "natsu": 5,
            "monokuma": 5,
            "mega lucario": 5,
            "thor": 5,
        }

        return rare[monster]

    def get_image(monster: str):
        link = {
            "skull slime": "https://cdn.discordapp.com/attachments/869312190119813250/869312365303312394/skull_slime.png",
            "silver crocodile": "https://cdn.discordapp.com/attachments/869312190119813250/869312355643818034/silver_crocodile.png",
            "shadow": "https://cdn.discordapp.com/attachments/869312190119813250/869312349167841321/shadow.png",
            "pumpkin witch": "https://cdn.discordapp.com/attachments/869312190119813250/869312321099542578/pumpkin_witch.png",
            "orc tauros": "https://cdn.discordapp.com/attachments/869312190119813250/869312317056245820/orc_tauros.png",
            "demon spirit": "https://cdn.discordapp.com/attachments/869312190119813250/869312273607454770/demon_spirit.png",
            "dark dragon": "https://cdn.discordapp.com/attachments/869312190119813250/869312259397124156/dark_dragon.png",
            "blue dragon": "https://cdn.discordapp.com/attachments/869312190119813250/869312249452445706/blue_dragon.png",
            "bat": "https://cdn.discordapp.com/attachments/869312190119813250/869312246717747200/bat.png",
            "ancient golem": "https://cdn.discordapp.com/attachments/869312190119813250/869312244075360326/ancient_golem.png",
            "zombie": "https://cdn.discordapp.com/attachments/869312190119813250/869312371158560869/zombie.png",
            "slime": "https://cdn.discordapp.com/attachments/869312190119813250/869312368197390397/slime.png",
            "skeleton": "https://cdn.discordapp.com/attachments/869312190119813250/869312361956253737/skeleton.png",
            "red oricorio": "https://cdn.discordapp.com/attachments/869312190119813250/869312342519840778/red_oricorio.png",
            "oricorio": "https://cdn.discordapp.com/attachments/869312190119813250/869312318868160593/oricorio.png",
            "molten iron golem": "https://cdn.discordapp.com/attachments/869312190119813250/869312314820689940/molten_iron_golem.png",
            "minotaur king": "https://cdn.discordapp.com/attachments/869312190119813250/869312312803217478/minotaur_king.png",
            "minotaur": "https://cdn.discordapp.com/attachments/869312190119813250/869312310601216050/minotaur.png",
            "magala": "https://cdn.discordapp.com/attachments/869312190119813250/869312303424757861/magala.png",
            "imperial dragon": "https://cdn.discordapp.com/attachments/869312190119813250/869312296252498051/imperial_dragon.png",
            "ice dragon": "https://cdn.discordapp.com/attachments/869312190119813250/869312291647148073/ice_dragon.png",
            "grodd gorilla": "https://cdn.discordapp.com/attachments/869312190119813250/869312289067634748/grodd_gorilla.png",
            "godzilla": "https://cdn.discordapp.com/attachments/869250340925624371/869310211016491028/godzilla.png",
            "galaxy dragon": "https://cdn.discordapp.com/attachments/869250340925624371/869310194289614908/galaxy_dragon.png",
            "fire magician": "https://cdn.discordapp.com/attachments/869312190119813250/869312276765741076/fire_magician.png",
            "devil octopus": "https://cdn.discordapp.com/attachments/869312190119813250/869312275117400164/devil_octopus.png",
            "decalion": "https://cdn.discordapp.com/attachments/869312190119813250/869312270197485599/decalion.png",
            "cthulhu": "https://cdn.discordapp.com/attachments/869312190119813250/869312255483842571/cthulhu.png",
            "chica": "https://cdn.discordapp.com/attachments/869312190119813250/869312252904362074/chica.png",
            "holidoom": "https://cdn.discordapp.com/attachments/869312190119813250/869363614501457960/Holidoom.png",
            "quetzalcoatl": "https://cdn.discordapp.com/attachments/869312190119813250/869363618448306236/Quetzalcoatl.png",
            "wolf fighter": "https://cdn.discordapp.com/attachments/869250340925624371/869560051730366525/wolf_fighter.png",
            "stone golem": "https://cdn.discordapp.com/attachments/869250340925624371/869560048999862332/stone_golem.png",
            "sea girl": "https://cdn.discordapp.com/attachments/869250340925624371/869560046453940244/sea_girl.png",
            "sam": "https://cdn.discordapp.com/attachments/869250340925624371/869560043408871424/sam.png",
            "rathian": "https://cdn.discordapp.com/attachments/869250340925624371/869560030255521822/rathian.png",
            "nergigante": "https://cdn.discordapp.com/attachments/869250340925624371/869564283393024010/nergigante.png",
            "magician": "https://cdn.discordapp.com/attachments/869250340925624371/869564279542669402/magician.png",
            "magala final form": "https://cdn.discordapp.com/attachments/869250340925624371/869564275528695839/magala_final_form.png",
            "laymon": "https://cdn.discordapp.com/attachments/869250340925624371/869560008306729010/laymon.png",
            "kukulkan": "https://cdn.discordapp.com/attachments/869250340925624371/869560005756592148/Kukulkan.png",
            "ice golem": "https://cdn.discordapp.com/attachments/869250340925624371/869560003210649711/ice_golem.png",
            "ice dino": "https://cdn.discordapp.com/attachments/869250340925624371/869564658007289876/ice_dino.png",
            "gtruo": "https://cdn.discordapp.com/attachments/869250340925624371/869560000547278848/gtruo.png",
            "fat reaper": "https://cdn.discordapp.com/attachments/869250340925624371/869559998043283456/fat_reaper.png",
            "demon horse": "https://cdn.discordapp.com/attachments/869250340925624371/869559994872381451/demon_horse.png",
            "demon girl": "https://cdn.discordapp.com/attachments/869250340925624371/869559992599068722/demon_girl.png",
            "crystal golem": "https://cdn.discordapp.com/attachments/869250340925624371/869559990766166096/crystal_golem.png",
            "bugbear": "https://cdn.discordapp.com/attachments/869250340925624371/869559985321938954/bugbear.png",
            "chaos dragon": "https://cdn.discordapp.com/attachments/869250340925624371/869559988207620166/chaos_dragon.png",
            "magala (gore)": "https://cdn.discordapp.com/attachments/870014290374066189/870015214047875082/Magala_Gore.png",
            "wyvern": "https://cdn.discordapp.com/attachments/870014290374066189/870015230888013844/wyvern.png",
            "t-rex": "https://cdn.discordapp.com/attachments/870014290374066189/870015227113144330/t-rex.png",
            "platinum dragon": "https://cdn.discordapp.com/attachments/870014290374066189/870015222864281640/platinum_dragon.png",
            "norroth": "https://cdn.discordapp.com/attachments/870014290374066189/870015217332002826/norroth.png",
            "olione": "https://cdn.discordapp.com/attachments/870014290374066189/870015219856986152/olione.png",
            "naruto": "https://cdn.discordapp.com/attachments/870014290374066189/871154084160339998/naruto.png",
            "luffy": "https://cdn.discordapp.com/attachments/870014290374066189/871154079861182494/luffy_gear_fourth.png",
            "rin": "https://cdn.discordapp.com/attachments/870014290374066189/871154094633541672/rin.png",
            "nezuko": "https://cdn.discordapp.com/attachments/870014290374066189/871154090137239562/nezuko.png",
            "saitama": "https://cdn.discordapp.com/attachments/870014290374066189/871154100593647666/saitama.png",
            "deku": "https://cdn.discordapp.com/attachments/870014290374066189/871154076635770990/deku.png",
            "goku": "https://cdn.discordapp.com/attachments/870014290374066189/871154078233821194/goku_ultra_instinct.png",
            "natsu": "https://cdn.discordapp.com/attachments/870014290374066189/871154087310295060/natsu.png",
            "monokuma": "https://cdn.discordapp.com/attachments/870014290374066189/871154081635369000/monokuma.png",
            "mega lucario": "https://cdn.discordapp.com/attachments/800189588127612979/875100818301415464/mega-lucario.png",
            "thor": "https://cdn.discordapp.com/attachments/870014290374066189/885071437164085248/ced19a6796b41bd17f77a64213ed3aa3.png",
        }

        return link[monster]

    def all_monsters():
        here = [
            "skull slime",
            "silver crocodile",
            "shadow",
            "pumpkin witch",
            "orc tauros",
            "demon spirit",
            "dark dragon",
            "blue dragon",
            "bat",
            "ancient golem",
            "zombie",
            "slime",
            "skeleton",
            "red oricorio",
            "oricorio",
            "molten iron golem",
            "minotaur king",
            "minotaur",
            "magala",
            "imperial dragon",
            "ice dragon",
            "grodd gorilla",
            "godzilla",
            "galaxy dragon",
            "fire magician",
            "devil octopus",
            "decalion",
            "cthulhu",
            "chica",
            "holidoom",
            "quetzalcoatl",
            "wolf fighter",
            "stone golem",
            "sea girl",
            "sam",
            "rathian",
            "nergigante",
            "magician",
            "magala final form",
            "laymon",
            "kukulkan",
            "ice golem",
            "ice dino",
            "gtruo",
            "fat reaper",
            "demon horse",
            "demon girl",
            "crystal golem",
            "bugbear",
            "chaos dragon",
            "magala (gore)",
            "wyvern",
            "t-rex",
            "platinum dragon",
            "norroth",
            "olione",
            "naruto",
            "luffy",
            "rin",
            "nezuko",
            "saitama",
            "deku",
            "goku",
            "natsu",
            "monokuma",
            "mega lucario",
            "thor",
        ]

        return here

    def emoji(monster: str):
        emojis = {
            "skull slime": "<:skull_slime:869250806640177162>",
            "silver crocodile": "<:silver_crocodile:869250806623404073>",
            "shadow": "<:shadow:869250806690484255>",
            "pumpkin witch": "<:pumpkin_witch:869250806556291152>",
            "orc tauros": "<:orc_tauros:869250806560489562>",
            "demon spirit": "<:demon_spirit:869250807017660437>",
            "dark dragon": "<:dark_dragon:869250806543683644>",
            "blue dragon": "<:blue_dragon:869250806556295209>",
            "bat": "<:bat:869250806149427251>",
            "ancient golem": "<:ancient_golem:869250806539509760>",
            "zombie": "<:zombie:869290440661303367>",
            "slime": "<:slime:869264026218156052>",
            "skeleton": "<:skeleton:869290440535461928>",
            "red oricorio": "<:red_oricorio:869264026226557008>",
            "oricorio": "<:oricorio:869264026289442817>",
            "molten iron golem": "<:molten_iron_golem:869264025681276941>",
            "minotaur king": "<:minotaur_king:869264026071351348>",
            "minotaur": "<:minotaur:869264025979093083>",
            "magala": "<:magala:869264026134265896>",
            "imperial dragon": "<:imperial_dragon:869291288510468096>",
            "ice dragon": "<:ice_dragon:869264026130087967>",
            "grodd gorilla": "<:grodd_gorilla:869290440283783210>",
            "godzilla": "<:godzilla:869290440740991047>",
            "galaxy dragon": "<:galaxy_dragon:869264028218834944>",
            "fire magician": "<:fire_magician:869290440703221780>",
            "devil octopus": "<:devil_octopus:869264026125889556>",
            "decalion": "<:decalion:869264025949720647>",
            "cthulhu": "<:cthulhu:869264025945530419>",
            "chica": "<:chica:869264025677094933>",
            "holidoom": "<:Holidoom:869363432804208670>",
            "quetzalcoatl": "<:Quetzalcoatl:869363433856974958>",
            "wolf fighter": "<:wolf_figher:869553031719575592>",
            "stone golem": "<:stone_golem:869551762703536148>",
            "sea girl": "<:sea_girl:869554141666615307>",
            "sam": "<:sam:869551762770645022>",
            "rathian": "<:rathian:869551762359611444>",
            "nergigante": "<:nergigante:869552744971784272>",
            "magician": "<:magician:869551762623823892>",
            "magala final form": "<:magala_final_form:869554594831798353>",
            "laymon": "<:laymon:869550902195945493>",
            "kukulkan": "<:kukulkan:869551762648993812>",
            "ice golem": "<:ice_golem:869551762619650088>",
            "ice dino": "<:ice_dino:869555291375681556>",
            "gtruo": "<:gtRuO:869552642903384074>",
            "fat reaper": "<:fat_reaper:869550901117997158>",
            "demon horse": "<:demon_horse:869554141440139264>",
            "demon girl": "<:demon_girl:869554206326013962>",
            "crystal golem": "<:crystal_golem:869553033099489330>",
            "bugbear": "<:bugbear:869550717491355678>",
            "chaos dragon": "<:chaos_dragon:869555190951464990>",
            "magala (gore)": "<:magala_gore:870014389967798313>",
            "wyvern": "<:wyvern:870014390345277511>",
            "t-rex": "<:trex:870014390395609098>",
            "platinum dragon": "<:platinum_dragon:870014390034911233>",
            "norroth": "<:norroth:870014389820993547>",
            "olione": "<:olione:870014390206877756>",
            "naruto": "<:naruto:871152621866602537>",
            "luffy": "<:luffy_gear_fourth:871152622747390053>",
            "rin": "<:rin:871152621979861052>",
            "nezuko": "<:nezuko:871152621761753118>",
            "saitama": "<:saitama:871152621883375666>",
            "deku": "<:deku:871152621296185384>",
            "goku": "<:goku_ultra_instinct:871152621325541436>",
            "natsu": "<:natsu:871152621673664562>",
            "monokuma": "<:monokuma:871152621556207636>",
            "mega lucario": "<:mega_lucario:875100667415502928>",
            "thor": "<:thor:885071372991213630>",
        }

        return emojis[monster]

    def name(monster: str):
        m_name = {
            "skull slime": "Skull Slime",
            "silver crocodile": "Silver Crocodile",
            "shadow": "Shadow",
            "pumpkin witch": "Pumpkin Witch",
            "orc tauros": "Orc Tauros",
            "demon spirit": "Demon Spirit",
            "dark dragon": "Dark Dragon",
            "blue dragon": "Blue Dragon",
            "bat": "Bat",
            "ancient golem": "Ancient Golem",
            "zombie": "Zombie",
            "slime": "Slime",
            "skeleton": "Skeleton",
            "red oricorio": "Red Oricorio",
            "oricorio": "Oricorio",
            "molten iron golem": "Molten Iron Golem",
            "minotaur king": "Minotaur King",
            "minotaur": "Minotaur",
            "magala": "Magala",
            "imperial dragon": "Imperial Dragon",
            "ice dragon": "Ice Dragon",
            "grodd gorilla": "Grodd Gorilla",
            "godzilla": "Godzilla",
            "galaxy dragon": "Galaxy Dragon",
            "fire magician": "Fire Magician",
            "devil octopus": "Devil Octopus",
            "decalion": "Decalion",
            "cthulhu": "Cthulhu",
            "chica": "Chica",
            "holidoom": "Holidoom",
            "quetzalcoatl": "Quetzalcoatl",
            "wolf fighter": "Wolf Fighter",
            "stone golem": "Stone Golem",
            "sea girl": "Sea Girl",
            "sam": "Sam",
            "rathian": "Rathian",
            "nergigante": "Nergigante",
            "magician": "Magician",
            "magala final form": "Magala (Final Form)",
            "laymon": "Laymon",
            "kukulkan": "Kukulkan",
            "ice golem": "Ice Golem",
            "ice dino": "Ice Dino",
            "gtruo": "Gtruo",
            "fat reaper": "Fat Reaper",
            "demon horse": "Demon Horse",
            "demon girl": "Demon Girl",
            "crystal golem": "Crystal Golem",
            "bugbear": "Bugbear",
            "chaos dragon": "Chaos Dragon",
            "magala (gore)": "Magala (Gore)",
            "wyvern": "Wyvern",
            "t-rex": "T-Rex",
            "platinum dragon": "Platinum Dragon",
            "norroth": "Norroth",
            "olione": "Olione",
            "naruto": "Naruto (Six Path)",
            "luffy": "Luffy (4th Gear)",
            "rin": "Rin",
            "nezuko": "Nezuko",
            "saitama": "Saitama",
            "deku": "Deku",
            "goku": "Goku (Ultra Instinct)",
            "natsu": "Natsu",
            "monokuma": "Monokuma",
            "mega lucario": "Mega Lucario",
            "thor": "Thor",
        }

        return m_name[monster]

    def xp_drop(monster: str):
        xp = {
            "skull slime": 15,
            "silver crocodile": 15,
            "shadow": 10,
            "pumpkin witch": 10,
            "orc tauros": 25,
            "demon spirit": 45,
            "dark dragon": 50,
            "blue dragon": 50,
            "bat": 15,
            "ancient golem": 20,
            "zombie": 10,
            "slime": 10,
            "skeleton": 10,
            "red oricorio": 35,
            "oricorio": 30,
            "molten iron golem": 50,
            "minotaur king": 50,
            "minotaur": 30,
            "magala": 65,
            "imperial dragon": 100,
            "ice dragon": 50,
            "grodd gorilla": 40,
            "godzilla": 100,
            "galaxy dragon": 100,
            "fire magician": 30,
            "devil octopus": 30,
            "decalion": 100,
            "cthulhu": 45,
            "chica": 25,
            "holidoom": 100,
            "quetzalcoatl": 100,
            "wolf fighter": 50,
            "stone golem": 25,
            "sea girl": 50,
            "sam": 75,
            "rathian": 75,
            "nergigante": 50,
            "magician": 25,
            "magala final form": 100,
            "laymon": 100,
            "kukulkan": 50,
            "ice golem": 25,
            "ice dino": 25,
            "gtruo": 40,
            "fat reaper": 25,
            "demon horse": 50,
            "demon girl": 50,
            "crystal golem": 50,
            "bugbear": 25,
            "chaos dragon": 100,
            "magala (gore)": 100,
            "wyvern": 100,
            "t-rex": 50,
            "platinum dragon": 75,
            "norroth": 50,
            "olione": 25,
            "naruto": 500,
            "luffy": 500,
            "rin": 500,
            "nezuko": 500,
            "saitama": 500,
            "deku": 500,
            "goku": 500,
            "natsu": 500,
            "monokuma": 500,
            "mega lucario": 500,
            "thor": 500,
        }

        return xp[monster]

    def get_hp(monster: str):
        hp = {
            "skull slime": 50,
            "silver crocodile": 50,
            "shadow": 50,
            "pumpkin witch": 50,
            "orc tauros": 50,
            "demon spirit": 150,
            "dark dragon": 200,
            "blue dragon": 200,
            "bat": 50,
            "ancient golem": 50,
            "zombie": 50,
            "slime": 50,
            "skeleton": 50,
            "red oricorio": 150,
            "oricorio": 50,
            "molten iron golem": 300,
            "minotaur king": 300,
            "minotaur": 100,
            "magala": 250,
            "imperial dragon": 300,
            "ice dragon": 150,
            "grodd gorilla": 150,
            "godzilla": 300,
            "galaxy dragon": 300,
            "fire magician": 50,
            "devil octopus": 50,
            "decalion": 300,
            "cthulhu": 250,
            "chica": 50,
            "holidoom": 300,
            "quetzalcoatl": 300,
            "wolf fighter": 100,
            "stone golem": 100,
            "sea girl": 150,
            "sam": 150,
            "rathian": 200,
            "nergigante": 100,
            "magician": 100,
            "magala final form": 300,
            "laymon": 300,
            "kukulkan": 200,
            "ice golem": 150,
            "ice dino": 100,
            "gtruo": 100,
            "fat reaper": 50,
            "demon horse": 150,
            "demon girl": 150,
            "crystal golem": 200,
            "bugbear": 100,
            "chaos dragon": 300,
            "magala (gore)": 300,
            "wyvern": 300,
            "t-rex": 200,
            "platinum dragon": 250,
            "norroth": 150,
            "olione": 100,
            "naruto": 400,
            "luffy": 400,
            "rin": 400,
            "nezuko": 400,
            "saitama": 400,
            "deku": 400,
            "goku": 400,
            "natsu": 400,
            "monokuma": 400,
            "mega lucario": 400,
            "thor": 400,
        }

        return hp[monster]

    def cup_drop(monster: str):
        cup = {
            "skull slime": 100,
            "silver crocodile": 100,
            "shadow": 300,
            "pumpkin witch": 300,
            "orc tauros": 300,
            "demon spirit": 300,
            "dark dragon": 500,
            "blue dragon": 500,
            "bat": 100,
            "ancient golem": 300,
            "zombie": 100,
            "slime": 100,
            "skeleton": 100,
            "red oricorio": 500,
            "oricorio": 300,
            "molten iron golem": 1000,
            "minotaur king": 1000,
            "minotaur": 300,
            "magala": 1500,
            "imperial dragon": 1500,
            "ice dragon": 500,
            "grodd gorilla": 500,
            "godzilla": 1500,
            "galaxy dragon": 1500,
            "fire magician": 300,
            "devil octopus": 300,
            "decalion": 1500,
            "cthulhu": 300,
            "chica": 300,
            "holidoom": 1500,
            "quetzalcoatl": 1500,
            "wolf fighter": 300,
            "stone golem": 1000,
            "sea girl": 1000,
            "sam": 1000,
            "rathian": 1000,
            "nergigante": 1000,
            "magician": 300,
            "magala final form": 1500,
            "laymon": 1500,
            "kukulkan": 1000,
            "ice golem": 500,
            "ice dino": 300,
            "gtruo": 300,
            "fat reaper": 100,
            "demon horse": 300,
            "demon girl": 1000,
            "crystal golem": 1000,
            "bugbear": 100,
            "chaos dragon": 1500,
            "magala (gore)": 1500,
            "wyvern": 1500,
            "t-rex": 1000,
            "platinum dragon": 1000,
            "norroth": 1000,
            "olione": 300,
            "naruto": 5000,
            "luffy": 5000,
            "rin": 5000,
            "nezuko": 5000,
            "saitama": 5000,
            "deku": 5000,
            "goku": 5000,
            "natsu": 5000,
            "monokuma": 5000,
            "mega lucario": 5000,
            "thor": 5000,
        }

        return cup[monster]


class Team:
    def get_moves(team_name: str):
        moves = {
            "kury": {
                "base": ["punch", "kick"],
                "special": ["energy beam", "tails smash"],
                "ultra": "evil eyes",
            },
            "anny": {
                "base": ["punch", "kick"],
                "special": ["tsunami", "wave sonar"],
                "ultra": "ice realm",
            },
            "fatima": {
                "base": ["punch", "kick"],
                "special": ["energy ball", "fairy fate"],
                "ultra": "dream dimension",
            },
            "lilly": {
                "base": ["punch", "kick"],
                "special": ["loud cry", "crying punch"],
                "ultra": "water spin",
            },
            "luna": {
                "base": ["punch", "kick"],
                "special": ["angry fist", "power fist"],
                "ultra": "ultra fist",
            },
            "celia": {
                "base": ["punch", "kick"],
                "special": ["black hole", "big bang"],
                "ultra": "void gateway",
            },
            "micky": {
                "base": ["punch", "kick"],
                "special": ["hammer smash", "pick-tick"],
                "ultra": "mjolnir",
            },
            "vanessa": {
                "base": ["punch", "kick"],
                "special": ["last flame", "subzero flame"],
                "ultra": "meteor fall",
            },
            "ornella": {
                "base": ["punch", "kick"],
                "special": ["ZzZ", "ZzZ 2"],
                "ultra": "ZzZ 3",
            },
            "kury (prestiged)": {
                "base": ["punch", "kick"],
                "special": ["energy beam", "tails smash"],
                "ultra": "evil eyes",
            },
            "anny (prestiged)": {
                "base": ["punch", "kick"],
                "special": ["tsunami", "wave sonar"],
                "ultra": "ice realm",
            },
            "fatima (prestiged)": {
                "base": ["punch", "kick"],
                "special": ["energy ball", "fairy fate"],
                "ultra": "dream dimension",
            },
            "lilly (prestiged)": {
                "base": ["punch", "kick"],
                "special": ["loud cry", "crying punch"],
                "ultra": "water spin",
            },
            "luna (prestiged)": {
                "base": ["punch", "kick"],
                "special": ["angry fist", "power fist"],
                "ultra": "ultra fist",
            },
            "celia (prestiged)": {
                "base": ["punch", "kick"],
                "special": ["black hole", "big bang"],
                "ultra": "void gateway",
            },
            "micky (prestiged)": {
                "base": ["punch", "kick"],
                "special": ["hammer smash", "pick-tick"],
                "ultra": "mjolnir",
            },
            "vanessa (prestiged)": {
                "base": ["punch", "kick"],
                "special": ["last flame", "subzero flame"],
                "ultra": "meteor fall",
            },
            "ornella (prestiged)": {
                "base": ["punch", "kick"],
                "special": ["ZzZ", "ZzZ 2"],
                "ultra": "ZzZ 3",
            },
        }

        return moves[team_name]

    def move_emoji(move_name: str):
        emojises = {
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
            "ZzZ 2": "<:zzz:868622437636522015>",
            "ZzZ 3": "<:zzz_3:869203680056979556>",
            "water spin": "<:water_spin:869203680082165871>",
            "void gateway": "<:void_gateway:869203679885000745>",
            "ultra fist": "<:ultra_fist:869203680623222794>",
            "mjolnir": "<:mjolnir:869203679566233641>",
            "meteor fall": "<:meteor_fall:869204645078237205>",
            "ice realm": "<:ice_realm:869203679289434142>",
            "evil eyes": "<:evil_eye:869203679465570334>",
            "dream dimension": "<:dream_dimension:869203680048586833>",
        }

        return emojises[move_name]

    def get_move_name(move_name: str):
        nameses = {
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
            "ZzZ 2": "ZzZ 2.0",
            "ZzZ 3": "ZzZ 3.0",
            "water spin": "Water Spin",
            "void gateway": "Void Gateway",
            "ultra fist": "Ultra Fist",
            "mjolnir": "Mjolnir",
            "meteor fall": "Meteor Fall",
            "ice realm": "Ice Realm",
            "evil eyes": "Evil Eyes",
            "dream dimension": "Dream Dimension",
        }

        return nameses[move_name]

    def get_move_base_damage(move_name: str):
        damage = {
            "punch": 4,
            "kick": 4,
            "energy beam": 24,
            "tails smash": 27,
            "tsunami": 23,
            "wave sonar": 25,
            "energy ball": 24,
            "fairy fate": 27,
            "loud cry": 25,
            "crying punch": 25,
            "angry fist": 26,
            "power fist": 27,
            "black hole": 26,
            "big bang": 28,
            "hammer smash": 24,
            "pick-tick": 25,
            "last flame": 28,
            "subzero flame": 26,
            "ZzZ": 23,
            "ZzZ 2": 27,
            "ZzZ 3": 130,
            "water spin": 130,
            "void gateway": 130,
            "ultra fist": 130,
            "mjolnir": 130,
            "meteor fall": 130,
            "ice realm": 130,
            "evil eyes": 130,
            "dream dimension": 130,
        }

        return damage[move_name]

    def get_story(team_name: str):
        story = {
            "kury": "An adventurous girl, has defied the laws of nature obtaining a divine power, still still unable to fully master it, is looking for the unbeatable opponent, the one who does not go down with a single blow.",
            "anny": "The sea has always been his home, he has never left it, he loves living with the animals that live there and respects them from the first to the last, woe to those who harm him.",
            "fatima": "She has never been able to fully understand her generation, but she has always loved the fact that she has a power that only 2% of creatures in the universe have: being a fairy! Its spells are as bad as a tank.",
            "lilly": "She has the bad habit of crying even for nonsense, she never ends .. she loves to sleep and eat from morning to night, woe to those who disturb her.",
            "luna": "Not much is known about her, she appeared in town one day by chance and never revealed her origins .. the only sure thing we know is that her fists really hurt.",
            "celia": "It is said that she is the daughter of the universe, her powers allow her to stop time and space for a few seconds, no one has ever dared to harm her since she was born.",
            "micky": "This girl was once a professional mechanic, until a meteorite fell on her workshop and since she woke up she found herself with supernatural powers, like a force equal to 200 men.",
            "vanessa": "She is a mystery, she came here through a very badly tanned dimensional portal, since she recovered she has not wanted to mention anything that had happened to her: she is thought to have challenged the gods to prove herself.",
            "ornella": "Quiet, a normal country girl who loves to do absolutely nothing except look after her rebellious hair, except that she has practically infinite magical power, and a cheeky fortune.",
            "kury (prestiged)": "An adventurous girl, has defied the laws of nature obtaining a divine power, still still unable to fully master it, is looking for the unbeatable opponent, the one who does not go down with a single blow.",
            "anny (prestiged)": "The sea has always been his home, he has never left it, he loves living with the animals that live there and respects them from the first to the last, woe to those who harm him.",
            "fatima (prestiged)": "She has never been able to fully understand her generation, but she has always loved the fact that she has a power that only 2% of creatures in the universe have: being a fairy! Its spells are as bad as a tank.",
            "lilly (prestiged)": "She has the bad habit of crying even for nonsense, she never ends .. she loves to sleep and eat from morning to night, woe to those who disturb her.",
            "luna (prestiged)": "Not much is known about her, she appeared in town one day by chance and never revealed her origins .. the only sure thing we know is that her fists really hurt.",
            "celia (prestiged)": "It is said that she is the daughter of the universe, her powers allow her to stop time and space for a few seconds, no one has ever dared to harm her since she was born.",
            "micky (prestiged)": "This girl was once a professional mechanic, until a meteorite fell on her workshop and since she woke up she found herself with supernatural powers, like a force equal to 200 men.",
            "vanessa (prestiged)": "She is a mystery, she came here through a very badly tanned dimensional portal, since she recovered she has not wanted to mention anything that had happened to her: she is thought to have challenged the gods to prove herself.",
            "ornella (prestiged)": "Quiet, a normal country girl who loves to do absolutely nothing except look after her rebellious hair, except that she has practically infinite magical power, and a cheeky fortune.",
        }

        return story[team_name]

    def images(team_name: str):
        imag = {
            "kury": "https://cdn.discordapp.com/attachments/800189588127612979/868561058032418847/62089ee9672198cd380b938aec5f1577.gif",
            "anny": "https://cdn.discordapp.com/attachments/800189588127612979/868561062381887519/2900920e2ac0a0c8f16eba53c837315b.gif",
            "fatima": "https://cdn.discordapp.com/attachments/800189588127612979/868561049102737408/3f66bea314d5ed8dc7355c98c8e2bdf5.gif",
            "lilly": "https://cdn.discordapp.com/attachments/800189588127612979/868561077598838794/ff986c4116c1551007ff0152e2a4d85e.gif",
            "luna": "https://cdn.discordapp.com/attachments/800189588127612979/868561067528323072/AW4101957_01.gif",
            "celia": "https://cdn.discordapp.com/attachments/800189588127612979/868561064651001947/61343192396756773fb4f0162ff03f7f.gif",
            "micky": "https://cdn.discordapp.com/attachments/800189588127612979/868561054257545286/95aa2d1da0354a42226b09f6b91dde0f.gif",
            "vanessa": "https://cdn.discordapp.com/attachments/800189588127612979/868561073580675152/de4e57e4e2cdf53dba84a026fe61086e.gif",
            "ornella": "https://cdn.discordapp.com/attachments/800189588127612979/868561069948428408/AW4101957_03.gif",
            "kury (prestiged)": "https://cdn.discordapp.com/attachments/800189588127612979/868561058032418847/62089ee9672198cd380b938aec5f1577.gif",
            "anny (prestiged)": "https://cdn.discordapp.com/attachments/800189588127612979/868561062381887519/2900920e2ac0a0c8f16eba53c837315b.gif",
            "fatima (prestiged)": "https://cdn.discordapp.com/attachments/800189588127612979/868561049102737408/3f66bea314d5ed8dc7355c98c8e2bdf5.gif",
            "lilly (prestiged)": "https://cdn.discordapp.com/attachments/800189588127612979/868561077598838794/ff986c4116c1551007ff0152e2a4d85e.gif",
            "luna (prestiged)": "https://cdn.discordapp.com/attachments/800189588127612979/868561067528323072/AW4101957_01.gif",
            "celia (prestiged)": "https://cdn.discordapp.com/attachments/800189588127612979/868561064651001947/61343192396756773fb4f0162ff03f7f.gif",
            "micky (prestiged)": "https://cdn.discordapp.com/attachments/800189588127612979/868561054257545286/95aa2d1da0354a42226b09f6b91dde0f.gif",
            "vanessa (prestiged)": "https://cdn.discordapp.com/attachments/800189588127612979/868561073580675152/de4e57e4e2cdf53dba84a026fe61086e.gif",
            "ornella (prestiged)": "https://cdn.discordapp.com/attachments/800189588127612979/868561069948428408/AW4101957_03.gif",
        }

        return imag[team_name]

    def calc_needed_xp(level: int, teammate: str):
        if teammate.endswith("(prestiged)"):
            vf = 50000
        else:
            vf = 3500

        for i in range(1, level):
            vf += 2370

        return vf

    def emoji(team_name: str):
        emojis = {
            "kury": "<a:Kury_Team:868398859766857749>",
            "anny": "<a:Anny_Team:868398861759172608>",
            "fatima": "<a:Fatima_Team:868398860601552927>",
            "lilly": "<a:Lilly_Team:868398860815446036>",
            "luna": "<a:Luna_Team:868398860660244490>",
            "celia": "<a:Celia_Team:868398861624946708>",
            "micky": "<a:Micky_Team:868398859796234290>",
            "vanessa": "<a:Vanessa_Team:868398860911931423>",
            "ornella": "<a:Ornella_Team:868398859989160006>",
            "kury (prestiged)": "<a:Kury_Team:868398859766857749>",
            "anny (prestiged)": "<a:Anny_Team:868398861759172608>",
            "fatima (prestiged)": "<a:Fatima_Team:868398860601552927>",
            "lilly (prestiged)": "<a:Lilly_Team:868398860815446036>",
            "luna (prestiged)": "<a:Luna_Team:868398860660244490>",
            "celia (prestiged)": "<a:Celia_Team:868398861624946708>",
            "micky (prestiged)": "<a:Micky_Team:868398859796234290>",
            "vanessa (prestiged)": "<a:Vanessa_Team:868398860911931423>",
            "ornella (prestiged)": "<a:Ornella_Team:868398859989160006>",
        }

        return emojis[team_name]

    def name(team_name: str):
        names = {
            "kury": "Kury",
            "anny": "Anny",
            "fatima": "Fatima",
            "lilly": "Lilly",
            "luna": "Luna",
            "celia": "Celia",
            "micky": "Micky",
            "vanessa": "Vanessa",
            "ornella": "Ornella",
            "kury (prestiged)": "<:prestiged:870289549190897664> Kury",
            "anny (prestiged)": "<:prestiged:870289549190897664> Anny",
            "fatima (prestiged)": "<:prestiged:870289549190897664> Fatima",
            "lilly (prestiged)": "<:prestiged:870289549190897664> Lilly",
            "luna (prestiged)": "<:prestiged:870289549190897664> Luna",
            "celia (prestiged)": "<:prestiged:870289549190897664> Celia",
            "micky (prestiged)": "<:prestiged:870289549190897664> Micky",
            "vanessa (prestiged)": "<:prestiged:870289549190897664> Vanessa",
            "ornella (prestiged)": "<:prestiged:870289549190897664> Ornella",
        }

        return names[team_name]

    def ivs(team_name: str):
        team_ivs = {
            "kury": {"atk": 20, "def": 10, "spd": 10, "hp": 25, "mag": 20, "luck": 15},
            "anny": {"atk": 18, "def": 14, "spd": 15, "hp": 16, "mag": 18, "luck": 12},
            "fatima": {
                "atk": 19,
                "def": 10,
                "spd": 14,
                "hp": 15,
                "mag": 10,
                "luck": 13,
            },
            "lilly": {"atk": 15, "def": 10, "spd": 10, "hp": 16, "mag": 15, "luck": 12},
            "luna": {"atk": 16, "def": 13, "spd": 15, "hp": 18, "mag": 11, "luck": 17},
            "celia": {"atk": 19, "def": 18, "spd": 13, "hp": 15, "mag": 18, "luck": 15},
            "micky": {"atk": 20, "def": 15, "spd": 10, "hp": 17, "mag": 19, "luck": 15},
            "vanessa": {
                "atk": 18,
                "def": 13,
                "spd": 14,
                "hp": 16,
                "mag": 15,
                "luck": 16,
            },
            "ornella": {
                "atk": 19,
                "def": 15,
                "spd": 15,
                "hp": 10,
                "mag": 15,
                "luck": 13,
            },
            "kury (prestiged)": {
                "atk": 300,
                "def": 200,
                "spd": 200,
                "hp": 225,
                "mag": 220,
                "luck": 215,
            },
            "anny (prestiged)": {
                "atk": 280,
                "def": 240,
                "spd": 250,
                "hp": 216,
                "mag": 218,
                "luck": 212,
            },
            "fatima (prestiged)": {
                "atk": 290,
                "def": 200,
                "spd": 240,
                "hp": 250,
                "mag": 200,
                "luck": 230,
            },
            "lilly (prestiged)": {
                "atk": 250,
                "def": 200,
                "spd": 200,
                "hp": 260,
                "mag": 250,
                "luck": 220,
            },
            "luna (prestiged)": {
                "atk": 260,
                "def": 230,
                "spd": 250,
                "hp": 280,
                "mag": 210,
                "luck": 270,
            },
            "celia (prestiged)": {
                "atk": 290,
                "def": 280,
                "spd": 230,
                "hp": 250,
                "mag": 280,
                "luck": 250,
            },
            "micky (prestiged)": {
                "atk": 300,
                "def": 250,
                "spd": 200,
                "hp": 270,
                "mag": 290,
                "luck": 250,
            },
            "vanessa (prestiged)": {
                "atk": 280,
                "def": 230,
                "spd": 240,
                "hp": 260,
                "mag": 250,
                "luck": 260,
            },
            "ornella (prestiged)": {
                "atk": 290,
                "def": 250,
                "spd": 250,
                "hp": 200,
                "mag": 250,
                "luck": 230,
            },
        }

        return team_ivs[team_name]

    def ivs_level_based(team_name: str, level: int):
        final_ivs = {}
        team = Team.ivs(team_name)
        for k, v in team.items():
            for i in range(0, level):
                v += 3
                final_ivs[k] = v

        return final_ivs


class Exchange:
    def calculate_exc(mineral: str, amount: int):
        exc = {"bronze": 250, "silver": 125, "gold": 25, "diamond": 5}

        return int(amount / exc[mineral])

    def exc_info(mineral: str):
        exci = {"bronze": 250, "silver": 125, "gold": 25, "diamond": 5}

        return exci[mineral]


class Mineral:
    def emoji(mineral: str):
        emo = {
            "bronze": "<:bronze:867815549144530944>",
            "silver": "<:silver:867815548950413313>",
            "gold": "<:gold:867815549042819113>",
            "diamond": "<:diamond:867815548862332969>",
        }

        return emo[mineral]

    def name(mineral: str):
        name = {
            "bronze": "Bronze",
            "silver": "Silver",
            "gold": "Gold",
            "diamond": "Diamond",
        }

        return name[mineral]

    def amount(mineral_name: str):
        rates = {
            "bronze": random.randint(1, 100),
            "silver": random.randint(1, 50),
            "gold": random.randint(1, 20),
            "diamond": random.randint(1, 5),
        }

        return rates[mineral_name]

    def base_mine_parser(pickaxe_type: str, mineral: str):
        bbgd = {
            "wood": {
                "bronze": random.randint(1, 100),
                "silver": random.randint(1, 50),
                "gold": random.randint(1, 20),
                "diamond": random.randint(1, 5),
            },
            "golden": {
                "bronze": random.randint(50, 200),
                "silver": random.randint(25, 150),
                "gold": random.randint(10, 50),
                "diamond": random.randint(1, 8),
            },
            "ephemeral": {
                "bronze": random.randint(100, 300),
                "silver": random.randint(50, 250),
                "gold": random.randint(20, 100),
                "diamond": random.randint(1, 11),
            },
            "candy": {
                "bronze": random.randint(200, 400),
                "silver": random.randint(100, 350),
                "gold": random.randint(30, 200),
                "diamond": random.randint(1, 14),
            },
            "sky": {
                "bronze": random.randint(400, 500),
                "silver": random.randint(150, 450),
                "gold": random.randint(40, 300),
                "diamond": random.randint(1, 17),
            },
            "nebula": {
                "bronze": random.randint(450, 600),
                "silver": random.randint(200, 550),
                "gold": random.randint(50, 400),
                "diamond": random.randint(1, 20),
            },
            "divine": {
                "bronze": random.randint(500, 700),
                "silver": random.randint(250, 650),
                "gold": random.randint(60, 500),
                "diamond": random.randint(1, 23),
            },
            "orc": {
                "bronze": random.randint(550, 800),
                "silver": random.randint(300, 750),
                "gold": random.randint(70, 600),
                "diamond": random.randint(1, 26),
            },
            "earth": {
                "bronze": random.randint(600, 900),
                "silver": random.randint(350, 850),
                "gold": random.randint(80, 700),
                "diamond": random.randint(1, 30),
            },
        }

        return bbgd[pickaxe_type][mineral]

    def luck_cupcake():
        r = random.randint(1, 100)
        return r in range(1, 10)


class Pickaxe:
    def calculate_charge(pick_type: str):
        pickaxes_recharges = {
            "wood": 1,
            "golden": 2,
            "ephemeral": 5,
            "candy": 10,
            "sky": 20,
            "nebula": 50,
            "divine": 100,
            "orc": 250,
            "earth": 500,
        }

        return pickaxes_recharges[pick_type]

    def use(pick_type: str):
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
            "earth": 1,
        }

        return pickaxes_rates_durability[pick_type]

    def add_xp(pick_type: str):
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
            "earth": random.randint(1, 5),
        }

        exp = pickaxes_rates_xp[pick_type]
        return exp

    def check_durability(dur: int):
        """
        Checking if the pickaxe durability isn't 0.
        """
        return dur != 0

    def durability_set(pick_type: str):
        pickaxes_durabilites = {
            "wood": 100,
            "golden": 150,
            "ephemeral": 200,
            "candy": 250,
            "sky": 300,
            "nebula": 350,
            "divine": 400,
            "orc": 450,
            "earth": 500,
        }

        return pickaxes_durabilites[pick_type]

    def upgrade_pick(pick_type: str):
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
            "earth": None,
        }

        if pickaxes_upgrade[pick_type] is None:
            return False

        return pickaxes_upgrade[pick_type]

    def check_xp(pick_xp: int, pick_needed_xp: int):
        """
        XP Pickaxe checker for upgrade.
        """
        return pick_xp >= pick_needed_xp

    def emoji(pick_type: str):
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
            "earth": "<:earth_pickaxe:868209126503759992>",
        }

        return pickaxes_emoji[pick_type]

    def name(pick_type: str):
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
            "earth": "Earth Pickaxe",
        }

        return pickaxes_names[pick_type]

    def perks(pick_type: str):
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
            "earth": "<:alert_pink:867758260707000380> +10% Cupcake Drop.\n<:xp:867817838941437974> `1` > `5`.\n<:durability:867818581864218654> `1` > `1`.\n<:cupcake:845632403405012992> `500`",
        }

        return pickaxes_perks[pick_type]


class Lootbox:
    def can_drop(l_type: str):
        """
        What each lootbox can drop.
        """
        lootbox_can_drop = {
            "common": ["bronze"],
            "uncommon": ["bronze", "silver"],
            "rare": ["bronze", "silver", "gold"],
            "epic": ["bronze", "silver", "gold", "diamond"],
        }

        return lootbox_can_drop[l_type]

    def emoji(l_type: str):
        """
        Lootboxes emojis.
        """
        lootboxes = {
            "common": "<:lootbox:867758260622590002>",
            "uncommon": "<:uncommon:867764757733834793>",
            "rare": "<:rare:867764757670002698>",
            "epic": "<:epic:867764757708406824>",
        }

        return lootboxes[l_type]

    def name(l_type: str):
        """
        Lootboxes full names.
        """
        lootboxes = {
            "common": "Common Lootbox",
            "uncommon": "Uncommon Lootbox",
            "rare": "Rare Lootbox",
            "epic": "Epic Lootbox",
        }

        return lootboxes[l_type]

    def coins(l_type: str):
        """
        How many cupcakes can drop
        each lootbox.
        """
        lootboxes_drop_cupcakes = {
            "common": random.randint(100, 350),
            "uncommon": random.randint(350, 750),
            "rare": random.randint(750, 1250),
            "epic": random.randint(1250, 2500),
        }

        return lootboxes_drop_cupcakes[l_type]

    def minerals(l_type: str):
        """
        How many minerals can drop
        each lootbox.
        """
        lootboxes_drop_minerals = {
            "common": {"bronze": random.randint(1, 45)},
            "uncommon": {
                "bronze": random.randint(1, 10500),
                "silver": random.randint(1, 2000),
            },
            "rare": {
                "bronze": random.randint(1, 23000),
                "silver": random.randint(1, 7000),
                "gold": random.randint(1, 1000),
            },
            "epic": {
                "bronze": random.randint(1, 50000),
                "silver": random.randint(1, 15000),
                "gold": random.randint(1, 5000),
                "diamond": random.randint(1, 3000),
            },
        }

        return lootboxes_drop_minerals[l_type]


class Items:
    def parse_all(rar: str, item: str):
        full = {
            "common": {
                "amulet": {
                    "price": 75000,
                    "use": "+5% earning from mine (max. +50% - 10 amulets).",
                    "emoji": "<:amulet:875117133565157396>",
                },
                "dice": {
                    "price": 35000,
                    "use": "`ami dice`, check `ami help dice` for more info.",
                    "emoji": "<:dice:874968585548730398>",
                },
                "cherries": {
                    "price": 10000,
                    "use": "Highly increase critical chance in monsterhunt.",
                    "emoji": "<:cherries:874968585670369341>",
                    "uses": 50,
                },
                "bells": {
                    "price": 125000,
                    "use": "Highly increase special rate in monsterhunt.",
                    "emoji": "<:special_bells:875098746063568916>",
                    "uses": 50,
                },
                "cake": {
                    "price": 25000,
                    "use": "Increase your chances to find diamonds in mine.",
                    "emoji": "<:cake:875302049510723594>",
                    "uses": 50,
                },
                "potion": {
                    "price": 40000,
                    "use": "Highly increase chances to jail into monsterhunt.",
                    "emoji": "<:potion:875307979430305812>",
                    "uses": 50,
                },
                "drink": {
                    "price": 20000,
                    "use": "Highly increase your chances to land criticals in battles.",
                    "emoji": "<:drink:875307978679550003>",
                    "uses": 50,
                },
            },
            "vote": {
                "lucky block": {
                    "rate": "1/1,250",
                    "use": "`ami open lb`, check `ami help open lb` for more info.",
                    "emoji": "<:lucky_block:874968585267712091>",
                },
                "golden cupcake": {
                    "rate": "1/1",
                    "use": "Each golden cupcakes will give one level to your teammate.",
                    "emoji": "<:golden_cupcake:874968585833967676>",
                },
                "antic book": {
                    "rate": "1/3,500",
                    "use": "Instant prestige your teammate.",
                    "emoji": "<:antic_book:875302049389088819>",
                },
            },
        }

        return full[rar][item]


class Cuppy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.in_captcha = {}
        self.captcha_failed = {}
        self.fails.start()

    def cog_unload(self):
        self.fails.stop()

    async def captcha(self, ctx, user: discord.Member):
        """
        This is actually a thing that i needed forcely to
        do, people can easly log as a selfbots and start
        spamming commands to earn, then we handle it with
        this captcha system, which every 50 cuppy commands
        is invoked and it will bl the user from the bot
        permanently if the user fails the captcha.
        """

        self.in_captcha[user.id] = True
        image = ImageCaptcha(
            fonts=["fonts/standard.ttf", "fonts/mitalic.ttf"]
        )
        number = random.randint(1000, 99999)
        data = image.generate(str(number))
        buffer = BytesIO()
        image.write(str(number), buffer)
        buffer.seek(0)
        file = discord.File(fp=buffer, filename="captcha.png")

        time = random.randint(60, 180)

        await ctx.send(
            f"{user.mention} please solve the **captcha** above by sending the right numbers to continue playing cuppy."
            f" You have **{humanize.precisedelta(time)}**. No reply from the bot means you are __incorrect__, please join the support server (`ami support`) if you need help with the captcha!\n"
            "If you exceed the timeout limit, you will receive an **in-game ban** and a **bot ban** (the ban is temporary and the time is totally random.).",
            file=file,
        )

        while True:
            try:
                mex = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author.id == user.id
                    and m.channel.id == ctx.channel.id
                    and m.content == str(number),
                    timeout=time,
                )
            except asyncio.TimeoutError:
                await ctx.send(
                    f"<:4318crossmark:848857812565229601> {user.mention} you exceed the timeout limit from the captcha, you are now temporary banned from the bot."
                )
                self.captcha_failed[user.id] = "Failed solving the cuppy captcha."
                del self.in_captcha[user.id]
                break

            if mex.content == str(number):
                await ctx.send(
                    f"<:4430checkmark:848857812632076314> {user.mention} thanks, you may continue playing cuppy!"
                )
                del self.in_captcha[user.id]
                break

    async def cog_check(self, ctx):
        if ctx.author.id in self.in_captcha.keys():
            return False

        if ctx.author.id in self.captcha_failed.keys():
            await ctx.send(
                f"{ctx.author.mention} you are temporary banned from using the bot, try again later."
            )
            return False

        s = random.randint(1, 100)
        if s == 1:
            await self.captcha(ctx, ctx.author)
            return False

        return True

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cuppy Loaded")

    @commands.command()
    @is_team()
    async def checkcuppy_bl(
        self, ctx, member: typing.Union[discord.Member, discord.User, str]
    ):
        if member.id in self.captcha_failed:
            await ctx.send(f"{self.captcha_failed[member.id]}")
        else:
            await ctx.send(f"{member.id} ({member.name}) not banned.")

    @tasks.loop(hours=12)
    async def fails(self):
        if len(self.captcha_failed) < 1:
            return

        for k in self.captcha_failed.keys():
            del self.captcha_failed[k]

    @commands.command(help="Link for the top.gg vote page")
    async def vote(self, ctx):
        em = discord.Embed(
            description=f"Votes are connected to cuppy, voting you will get awesome rewards, like:\n<:golden_cupcake:874968585833967676>, <:lucky_block:874968585267712091>, <:antic_book:875302049389088819>, {Lootbox.emoji('common')}, {Lootbox.emoji('uncommon')}, {Lootbox.emoji('rare')}, {Lootbox.emoji('epic')}\nYou can check `ami checklist` to check time before your next vote.\n\nhttps://amibot.gg/vote",
            color=0xFFCFF1,
        )
        em.set_footer(
            text="Remember to leave your DM's open to see what you've got from the vote!"
        )
        em.set_author(name="Vote to get rewards!", icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=em)

    @commands.command(aliases=["inv"], help="Check your inventory and your items.")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def inventory(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        balance = data[0]["balance"]
        common = data[0]["lootbox_common"]
        uncommon = data[0]["lootbox_uncommon"]
        rare = data[0]["lootbox_rare"]
        epic = data[0]["lootbox_epic"]
        bronze = data[0]["bronze"]
        silver = data[0]["silver"]
        gold = data[0]["gold"]
        diamond = data[0]["diamond"]
        amulet = data[0]["amulet"]
        dice = data[0]["dice"]
        cherries = data[0]["cherries"]
        bells = data[0]["bells"]
        lucky_blocks = data[0]["lucky_blocks"]
        golden_cups = data[0]["golden_cups"]
        cake = data[0]["cake"]
        potion = data[0]["potion"]
        drink = data[0]["drink"]
        antic_book = data[0]["antic_books"]

        await ctx.send(
            embed=discord.Embed(
                color=self.bot.color, timestamp=datetime.datetime.utcnow()
            )
            .add_field(
                name="Currencies",
                value=f"<:cupcake:845632403405012992> **{humanize.intcomma(balance)}** Cupcakes\n<:golden_cupcake:874968585833967676> **{humanize.intcomma(golden_cups)}** Golden Cupcakes",
            )
            .add_field(
                name="Boxes",
                value=f"{Lootbox.emoji('common')} **{humanize.intcomma(common)}**x Common\n{Lootbox.emoji('uncommon')} **{humanize.intcomma(uncommon)}**x Uncommon\n"
                f"{Lootbox.emoji('rare')} **{humanize.intcomma(rare)}**x Rare\n{Lootbox.emoji('epic')} **{humanize.intcomma(epic)}**x Epic",
                inline=False,
            )
            .add_field(
                name="Items",
                value=f"{Items.parse_all('common', 'amulet')['emoji']} **{amulet}**x Amulets [`+{5*data[0]['amulet'] if data[0]['amulet'] >= 1 else 0}%`]\n{Items.parse_all('common', 'dice')['emoji']} **{dice}**x Dices\n"
                f"{Items.parse_all('common', 'cherries')['emoji']} **{cherries}**x Cherries [`{humanize.intcomma(data[0]['cherries_uses']) or ' '}`]\n{Items.parse_all('common', 'bells')['emoji']} **{bells}**x Bells [`{humanize.intcomma(data[0]['bells_uses']) or ' '}`]\n"
                f"{Items.parse_all('common', 'cake')['emoji']} **{cake}**x Cakes [`{humanize.intcomma(data[0]['cake_uses']) or ' '}`]\n{Items.parse_all('common', 'potion')['emoji']} **{potion}**x Potions [`{humanize.intcomma(data[0]['potion_uses']) or ' '}`]\n{Items.parse_all('common', 'drink')['emoji']} **{drink}**x Drinks [`{humanize.intcomma(data[0]['drink_uses']) or ' '}`]\n"
                f"{Items.parse_all('vote', 'lucky block')['emoji']} **{lucky_blocks}**x Lucky Blocks\n{Items.parse_all('vote', 'antic book')['emoji']} **{antic_book}**x Antic Books",
            )
            .add_field(
                name="Minerals",
                value=f"{Mineral.emoji('bronze')} **{humanize.intcomma(bronze)}**x Bronze\n{Mineral.emoji('silver')} **{humanize.intcomma(silver)}**x Silver\n{Mineral.emoji('gold')} **{humanize.intcomma(gold)}**x Gold\n{Mineral.emoji('diamond')} **{humanize.intcomma(diamond)}**x Diamonds",
                inline=True,
            )
            .set_footer(text="Type a;vote to get more rewards!")
            .set_author(
                name=f"{ctx.author.name}'s inventory", icon_url=ctx.author.avatar_url
            )
        )

    @commands.group(
        name="shop",
        aliases=["s", "sh"],
        help="Items shop, where you can buy useful stuff.",
        invoke_without_command=True,
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def items_shop(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        items = ["amulet", "dice", "cherries", "bells", "potion", "drink", "cake"]

        c_l = []

        for i in items:
            f = Items.parse_all("common", i)
            c_l.append(
                f"{f['emoji']} **{i.title()}** (<:cupcake:845632403405012992> `{humanize.intcomma(f['price'])}`)\n{f['use']}\n"
            )

        f_c_l = "\n".join(c_l)

        await ctx.send(
            embed=discord.Embed(
                description="`ami shop buy <item> [amount]` to buy something from the shop.\n\n"
                f"{f_c_l}",
                color=self.bot.color,
            ).set_author(name="Items Shop", icon_url=self.bot.user.avatar_url)
        ) or await ctx.invoke(**{"command": "items_shop"})

    @commands.command(help="Use items from your inventory to get power-ups into monsterhunt/mine & others!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def use(self, ctx, item, amount = None):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        valid_items = ["dice", "cherries", "bells", "potion", "drink", "cake"]

        if item.lower() in ["amulet", "amulets"]:
            return await ctx.send(
                f"{ctx.author.mention} the <:amulet:875117133565157396> **{item.title()}** is not an usable item."
            )

        if item.lower() not in valid_items:
            return await ctx.send(
                f"{ctx.author.mention} **{item}** is not a valid item, maybe a typo?"
            )

        if amount is None:
            amount = 1

        elif amount.lower() == "all":
            amount = data[0][item.lower()]

        parsed = Items.parse_all("common", item.lower())
        emoji = parsed["emoji"]
        try:
            uses = parsed["uses"] * amount
        except KeyError:
            uses = None
        usage = parsed["use"]

        if not uses:
            return await ctx.send(
                f"{ctx.author.mention} {emoji} **{item.title()}** is not an usable item."
            )

        if amount != 'all':
            if amount > data[0][f"{item.lower()}"]:
                return await ctx.send(
                    f"{ctx.author.mention} you have {emoji} **{data[0][f'{item.lower()}']}x {item.title()}**, buy some others to can use them."
                )

        await self.bot.db.execute(
            f"UPDATE cuppy SET {item.lower()} = $1, {item.lower()}_uses = $2 WHERE user_id = $3",
            data[0][f"{item.lower()}"] - amount,
            data[0][f"{item.lower()}_uses"] + uses,
            ctx.author.id,
        )
        await ctx.send(
            f"{ctx.author.mention} you've activated {emoji} {amount}x **{item.title()}** for **{uses}x** uses!\nPerk: {usage}"
        )

    @commands.command(
        name="goldencup",
        aliases=["gc"],
        help="Use your golden cupcakes to give levels to your teammates!",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def golden_cupcake(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        if data[0]["golden_cups"] < 1:
            return await ctx.send(
                f"{ctx.author.mention} you have no {Items.parse_all('vote', 'golden cupcake')['emoji']} **Golden Cupcakes** to use."
            )

        team = data[0]["team_name"]
        if not team:
            return await ctx.send(f"{ctx.author.mention} you don't have a teammate.")

        await self.bot.db.execute(
            "UPDATE cuppy SET team_level = $1, team_xp = $2, golden_cups = $3 WHERE user_id = $4",
            data[0]["team_level"] + 1 * data[0]["golden_cups"],
            0,
            0,
            ctx.author.id,
        )
        await ctx.send(
            f"{ctx.author.mention} you used {Items.parse_all('vote', 'golden cupcake')['emoji']} {data[0]['golden_cups']}x **Golden Cupcake** and gave **+{1*data[0]['golden_cups']}** levels to your {Team.emoji(data[0]['team_name'])} **{Team.name(data[0]['team_name'])}**!"
        )

    @commands.command(
        name="anticbook",
        aliases=["ab"],
        help="Use your antic books to prestige your teammate!",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def antic_book(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        if data[0]["antic_books"] < 1:
            return await ctx.send(
                f"{ctx.author.mention} you have no {Items.parse_all('vote', 'antic book')['emoji']} **Antic Books** to use."
            )

        team = data[0]["team_name"]
        if not team:
            return await ctx.send(f"{ctx.author.mention} you don't have a teammate.")

        team = data[0]["team_name"]
        if team.endswith("(prestiged)"):
            return await ctx.send(
                f"{ctx.author.mention} your teammate is already prestiged."
            )

        await self.bot.db.execute(
            "UPDATE cuppy SET team_name = $1, team_xp = $2, antic_books = $3, team_level = $4 WHERE user_id = $5",
            data[0]["team_name"] + " (prestiged)",
            0,
            data[0]["antic_books"] - 1,
            1,
            ctx.author.id,
        )
        await ctx.send(
            f"{ctx.author.mention} you used {Items.parse_all('vote', 'antic book')['emoji']} **Antic Book** and prestiged your {Team.emoji(data[0]['team_name'])} **{Team.name(data[0]['team_name'])}**!"
        )

    @items_shop.command(help="Buy items from the items shop using your cupcakes")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def buy(self, ctx, item, amount=1):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        valid_items = ["amulet", "dice", "cherries", "bells", "potion", "drink", "cake"]

        if item.lower() not in valid_items:
            return await ctx.send(
                f"{ctx.author.mention} **{item}** is not a valid item, maybe a typo?"
            )

        parsed = Items.parse_all("common", item.lower())
        price = parsed["price"] * amount
        emoji = parsed["emoji"]

        if item.lower() == "amulet":
            if data[0]["amulet"] == 10:
                return await ctx.send(
                    f"{ctx.author.mention} you have reached the maximum amulet amount (10), you can't buy more amulets."
                )

        if price > data[0]["balance"]:
            return await ctx.send(
                f"{ctx.author.mention} {emoji} **{item.title()}** cost is <:cupcake:845632403405012992> **{humanize.intcomma(price)}**, you have only <:cupcake:845632403405012992> **{humanize.intcomma(data[0]['balance'])}**"
            )

        await self.bot.db.execute(
            f"UPDATE cuppy SET {item.lower()} = $1, balance = $2 WHERE user_id = $3",
            data[0][f"{item.lower()}"] + amount,
            data[0]["balance"] - price,
            ctx.author.id,
        )
        await ctx.send(
            f"{ctx.author.mention} you've succesfully bought {emoji} {amount}x **{item.title()}** for <:cupcake:845632403405012992> **{humanize.intcomma(price)}**!"
        )

    @commands.group(
        aliases=["xpr"],
        help="The XP-Room is a place where your teammate can grind xp automatically! Start the xp room to make your teammate earns xp by itself!\nUpgrading the stats of your XP-Room will make the duration longer, lower cost and in consequence more xp earned for your teammate!",
        invoke_without_command=True,
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def xproom(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        xp_room_cost_level = data[0]["xp_room_cost_level"]
        xp_room_duration_level = data[0]["xp_room_duration_level"]
        xp_room_farm_level = data[0]["xp_room_farm_level"]

        if data[0]["xp_room_date"]:
            tit = "✅ Your XP-Room is currently running!"
        else:
            tit = "❌ Your XP-Room is not running!"

        if (
            data[0]["xp_room_date"]
            and datetime.datetime.utcnow() > data[0]["xp_room_date"]
        ):
            tit = "🎉 Your XP-Room has finished: `ami xpr claim`!"

        cost_upgrade = "⚡**`MAX LEVEL`**⚡"
        farm_upgrade = "⚡**`MAX LEVEL`**⚡"
        duration_upgrade = "⚡**`MAX LEVEL`**⚡"

        if xp_room_cost_level < 10:
            cost_upgrade = f"`Next Level:` <:cupcake:845632403405012992> `{humanize.intcomma(XpRoom.parse_upgrade('cost', xp_room_cost_level+1))}`"

        if xp_room_farm_level < 10:
            farm_upgrade = f"`Next Level:` <:cupcake:845632403405012992> `{humanize.intcomma(XpRoom.parse_upgrade('farm', xp_room_farm_level+1))}`"

        if xp_room_duration_level < 10:
            duration_upgrade = f"`Next Level:` <:cupcake:845632403405012992> `{humanize.intcomma(XpRoom.parse_upgrade('duration', xp_room_duration_level+1))}`"

        await ctx.send(
            embed=discord.Embed(
                title=tit,
                description=f"`a;xpr run` to run your 🏹 **XP-Room** at his maximum.\n"
                f"`a;xpr upgrade <stats>` to upgrade one of your 🏹 **XP-Room** stats.\n"
                f"__When your 🏹 **XP-Room** is running, you can't battle or hunt monsters__",
                color=self.bot.color,
            )
            .add_field(
                name=f"💰 Cost | `{humanize.intcomma(XpRoom.cost_parser(data[0]['xp_room_cost_level'], XpRoom.time_parser(xp_room_duration_level)))}`",
                value=f"<:alert_pink:867758260707000380>`Level {data[0]['xp_room_cost_level']} / 10`\n{cost_upgrade}",
            )
            .add_field(
                name=f"⚙ Farm | `{millify(XpRoom.farm_parser(data[0]['xp_room_farm_level'])[0])} - {millify(XpRoom.farm_parser(data[0]['xp_room_farm_level'])[len(XpRoom.farm_parser(data[0]['xp_room_farm_level']))-1])} EXP`",
                value=f"<:alert_pink:867758260707000380>`Level {data[0]['xp_room_farm_level']} / 10`\n{farm_upgrade}",
            )
            .add_field(
                name=f"⏱ Duration | `{XpRoom.time_parser(data[0]['xp_room_duration_level'])}H`",
                value=f"<:alert_pink:867758260707000380>`Level {data[0]['xp_room_duration_level']} / 10`\n{duration_upgrade}",
            )
            .add_field(
                name=f"<:cupcake:845632403405012992> You currently have {humanize.intcomma(data[0]['balance'])} Cupcakes!",
                value=f"`Your 🏹 XP-Farm can run for {XpRoom.time_parser(data[0]['xp_room_duration_level'])}H earning maximum {millify(XpRoom.farm_parser(data[0]['xp_room_farm_level'])[len(XpRoom.farm_parser(data[0]['xp_room_farm_level']))-1])} EXP at the cost of {humanize.intcomma(XpRoom.cost_parser(data[0]['xp_room_cost_level'], XpRoom.time_parser(xp_room_duration_level)))} Cupcakes!`",
            )
            .set_author(
                name=f"{ctx.author.name}'s XP-Room Info",
                icon_url=self.bot.user.avatar_url,
            )
            .set_footer(
                text='Check "ami checklist" to see when your XP-Room has ended.'
            )
        ) or await ctx.invoke(**{"command": "xproom"})

    @xproom.command(help="Run your XP-Room")
    async def run(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        if data[0]["team_name"] is None:
            return await ctx.send(
                f"{ctx.author.mention} you don't have a teammate, check `ami team shop`!"
            )

        if data[0]["xp_room_date"]:
            return await ctx.send(
                f"{ctx.author.mention} your 🏹 **XP-Room** is already running."
            )

        if (
            data[0]["xp_room_date"]
            and datetime.datetime.utcnow() < data[0]["xp_room_date"]
        ):
            return await ctx.send(
                f"{ctx.author.mention} your 🏹 **XP-Room** is not ended yet, try again later."
            )

        time = data[0]["xp_room_duration_level"]
        cost = data[0]["xp_room_cost_level"]
        final_time = XpRoom.time_parser(time)

        actual = datetime.datetime.utcnow()
        future = actual + datetime.timedelta(hours=final_time)

        payout = XpRoom.cost_parser(cost, final_time)

        if payout > data[0]["balance"]:
            return await ctx.send(
                f"{ctx.author.mention} your 🏹 **XP-Room** can run for <:cupcake:845632403405012992> **{humanize.intcomma(payout)}**, you have only <:cupcake:845632403405012992> **{humanize.intcomma(data[0]['balance'])}**"
            )

        image = ImageCaptcha(fonts=["fonts/standard.ttf"])
        number = random.randint(1000, 99999)
        file_data = image.generate(str(number))
        buffer = BytesIO()
        image.write(str(number), buffer)
        buffer.seek(0)
        file = discord.File(fp=buffer, filename="captcha.png")

        timer = 60

        me = await ctx.send(
            f"{ctx.author.mention} please solve the captcha to run your 🏹 **XP-Room**: you have 1 minute.",
            file=file,
        )

        try:
            mex = await self.bot.wait_for(
                "message",
                check=lambda m: m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id
                and m.content == str(number),
                timeout=timer,
            )
        except asyncio.TimeoutError:
            await me.delete()
            return

        if mex.content == str(number):
            await self.bot.db.execute(
                "UPDATE cuppy SET balance = $1, xp_room_date = $2 WHERE user_id = $3",
                data[0]["balance"] - payout,
                future,
                ctx.author.id,
            )
            return await ctx.send(
                f"{ctx.author.mention} you've spent <:cupcake:845632403405012992> **{humanize.intcomma(payout)}** to run your 🏹 **XP-Room**, it will be back in ⏱ **{final_time}H**!"
            )

    @xproom.command(help="Claim the rewards from the XP-Room when it ends.")
    async def claim(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        if data[0]["team_name"] is None:
            return await ctx.send(
                f"{ctx.author.mention} you don't have a teammate, check `ami team shop`!"
            )

        if not data[0]["xp_room_date"]:
            return await ctx.send(
                f"{ctx.author.mention} your 🏹 **XP-Room** is not running, run it with `ami xpr run`."
            )

        if (
            data[0]["xp_room_date"]
            and datetime.datetime.utcnow() < data[0]["xp_room_date"]
        ):
            return await ctx.send(
                f"{ctx.author.mention} your 🏹 **XP-Room** is not ended yet, try again later."
            )

        earns = random.choice(XpRoom.farm_parser(data[0]['xp_room_farm_level']))

        name = Team.name(data[0]["team_name"])
        emoji = Team.emoji(data[0]["team_name"])

        await self.bot.db.execute(
            "UPDATE cuppy SET xp_room_date = $1, team_xp = $2 WHERE user_id = $3",
            None,
            data[0]["team_xp"] + earns,
            ctx.author.id,
        )
        mexx = f"🎉 Your {emoji} **{name}** returned with <:xp:867817838941437974> **+ {humanize.intcomma(earns)}**!"
        if (data[0]["team_xp"] + earns) >= Team.calc_needed_xp(
            data[0]["team_level"], data[0]["team_name"]
        ):
            await self.bot.db.execute(
                "UPDATE cuppy SET team_level = $1, team_xp = $2 WHERE user_id = $3",
                data[0]["team_level"] + 1,
                0,
                ctx.author.id,
            )
            mexx += f"\n‼ Oh! Your {emoji} **{name}** leveled up to level **{humanize.intcomma(data[0]['team_level'] + 1)}**!"

        await ctx.send(
            embed=discord.Embed(
                title="🏹 XP-Room Claimed!", description=f"{mexx}", color=self.bot.color
            )
            .set_footer(text='Run your XP-Room again with "a;xpr run"!')
            .set_author(
                name=f"{ctx.author.name}'s XP-Room", icon_url=self.bot.user.avatar_url
            )
        )

    @xproom.command(
        help="Upgrade the stats of your XP-Room to gain more xp.", name="upgrade"
    )
    async def upgrade_xpr(self, ctx, stat: str):
        valids = ["farm", "cost", "duration"]
        if stat.lower() not in valids:
            return await ctx.send(
                f"{ctx.author.mention} **{stat}** is not a valid stat to upgrade for the 🏹 **XP-Room**."
            )

        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        if data[0]["team_name"] is None:
            return await ctx.send(
                f"{ctx.author.mention} you don't have a teammate, check `ami team shop`!"
            )

        if (
            data[0]["xp_room_date"]
            and datetime.datetime.utcnow() < data[0]["xp_room_date"]
        ):
            return await ctx.send(
                f"{ctx.author.mention} your 🏹 **XP-Room** is not ended yet, you can't upgrade while it's running."
            )

        if data[0]["xp_room_date"]:
            return await ctx.send(
                f"{ctx.author.mention} your 🏹 **XP-Room** is ended, please claim it before upgrade."
            )

        upf = data[0][f"xp_room_{stat.lower()}_level"]
        if upf == 10:
            return await ctx.send(
                f"{ctx.author.mention} your 🏹 **XP-Room** `{stat.lower()}` is already at the maximum level, you can't upgrade it anymore."
            )

        up = XpRoom.parse_upgrade(stat.lower(), upf + 1)

        if up > data[0]["balance"]:
            return await ctx.send(
                f"{ctx.author.mention}, **{stat.lower()}** upgrade price is <:cupcake:845632403405012992> **{humanize.intcomma(up)}** and you have only <:cupcake:845632403405012992> **{humanize.intcomma(data[0]['balance'])}**"
            )

        await self.bot.db.execute(
            f"UPDATE cuppy SET xp_room_{stat.lower()}_level = $1, balance = $2 WHERE user_id = $3",
            upf + 1,
            data[0]["balance"] - up,
            ctx.author.id,
        )
        await ctx.send(
            f"{ctx.author.mention} you've spent <:cupcake:845632403405012992> **{humanize.intcomma(up)}** to upgrade your 🏹 **XP-Room** `{stat.lower()}`, which now is Lvl. **{upf + 1}**!"
        )

    @commands.command(help="Claim your daily cupcakes gift!")
    async def daily(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        if data[0]["daily_date"]:
            if datetime.datetime.utcnow() < data[0]["daily_date"]:
                return await ctx.send(
                    f"{ctx.author.mention} your daily reward is not ready yet, take a look on the checklist to know when it's ready."
                )

        actual = datetime.datetime.utcnow()
        future = actual + datetime.timedelta(hours=24)

        c = 500
        await self.bot.db.execute(
            "UPDATE cuppy SET balance = $1, daily_date = $2 WHERE user_id = $3",
            data[0]["balance"] + c,
            future,
            ctx.author.id,
        )
        data2 = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )

        time = data2[0]["daily_date"] - datetime.datetime.utcnow()
        await ctx.send(
            f"<:alert_pink:867758260707000380> {ctx.author.mention} you got <:cupcake:845632403405012992> **{c}** from your daily reward!\n<:alert_pink:867758260707000380> You can claim the next one in **{humanize.precisedelta(time.seconds)}**."
        )

    @commands.command(help="Claim your weekly cupcakes gift!")
    async def weekly(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        if data[0]["weekly_date"]:
            if datetime.datetime.utcnow() < data[0]["weekly_date"]:
                return await ctx.send(
                    f"{ctx.author.mention} your weekly reward is not ready yet, take a look on the checklist to know when it's ready."
                )

        actual = datetime.datetime.utcnow()
        future = actual + datetime.timedelta(days=7)

        c = 3500
        await self.bot.db.execute(
            "UPDATE cuppy SET balance = $1, weekly_date = $2 WHERE user_id = $3",
            data[0]["balance"] + c,
            future,
            ctx.author.id,
        )

        data2 = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )

        time2 = data2[0]["weekly_date"] - datetime.datetime.utcnow()
        await ctx.send(
            f"<:alert_pink:867758260707000380> {ctx.author.mention} you got <:cupcake:845632403405012992> **{c}** from your weekly reward!\n<:alert_pink:867758260707000380> You can claim the next one in **{time2.days} day(s), {humanize.precisedelta(time2.seconds)}**."
        )

    @commands.command(help="Claim your monthly cupcakes gift!")
    async def monthly(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        if data[0]["monthly_date"]:
            if datetime.datetime.utcnow() < data[0]["monthly_date"]:
                return await ctx.send(
                    f"{ctx.author.mention} your monthly reward is not ready yet, take a look on the checklist to know when it's ready."
                )

        actual = datetime.datetime.utcnow()
        future = actual + datetime.timedelta(days=31)

        c = 15000
        await self.bot.db.execute(
            "UPDATE cuppy SET balance = $1, monthly_date = $2 WHERE user_id = $3",
            data[0]["balance"] + c,
            future,
            ctx.author.id,
        )

        data2 = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )

        time2 = data2[0]["monthly_date"] - datetime.datetime.utcnow()
        await ctx.send(
            f"<:alert_pink:867758260707000380> {ctx.author.mention} you got <:cupcake:845632403405012992> **{c}** from your monthly reward!\n<:alert_pink:867758260707000380> You can claim the next one in **{time2.days} day(s), {humanize.precisedelta(time2.seconds)}**."
        )

    @commands.command(
        help="That's you checklist, you can check here times before you can get the next rewards!",
        aliases=["cl"],
    )
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def checklist(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        daily = data[0]["daily_date"]
        weekly = data[0]["weekly_date"]
        monthly = data[0]["monthly_date"]
        vote = data[0]["vote_date"]
        xprs = data[0]["xp_room_date"]

        daily_mex = ""
        weekly_mex = ""
        monthly_mex = ""
        vote_mex = ""
        xprs_mex = ""

        if not xprs:
            xprs_mex = "is **ready**!"
            xtick = "✅"
        else:
            if datetime.datetime.utcnow() > xprs:
                xprs_mex = "is **ready**!"
                xtick = "✅"
            else:
                x_final_date = xprs - datetime.datetime.utcnow()
                b = humanize.precisedelta(x_final_date.seconds).replace(" hours,", "H")
                b = b.replace(" hour,", "H")
                b = b.replace(" hour and", "H")
                b = b.replace(" minutes and", "M")
                b = b.replace(" seconds", "S")
                b = b.replace(" months,", "MO")
                b = b.replace(" minute and", "M")
                b = b.replace(" second", "S")
                b = b.replace(" month,", "MO")
                xprs_mex = f"will be back in **{b}**!"
                xtick = ":black_medium_square:"

        if not daily:
            daily_mex = "is **ready**!"
            dtick = "✅"
        else:
            if datetime.datetime.utcnow() > daily:
                daily_mex = "is **ready**!"
                dtick = "✅"
            else:
                d_final_date = daily - datetime.datetime.utcnow()
                b = humanize.precisedelta(d_final_date.seconds).replace(" hours,", "H")
                b = b.replace(" hour,", "H")
                b = b.replace(" hour and", "H")
                b = b.replace(" hours and", "H")
                b = b.replace(" minutes and", "M")
                b = b.replace(" seconds", "S")
                b = b.replace(" months,", "MO")
                b = b.replace(" minute and", "M")
                b = b.replace(" second", "S")
                b = b.replace(" month,", "MO")
                daily_mex = f"is in **{b}**!"
                dtick = ":black_medium_square:"

        if not weekly:
            weekly_mex = "is **ready**!"
            wtick = "✅"
        else:
            if datetime.datetime.utcnow() > weekly:
                weekly_mex = "is **ready**!"
                wtick = "✅"
            else:
                w_final_date = weekly - datetime.datetime.utcnow()
                b = humanize.precisedelta(w_final_date.seconds).replace(" hours,", "H")
                b = b.replace(" hour,", "H")
                b = b.replace(" hour and", "H")
                b = b.replace(" minutes and", "M")
                b = b.replace(" seconds", "S")
                b = b.replace(" months,", "MO")
                b = b.replace(" minute and", "M")
                b = b.replace(" second", "S")
                b = b.replace(" month,", "MO")
                if w_final_date.days:
                    weekly_mex = f"is in **{w_final_date.days}D {b}**!"
                else:
                    weekly_mex = f"is in **{b}**!"
                wtick = ":black_medium_square:"

        if not monthly:
            monthly_mex = "is **ready**!"
            mtick = "✅"
        else:
            if datetime.datetime.utcnow() > monthly:
                monthly_mex = "is **ready**!"
                mtick = "✅"
            else:
                m_final_date = monthly - datetime.datetime.utcnow()
                b = humanize.precisedelta(m_final_date.seconds).replace(" hours,", "H")
                b = b.replace(" hour,", "H")
                b = b.replace(" hour and", "H")
                b = b.replace(" minutes and", "M")
                b = b.replace(" seconds", "S")
                b = b.replace(" months,", "MO")
                b = b.replace(" minute and", "M")
                b = b.replace(" second", "S")
                b = b.replace(" month,", "MO")
                if m_final_date.days:
                    monthly_mex = f"is in **{m_final_date.days}D {b}**!"
                else:
                    monthly_mex = f"is in **{b}**!"
                mtick = ":black_medium_square:"

        if not vote:
            vote_mex = "is **ready**!"
            vtick = "✅"
        else:
            if datetime.datetime.utcnow() > vote:
                vote_mex = "is **ready**!"
                vtick = "✅"
            else:
                v_final_date = vote - datetime.datetime.utcnow()
                b = humanize.precisedelta(v_final_date.seconds).replace(" hours,", "H")
                b = b.replace(" hour,", "H")
                b = b.replace(" hour and", "H")
                b = b.replace(" minutes and", "M")
                b = b.replace(" seconds", "S")
                b = b.replace(" months,", "MO")
                b = b.replace(" minute and", "M")
                b = b.replace(" second", "S")
                b = b.replace(" month,", "MO")
                vote_mex = f"is in **{b}**!"
                vtick = ":black_medium_square:"

        await ctx.send(
            embed=discord.Embed(
                title="Your Checklist",
                description=f"{xtick} 🏹 Your XP-Room {xprs_mex}\n{dtick} 🎁 Your next daily {daily_mex}\n"
                f"{wtick} ⏱ Your next weekly {weekly_mex}\n{mtick} 📆 Your next monthly {monthly_mex}\n"
                f"{vtick} 🎟 Your next vote {vote_mex}\n\n`a;vote`, `a;daily`, `a;weekly`, `a;monthly`, `a;xpr`",
                color=self.bot.color,
                timestamp=datetime.datetime.utcnow(),
            )
            .set_author(
                name=f"{ctx.author.name}'s Checklist", icon_url=self.bot.user.avatar_url
            )
            .set_footer(text="Ami 2021"),
        )

    @commands.command(
        help="Take a look on how many lootboxes you have in your inventory.",
        aliases=["boxinv", "bi"],
    )
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def boxinventory(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        common = data[0]["lootbox_common"]
        uncommon = data[0]["lootbox_uncommon"]
        rare = data[0]["lootbox_rare"]
        epic = data[0]["lootbox_epic"]

        await ctx.send(
            f"{ctx.author.mention} you currently have {Lootbox.emoji('common')} {common}x "
            f"{Lootbox.emoji('uncommon')} {uncommon}x {Lootbox.emoji('rare')} {rare}x {Lootbox.emoji('epic')} {epic}x"
        )

    @commands.command(
        help="Check the global leaderboard about users or clans, you can pass `ami leaderboard clans` to see clans or just `ami leaderboard` to see users!",
        aliases=["lb"],
    )
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def leaderboard(self, ctx, types: str = None):
        if types is None:
            types = "users"

        d = ["players", "users", "clans", "clan"]
        if types:
            if types not in d:
                return await ctx.send(
                    f"{ctx.author.mention} you've passed an invalid leaderboard type."
                )

        if types in ["users", "players"]:
            user = await self.bot.db.fetch(
                "SELECT *, RANK() OVER (ORDER BY balance DESC) FROM cuppy LIMIT $1", 10
            )
            names = []
            bals = []
            for i in user:
                users = self.bot.get_user(i["user_id"]) or (
                    await self.bot.fetch_user(i["user_id"])
                )
                bal = i["balance"]
                if ctx.author.id == i["user_id"]:
                    names.append(
                        f"{i['rank']}. **{users.name}#{users.discriminator}**"
                    )
                else:
                    names.append(f"{i['rank']}. {users.name}#{users.discriminator}")
                bals.append(f"<:cupcake:845632403405012992> {humanize.intcomma(bal)}")

            return await ctx.send(
                embed=discord.Embed(
                    description=f"Cuppy leaderboard about __{types}__!",
                    color=self.bot.color,
                )
                .add_field(name=f"📕 {types.title()}", value="\n".join(names))
                .add_field(name="📕 Balance", value="\n".join(bals))
                .set_author(
                    name="Ami Cuppy Leaderboard", icon_url=self.bot.user.avatar_url
                )
                .set_thumbnail(url=self.bot.user.avatar_url)
                .set_footer(
                    text="The leaderboard is sent in real-time, no delay on new balances / clans xp."
                )
            )

        elif types in ["clans", "clan"]:
            user = await self.bot.db.fetch(
                "SELECT *, RANK() OVER (ORDER BY clan_xp DESC) FROM clans LIMIT $1", 10
            )
            clan_names = []
            clan_exps = []
            clan_leagues = []
            for i in user:
                name = i["clan_name"]
                league = i["clan_league"]
                xp = i["clan_xp"]
                members = i["clan_members"]
                clan_names.append(
                    f"{i['rank']}. {name} (👥 {members} / {Clan.max_members(league)})"
                )
                clan_exps.append(f"{humanize.intcomma(xp)}")
                clan_leagues.append(
                    f"{Clan.league_emoji(league)} {Clan.league_name(league)}"
                )

            return await ctx.send(
                embed=discord.Embed(
                    description=f"Cuppy leaderboard about __{types}__!",
                    color=self.bot.color,
                )
                .add_field(name=f"📕 {types.title()}", value="\n".join(clan_names))
                .add_field(name="📕 EXP", value="\n".join(clan_exps))
                .add_field(name="📕 League", value="\n".join(clan_leagues))
                .set_author(
                    name="Ami Cuppy Leaderboard", icon_url=self.bot.user.avatar_url
                )
                .set_thumbnail(url=self.bot.user.avatar_url)
                .set_footer(
                    text="The leaderboard is sent in real-time, no delay on new balances / clans xp."
                )
            )

    @commands.group(
        aliases=["min"],
        help="Check your minerals, see minerals exchange values.",
        invoke_without_command=True,
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def minerals(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command": "minerals"})

    @minerals.command(
        name="inventory", help="Check you minerals in your inventory", aliases=["inv"]
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def min_inventory(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        bronze = data[0]["bronze"]
        silver = data[0]["silver"]
        gold = data[0]["gold"]
        diamond = data[0]["diamond"]

        await ctx.send(
            f"{ctx.author.mention} you currently have "
            f"{Mineral.emoji('bronze')} {bronze}x "
            f"{Mineral.emoji('silver')} {silver}x "
            f"{Mineral.emoji('gold')} {gold}x "
            f"{Mineral.emoji('diamond')} {diamond}x "
        )

    @minerals.command(
        help="Check what are the minimun amount for each mineral to make an exchange.",
        aliases=["val"],
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def values(self, ctx):

        mines = ["bronze", "silver", "gold", "diamond"]

        cv = []

        for i in mines:
            name = Mineral.name(i)
            emoji = Mineral.emoji(i)
            exc = Exchange.exc_info(i)
            cv.append(
                f"`{exc}x` {emoji} **{name}** × <:cupcake:845632403405012992> **1**"
            )

        c = "\n".join(cv)
        await ctx.send(
            embed=discord.Embed(
                title="Minerals Values",
                description=f"Listed you can see all the values according to the mineral type"
                f" for exchanges.\nE.g : if you trade `250` bronze, you will get 1 cupcake!\n\n{c}",
                color=self.bot.color,
            )
        )

    @commands.command(
        help="Some info about you, your cuppy stats, when did you started playing cuppy and much more.",
        aliases=["pro"],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def profile(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        if not member:
            data = await self.bot.db.fetch(
                "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
            )
            if not data:
                return await ctx.invoke(self.balance)

        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", member.id
        )
        if not data:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> **{member.name}#{member.discriminator}** seems to be not registered into cuppy."
            )

        bal = data[0]["balance"]
        team = data[0]["team_name"]
        level = data[0]["team_level"]
        pick = data[0]["pickaxe_type"]
        life_earns = data[0]["lifetime_earns"]

        l_bronze = data[0]["pickaxe_bronzes"]
        l_silver = data[0]["pickaxe_silvers"]
        l_gold = data[0]["pickaxe_golds"]
        l_diamonds = data[0]["pickaxe_diamonds"]

        joined = data[0]["join_date"]

        c_open = data[0]["common_opened"]
        u_open = data[0]["uncommon_opened"]
        r_open = data[0]["rare_opened"]
        e_open = data[0]["epic_opened"]

        if team:
            ivs = Team.ivs_level_based(team, level)

            atk = ivs["atk"]
            defe = ivs["def"]
            speed = ivs["spd"]
            hp = ivs["hp"]
            magic = ivs["mag"]
            luck = ivs["luck"]

            team_name = Team.name(team)
            team_emoji = Team.emoji(team)
            team_message = f"{team_emoji} {team_name}\n⚔ `{humanize.intcomma(atk)}` 🛡 `{humanize.intcomma(defe)}`\n👟 `{humanize.intcomma(speed)}` ❤ `{humanize.intcomma(hp)}`\n✨ `{humanize.intcomma(magic)}` 🍀 `{humanize.intcomma(luck)}`"
        else:
            team_message = "No Teammate"

        pick_name = Pickaxe.name(pick)
        pick_emoji = Pickaxe.emoji(pick)

        em = discord.Embed(
            title=f"{member.name}'s Profile",
            description=f"📅 **Join Date**: <t:{int(joined)}>\n**Balance**: <:cupcake:845632403405012992> {humanize.intcomma(bal)}\n"
            f"**Teammate**: {team_message}\n\n"
            f"__**Minerals Earned**__\n{Mineral.emoji('bronze')} {humanize.intcomma(l_bronze)}x {Mineral.emoji('silver')} {humanize.intcomma(l_silver)}x\n{Mineral.emoji('gold')} {humanize.intcomma(l_gold)}x {Mineral.emoji('diamond')} {humanize.intcomma(l_diamonds)}x\n\n"
            f"**Lifetime Earnings**: <:cupcake:845632403405012992> {humanize.intcomma(life_earns)}x\n"
            f"**Pickaxe**: {pick_emoji} {pick_name}\n\n"
            f"__**Boxes Opened**__\n{Lootbox.emoji('common')} `{Lootbox.name('common')}`: {humanize.intcomma(c_open)}x\n{Lootbox.emoji('uncommon')} `{Lootbox.name('uncommon')}`: {humanize.intcomma(u_open)}x\n{Lootbox.emoji('rare')} `{Lootbox.name('rare')}`: {humanize.intcomma(r_open)}x\n{Lootbox.emoji('epic')} `{Lootbox.name('epic')}`: {humanize.intcomma(e_open)}x",
            color=self.bot.color,
        )

        em.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=em)

    @commands.command(
        help="Send some cupcakes to other members.", aliases=["gift", "send"]
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def give(self, ctx, member: discord.Member, amount: int):
        if member.id == ctx.author.id:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> {ctx.author.mention} you can't gift to yourself."
            )

        if member.bot:
            return await ctx.send(
                f"{ctx.author.mention} you can't send <:cupcake:845632403405012992> to {member.mention} since it's a bot."
            )

        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        data2 = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", member.id
        )
        if not data2:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> {ctx.author.mention} looks like **{member.name}#{member.discriminator}** is not registered into cuppy."
            )

        pick_earns = data2[0]["lifetime_earns"]
        if not pick_earns:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> {ctx.author.mention} you can't give <:cupcake:845632403405012992> to **{member.name}#{member.discriminator}** because they have less than <:cupcake:845632403405012992> **750** earned since started."
            )

        if pick_earns <= 750:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> {ctx.author.mention} you can't give <:cupcake:845632403405012992> to **{member.name}#{member.discriminator}** because they have less than <:cupcake:845632403405012992> **750** earned since started."
            )

        if amount < 1:
            return await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} you can't send negative amounts or 0.")

        bal = data[0]["balance"]
        if amount > bal:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> {ctx.author.mention} you have only <:cupcake:845632403405012992> **{humanize.intcomma(bal)}**"
            )

        await self.bot.db.execute(
            "UPDATE cuppy SET balance = $1 WHERE user_id = $2",
            data[0]["balance"] - amount,
            ctx.author.id,
        )
        await self.bot.db.execute(
            "UPDATE cuppy SET balance = $1 WHERE user_id = $2",
            data2[0]["balance"] + amount,
            member.id,
        )
        await ctx.send(
            f"<:alert_pink:867758260707000380> {ctx.author.mention} sent <:cupcake:845632403405012992> **{humanize.intcomma(amount)}** to {member.mention}"
        )

    @commands.command(
        help="Check how many cupcakes you've in this moment.", aliases=["bal"]
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def balance(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            date_today = str(int(datetime.datetime.utcnow().timestamp()))
            await self.bot.db.execute(
                "INSERT INTO cuppy (user_id, balance, pickaxe_type, pickaxe_exp, pickaxe_durability, pickaxe_earnings, pickaxe_diamonds, pickaxe_golds, pickaxe_silvers, pickaxe_bronzes, pickaxe_needed_xp, bronze, silver, gold, diamond, join_date) VALUES ($1, 10, $2, 0, 100, 0, 0, 0, 0, 0, $3, 0, 0, 0, 0, $4)",
                ctx.author.id,
                "wood",
                3500,
                date_today,
            )
            return await ctx.send(
                f"{ctx.author.mention} **your balance is now ready!**\n<:alert_pink:867758260707000380> Earn minerals mining with your pickaxe using `ami mine`!\n"
                f"<:alert_pink:867758260707000380> Vote to get <:lootbox:867758260622590002> and (**luckily**) <:uncommon:867764757733834793> <:rare:867764757670002698> or <:epic:867764757708406824> with `ami vote`!\n"
                f"<:alert_pink:867758260707000380> Upgrade your pickaxe to even more good ones (<:nebula_pickaxe:862694657959395348> <:sky_pickaxe:862694658055340032> <:divine_pickaxe:862694657891631114>) with `ami pickaxe upgrade`!\n"
                f"<:alert_pink:867758260707000380> Exchange the minerals you've got for <:cupcake:845632403405012992> with `ami exchange <mineral_name> <amount>`! Check `ami minerals values` for values of minerals!\n"
                f"<:alert_pink:867758260707000380> Create your own clan, invite friends into it and raise it to the top!"
            )

        bal = data[0]["balance"]
        await ctx.send(
            f"{ctx.author.mention} you currently have <:cupcake:845632403405012992> **{humanize.intcomma(bal)} Cupcakes!**"
        )

    @commands.command(
        help="Exchange a mineral to earn cupcakes (check `ami min val`) for minerals values.",
        aliases=["exc"],
    )
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def exchange(self, ctx, mineral_name, amount: int = None):
        valid_mins = ["bronze", "silver", "gold", "diamond"]
        if mineral_name.lower() not in valid_mins:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> {ctx.author.mention} **{mineral_name}** is not a valid mineral."
            )

        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        min = data[0][mineral_name.lower()]
        if amount is None:
            amount = min

        emoji = Mineral.emoji(mineral_name.lower())
        name = Mineral.name(mineral_name.lower())

        if amount > min:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> {ctx.author.mention} you have {emoji} **{min}x**, you can't exchange {emoji} **{amount}x**."
            )

        needed = Exchange.exc_info(mineral_name.lower())
        if min < needed:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> {ctx.author.mention} you need at least {needed}x {emoji} to exchange for <:cupcake:845632403405012992> cupcakes."
            )

        exc = Exchange.calculate_exc(mineral_name.lower(), amount)
        await self.bot.db.execute(
            f"UPDATE cuppy SET {mineral_name.lower()} = $1, balance = $2, lifetime_earns = $3 WHERE user_id = $4",
            data[0][mineral_name.lower()] - amount,
            data[0]["balance"] + exc,
            data[0]["lifetime_earns"] + exc,
            ctx.author.id,
        )
        await ctx.send(
            f"<:alert_pink:867758260707000380> {ctx.author.mention} exchanged {emoji} **{humanize.intcomma(amount)}x {name}** and earned <:cupcake:845632403405012992> **{humanize.intcomma(exc)}x Cupcakes**!"
        )

    @commands.group(
        help="Open your lootboxes <:lootbox:867758260622590002> <:uncommon:867764757733834793> <:rare:867764757670002698> <:epic:867764757708406824>",
        aliases=["op"],
        invoke_without_command=True,
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def open(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command": "open"})

    @open.command(name="luckyblock", help="Open your lucky blocks!", aliases=["lub"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lucky_block(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        blocks = data[0]["lucky_blocks"]
        if not blocks:
            return await ctx.send(
                f"{ctx.author.mention} you have no {Items.parse_all('vote', 'lucky block')['emoji']} **Lucky Blocks** to open."
            )

        c = random.choice([True, False])
        if c is True:
            earns = random.randint(15000, 150000)

            await ctx.send(
                embed=discord.Embed(
                    description=f"{ctx.author.mention} opened a {Items.parse_all('vote', 'lucky block')['emoji']} **Lucky Block**...\nand got <:cupcake:845632403405012992> **{humanize.intcomma(earns)}**!",
                    timestamp=datetime.datetime.utcnow(),
                    color=self.bot.color,
                ).set_author(
                    name=f"{ctx.author.name} opened a Lucky Block!",
                    icon_url=self.bot.user.avatar_url,
                )
            )

            return await self.bot.db.execute(
                "UPDATE cuppy SET balance = $1, lucky_blocks = $2 WHERE user_id = $3",
                data[0]["balance"] + earns,
                data[0]["lucky_blocks"] - 1,
                ctx.author.id,
            )

        await ctx.send(
            embed=discord.Embed(
                description=f"{ctx.author.mention} opened a {Items.parse_all('vote', 'lucky block')['emoji']} **Lucky Block**...\nbut found nothing.",
                timestamp=datetime.datetime.utcnow(),
                color=self.bot.color,
            ).set_author(
                name=f"{ctx.author.name} opened a Lucky Block!",
                icon_url=self.bot.user.avatar_url,
            )
        )

    @commands.command(help="Roll your dices and try to be lucky!")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def dice(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        dice = data[0]["dice"]
        if not dice:
            return await ctx.send(
                f"{ctx.author.mention} you have no {Items.parse_all('common', 'dice')['emoji']} **Dices** to roll."
            )

        mex = await ctx.send(
            f"{ctx.author.mention} it's time to roll a {Items.parse_all('common', 'dice')['emoji']} **Dice**!\n🟢 Please send a number between **1** and **6** in `30 seconds`."
        )

        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id
                and m.content.isdigit()
                and int(m.content) in range(1, 7),
                timeout=30,
            )
        except asyncio.TimeoutError:
            await mex.delete()
            return

        dice_n = random.randint(1, 6)

        await ctx.send(
            f"<a:rolling_dice:874983691686903838> Rolling a {Items.parse_all('common', 'dice')['emoji']} **Dice** for {ctx.author.mention}..."
        )
        await asyncio.sleep(4)

        if dice_n == int(msg.content):
            earnings = random.randint(20000, 150000)
            await self.bot.db.execute(
                "UPDATE cuppy SET balance = $1, dice = $2 WHERE user_id = $3",
                data[0]["balance"] + earnings,
                data[0]["dice"] - 1,
                ctx.author.id,
            )
            return await ctx.send(
                f"{ctx.author.mention} the {Items.parse_all('common', 'dice')['emoji']} **Dice** dropped a **{dice_n}**, you won and got <:cupcake:845632403405012992> **{humanize.intcomma(earnings)}**!"
            )
        else:
            await self.bot.db.execute(
                "UPDATE cuppy SET dice = $1 WHERE user_id = $2",
                data[0]["dice"] - 1,
                ctx.author.id,
            )
            return await ctx.send(
                f"{ctx.author.mention} the {Items.parse_all('common', 'dice')['emoji']} **Dice** dropped a **{dice_n}**, you lost and got nothing.."
            )

    @open.command(
        help="Choose what box to open, pass `ami box {lootbox_rarity} all` to open all the boxes you have for that rarity."
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def box(self, ctx, lootbox_rarity, flag=None):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        if flag:
            if flag != "all":
                return await ctx.send(
                    f"<:4318crossmark:848857812565229601> {ctx.author.mention} you passed an invalid argument in `flag`. Valid flag is `all`, to open all of the choosed lootbox rarity you have."
                )

        valid_lbs = ["common", "uncommon", "rare", "epic"]
        if lootbox_rarity.lower() not in valid_lbs:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> {ctx.author.mention} this is not a valid lootbox."
            )

        cups = Lootbox.coins(lootbox_rarity.lower())
        mins = Lootbox.minerals(lootbox_rarity.lower())
        emoji = Lootbox.emoji(lootbox_rarity.lower())
        name = Lootbox.name(lootbox_rarity.lower())
        drops = Lootbox.can_drop(lootbox_rarity.lower())

        lb = data[0][f"lootbox_{lootbox_rarity.lower()}"]
        if not lb:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> You don't have any {emoji} **{name}** to open."
            )

        amount = 1
        if flag == "all":
            amount = lb

        if amount > data[0][f"lootbox_{lootbox_rarity.lower()}"]:
            return await ctx.send(
                f"{ctx.author.mention} you don't have {emoji} {amount}x **{name}** left to open, `ami vote` to get more lootboxes!"
            )

        final_min = {}

        for drop in drops:
            if drop in mins:
                final_min[drop] = mins[drop]

        s = []
        for k, v in final_min.items():
            await self.bot.db.execute(
                f"UPDATE cuppy SET {k} = $1 WHERE user_id = $2",
                data[0][k] + v * amount,
                ctx.author.id,
            )
            m_emoji = Mineral.emoji(k)
            s.append(f"{m_emoji} {v*amount}x ")

        vcd = ",".join(s)
        await ctx.send(
            embed=discord.Embed(
                description=f"**{ctx.author.mention}** opened {emoji} {amount}x **{name}**...\nand found {vcd} & <:cupcake:845632403405012992> {humanize.intcomma(cups*amount)}x !",
                color=self.bot.color,
            )
            .set_author(
                name=f"{ctx.author.name} opened a {name}!",
                icon_url=self.bot.user.avatar_url,
            )
            .set_footer(text='Type "ami vote" to get more lootboxes!')
        )
        await self.bot.db.execute(
            "UPDATE cuppy SET balance = $1, lifetime_earns = $2 WHERE user_id = $3",
            data[0]["balance"] + cups * amount,
            data[0]["lifetime_earns"] + cups,
            ctx.author.id,
        )
        await self.bot.db.execute(
            f"UPDATE cuppy SET {lootbox_rarity.lower()}_opened = $1, lootbox_{lootbox_rarity.lower()} = $2 WHERE user_id = $3",
            data[0][f"{lootbox_rarity.lower()}_opened"] + amount,
            data[0][f"lootbox_{lootbox_rarity.lower()}"] - amount,
            ctx.author.id,
        )

    @commands.group(
        help="Check your pickaxe stats.", aliases=["pcx"], invoke_without_command=True
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pickaxe(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command": "pickaxe"})

    @pickaxe.command(
        help="Upgrade you pickaxe when it has reached the needed xp.", aliases=["upg"]
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def upgrade(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        pick = data[0]["pickaxe_type"]
        pick_exp = data[0]["pickaxe_exp"]
        pick_needed_xp = data[0]["pickaxe_needed_xp"]

        can_upgrade = Pickaxe.check_xp(pick_exp, pick_needed_xp)

        if pick == "earth":
            return await ctx.send(
                f"{ctx.author.mention} your have already the last pickaxe."
            )

        if can_upgrade:
            upgrade_it = Pickaxe.upgrade_pick(pick)
            if upgrade_it is False:
                return await ctx.send(
                    "<:alert_pink:867758260707000380> Your pickaxe is already upgraded to its maximum!"
                )

            dur_calc = Pickaxe.durability_set(upgrade_it)

            await self.bot.db.execute(
                "UPDATE cuppy SET pickaxe_type = $1, pickaxe_exp = $2, pickaxe_durability = $3, pickaxe_needed_xp = $4 WHERE user_id = $5",
                upgrade_it,
                pick_exp - pick_needed_xp,
                dur_calc,
                pick_exp + random.randint(1200, 2500),
                ctx.author.id,
            )
            await asyncio.sleep(1)
            data2 = await self.bot.db.fetch(
                "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
            )
            pick2 = data2[0]["pickaxe_type"]
            emoji = Pickaxe.emoji(pick2)
            name = Pickaxe.name(pick2)
            await ctx.send(
                f"<:alert_pink:867758260707000380> Congratulations, **{ctx.author.name}**! You pickaxe was upgraded to {emoji} **{name}!**"
            )
        else:
            return await ctx.reply(
                f"<:alert_pink:867758260707000380> Your pickaxe has <:xp:867817838941437974> **{humanize.intcomma(pick_exp)} / {humanize.intcomma(pick_needed_xp)}**, you can't upgrade it now."
            )

    @pickaxe.command(help="Check the stats of your actual pickaxe.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def stats(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

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

        await ctx.send(
            embed=discord.Embed(
                title=f"{ctx.author.name} pickaxe's stats!",
                description=f"__**Pickaxe Cupcakes**__\nYou've earned <:cupcake:845632403405012992> **{humanize.intcomma(pick_earns)}** since started!\n\n"
                f"__**Pickaxe**__\n{emoji} **{name}**\n<:durability:867818581864218654> **Durability**: {pick_dur} / {Pickaxe.durability_set(pick)}\n<:xp:867817838941437974> **XP**: {f'{humanize.intcomma(pick_exp)} / {humanize.intcomma(pick_needed_xp)}' if pick != 'earth' else '**`MAX LEVEL`**'}\n\n"
                f"__**Pickaxe Stats**__\n"
                f"<:bronze:867815549144530944> **Bronze Earned**: {humanize.intcomma(pick_bronzes)}\n"
                f"<:silver:867815548950413313> **Silver Earned**: {humanize.intcomma(pick_silvers)}\n"
                f"<:gold:867815549042819113> **Gold Earned**: {humanize.intcomma(pick_golds)}\n"
                f"<:diamond:867815548862332969> **Diamonds Earned**: {humanize.intcomma(pick_diam)}",
                color=self.bot.color,
            )
        )

    @pickaxe.command(
        help="The list with all the pickaxe's you can get upgrading your one."
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def list(self, ctx):
        types = [
            "wood",
            "golden",
            "ephemeral",
            "candy",
            "sky",
            "nebula",
            "divine",
            "orc",
            "earth",
        ]

        em = discord.Embed(
            title="All Pickaxes List",
            description="<:xp:867817838941437974> Will tell you what is the XP drop range for each pickaxe\n<:durability:867818581864218654> Will tell you what is the usage range of durability for each pickaxe\n<:cupcake:845632403405012992> Will tell you how many cupcakes are needed to recharge it",
            color=self.bot.color,
        )
        for pick in types:
            name = Pickaxe.name(pick)
            emoji = Pickaxe.emoji(pick)
            perks = Pickaxe.perks(pick)
            em.add_field(name=f"{emoji} {name}", value=perks)

        await ctx.send(embed=em)

    @pickaxe.command(
        help="Recharge your pickaxe for 1 cupcake when it has 0 durability.",
        aliases=["rc", "r"],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def recharge(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        pick = data[0]["pickaxe_type"]
        pick_dur = data[0]["pickaxe_durability"]

        balance = data[0]["balance"]

        emoji = Pickaxe.emoji(pick)
        name = Pickaxe.name(pick)
        recharge_amount = Pickaxe.calculate_charge(pick)

        if pick_dur != 0:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> Your {emoji} **{name}** has <:durability:867818581864218654> **{humanize.intcomma(pick_dur)} / {Pickaxe.durability_set(pick)}**, you can recharge only at <:durability:867818581864218654> **0**."
            )

        if balance < recharge_amount:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> {ctx.author.name}, recharging your {emoji} **{name}** requires <:cupcake:845632403405012992> **{recharge_amount}**, you have only <:cupcake:845632403405012992> **{balance}**."
            )

        await self.bot.db.execute(
            "UPDATE cuppy SET pickaxe_durability = $1, balance = $2 WHERE user_id = $3",
            Pickaxe.durability_set(pick),
            data[0]["balance"] - recharge_amount,
            ctx.author.id,
        )
        await ctx.send(
            f"<:alert_pink:867758260707000380> {ctx.author.name}, you've spent <:cupcake:845632403405012992> **{recharge_amount}** to refill your {emoji} **{name}** durability!"
        )

    @commands.command(
        help="The name talks itself, go mining with your pickaxe, earn minerals and exchange em for cupcakes (if you're lucky, you can obtain also cupcakes from mining!)"
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def mine(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        pick = data[0]["pickaxe_type"]
        pick_exp = data[0]["pickaxe_exp"]
        pick_upgrade = data[0]["pickaxe_needed_xp"]
        pick_durability = data[0]["pickaxe_durability"]

        emoji = Pickaxe.emoji(pick)
        name = Pickaxe.name(pick)

        info = Pickaxe.check_durability(pick_durability)
        if info is False:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> {ctx.author.name}, your {emoji} **{name}** durability is **0 / {Pickaxe.durability_set(pick)}**, recharge it with `ami pickaxe recharge`!"
            )

        message = ""
        mineral = ""
        query = ""

        cc = random.randint(1, 100)
        if data[0]["cake_uses"] and data[0]["cake_uses"] >= 1:
            await self.bot.db.execute("UPDATE cuppy SET cake_uses = $1 WHERE user_id = $2", data[0]["cake_uses"] - 1, ctx.author.id,)
            cc = random.randint(1, 150)

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
        else:
            mineral = "diamond"
            query = "diamond"
            query2 = "diamonds"

        fc = Mineral.base_mine_parser(pick, mineral)
        full_emoji = Mineral.emoji(mineral)
        full_name = Mineral.name(mineral)

        if data[0]["amulet"]:
            await self.bot.db.execute(
                f"UPDATE cuppy SET {query} = $1 WHERE user_id = $2",
                data[0][query] + (fc + ((fc / 10) / 2 * data[0]["amulet"])),
                ctx.author.id,
            )
        else:
            await self.bot.db.execute(
                f"UPDATE cuppy SET {query} = $1 WHERE user_id = $2",
                data[0][query] + fc,
                ctx.author.id,
            )

        data2 = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )

        bronze = data2[0]["bronze"]
        silver = data2[0]["silver"]
        gold = data2[0]["gold"]
        diamond = data2[0]["diamond"]

        message = f"<:alert_pink:867758260707000380> **{ctx.author.name}** you've earned {full_emoji} **{fc}x {full_name}** thanks to your {emoji} **{name}**!\n<:alert_pink:867758260707000380> Now you have <:bronze:867815549144530944> {humanize.intcomma(bronze)}x <:silver:867815548950413313> {humanize.intcomma(silver)}x <:gold:867815549042819113> {humanize.intcomma(gold)}x <:diamond:867815548862332969> {humanize.intcomma(diamond)}x"

        luck = Mineral.luck_cupcake()
        if luck:
            fg = random.randint(1, 50)
            message += f"\n<:alert_pink:867758260707000380> You were a bit lucky and you got also <:cupcake:845632403405012992> **{fg}x**!"
            await self.bot.db.execute(
                "UPDATE cuppy SET balance = $1, pickaxe_earnings = $2, lifetime_earns = $3 WHERE user_id = $4",
                data2[0]["balance"] + fg,
                data2[0]["pickaxe_earnings"] + fg,
                data2[0]["lifetime_earns"] + fc,
                ctx.author.id,
            )

        if pick != "earth":
            experience = Pickaxe.add_xp(pick)
            await self.bot.db.execute(
                "UPDATE cuppy SET pickaxe_exp = $1 WHERE user_id = $2",
                data[0]["pickaxe_exp"] + experience,
                ctx.author.id,
            )

            if (experience + pick_exp) >= pick_upgrade:
                message += f"\n<:alert_pink:867758260707000380> Oh! You pickaxe has <:xp:867817838941437974> **{humanize.intcomma(pick_exp)} / {humanize.intcomma(pick_upgrade)}**, you can upgrade it!"
            else:
                message += f"\n<:alert_pink:867758260707000380> Your pickaxe gained <:xp:867817838941437974> **{humanize.intcomma(experience)}**!"

        await ctx.send(message)
        cvf = Pickaxe.use(pick)

        if cvf > pick_durability:
            cvf = pick_durability

        await self.bot.db.execute(
            f"UPDATE cuppy SET pickaxe_{query2} = $1, pickaxe_durability = $2 WHERE user_id = $3",
            data2[0][f"pickaxe_{query2}"] + fc,
            data2[0]["pickaxe_durability"] - cvf,
            ctx.author.id,
        )

        if data2[0]["uuid_clan"]:
            data3 = await self.bot.db.fetch(
                "SELECT * FROM clans WHERE clan_uuid = $1", data2[0]["uuid_clan"]
            )
            await self.bot.db.execute(
                "UPDATE clans SET clan_mines = $1 WHERE clan_uuid = $2",
                data3[0]["clan_mines"] + 1,
                data2[0]["uuid_clan"],
            )
            await self.bot.db.execute(
                "UPDATE clans SET clan_xp = $1 WHERE clan_uuid = $2",
                data3[0]["clan_xp"] + random.randint(1, 45),
                data2[0]["uuid_clan"],
            )
            data4 = await self.bot.db.fetch(
                "SELECT * FROM clans WHERE clan_uuid = $1", data2[0]["uuid_clan"]
            )
            if data4[0]["clan_xp"] >= Clan.needed_xp(data4[0]["clan_league"]):
                if Clan.needed_xp(data4[0]["clan_league"]) is not None:
                    await self.bot.db.execute(
                        "UPDATE clans SET clan_league = $1 WHERE clan_uuid = $2",
                        Clan.next_league(data4[0]["clan_league"]),
                        data4[0]["clan_uuid"],
                    )

    @commands.group(
        help="Build a squad with a teammate, check your team stats, level up it and much more!",
        invoke_without_command=True,
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def team(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command": "team"})

    @team.command(
        help="Recruit one of the teammate listed in `ami team shop`.", aliases=["rec"]
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def recruit(self, ctx, teammate_name: str):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        teammates = [
            "kury",
            "anny",
            "fatima",
            "lilly",
            "luna",
            "celia",
            "micky",
            "vanessa",
            "ornella",
        ]

        if teammate_name.lower() not in teammates:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> {ctx.author.mention} this is not a valid teammate."
            )

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
            return await ctx.send(
                f"<:alert_pink:867758260707000380> You have only <:cupcake:845632403405012992> **{bal}**, you can't buy {emoji} **{name}**."
            )

        d = data[0]["team_name"]

        if d:
            if teammate_name.lower() == d:
                return await ctx.send(
                    f"<:alert_pink:867758260707000380> {ctx.author.mention} your current teammate is already {emoji} **{name}**"
                )

            t_name = Team.name(d)
            t_emoji = Team.emoji(d)
            msg_b = await ctx.send(
                f"<:alert_pink:867758260707000380> {ctx.author.mention} are you sure you want to replace {t_emoji} **{t_name}** × {emoji} **{name}** ?\n"
                f'<:alert_pink:867758260707000380> This will reset all the stats (IVs, Level, XP, Wins Loses, Draws).\n<:alert_pink:867758260707000380> Reply in 30 seconds with "CONFIRM" to continue or with "DECLINE" to abort.'
            )

            try:
                msg = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author.id == ctx.author.id
                    and m.channel.id == ctx.channel.id
                    and m.content.lower() in ["confirm", "decline"],
                    timeout=30,
                )
            except asyncio.TimeoutError:
                await msg_b.delete()
                return

            if msg.content.lower() == "confirm":
                await self.bot.db.execute(
                    "UPDATE cuppy SET team_name = $1, team_wins = $2, team_loses = $3, team_ties = $4, team_level = $5, team_xp = $6, balance = $7 WHERE user_id = $8",
                    teammate_name.lower(),
                    0,
                    0,
                    0,
                    1,
                    0,
                    data[0]["balance"] - 500,
                    ctx.author.id,
                )

                await ctx.send(
                    f"{ctx.author.mention} you've succesfully replaced your {t_emoji} **{t_name}** with {emoji} **{name}** for <:cupcake:845632403405012992> **500**!\n⚔ `{atk}` 🛡 `{defe}`\n👟 `{speed}` ❤ `{hp}`\n✨ `{magic}` 🍀 `{luck}`"
                )

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

        await self.bot.db.execute(
            "UPDATE cuppy SET team_name = $1, balance = $2 WHERE user_id = $3",
            teammate_name.lower(),
            data[0]["balance"] - 500,
            ctx.author.id,
        )

        await ctx.send(
            f"{ctx.author.mention} you've succesfully recruited {emoji} **{name}** for <:cupcake:845632403405012992> **500**!\n⚔ `{atk}` 🛡 `{defe}`\n👟 `{speed}` ❤ `{hp}`\n✨ `{magic}` 🍀 `{luck}`"
        )

    @team.command(
        help="Once your teammate reached level 100, you can prestige it to make it stronger!",
        aliases=["prg"],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def prestige(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        team = data[0]["team_name"]
        if not team:
            return await ctx.send(
                f"{ctx.author.mention} you don't have a teammate, check out `ami team shop`!"
            )

        level = data[0]["team_level"]
        name = Team.name(team)
        emoji = Team.emoji(team)

        if team.endswith("(prestiged)"):
            return await ctx.send(
                f"{ctx.author.mention} your {emoji} **{name}** is already prestiged."
            )

        if level < 100:
            return await ctx.send(
                f"{ctx.author.mention} your {emoji} **{name}** is <:level:868426330293821450> **{level}**: you can prestige only at <:level:868426330293821450> **100**."
            )

        bal = data[0]["balance"]
        if bal < 10000:
            return await ctx.send(
                f"{ctx.author.mention} you need <:cupcake:845632403405012992> **10,000** to prestige {emoji} **{name}**"
            )

        msg_b = await ctx.send(
            f"{ctx.author.mention} are you sure you want to prestige your {emoji} **{name}** for <:cupcake:845632403405012992> **10,000**?\n"
            f'XP & Level will return to 0, and IVs will highly raise up.\n<:alert_pink:867758260707000380> Reply in 30 seconds with "CONFIRM" to continue or with "DECLINE" to abort.'
        )

        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id
                and m.content.lower() in ["confirm", "decline"],
                timeout=30,
            )
        except asyncio.TimeoutError:
            await msg_b.delete()
            return

        if msg.content.lower() == "confirm":
            await self.bot.db.execute(
                "UPDATE cuppy SET team_name = $1, team_level = $2, team_xp = $3, balance = $4 WHERE user_id = $5",
                f"{team.lower()}" + " (prestiged)",
                1,
                0,
                data[0]["balance"] - 10000,
                ctx.author.id,
            )

            await asyncio.sleep(2)

            data2 = await self.bot.db.fetch(
                "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
            )

            team2 = data2[0]["team_name"]

            name2 = Team.name(team2)
            emoji2 = Team.emoji(team2)

            await ctx.send(
                f"{ctx.author.mention} you've spent <:cupcake:845632403405012992> **10,000** and now your teammate is {emoji2} **{name2}** !!"
            )

            return

        elif msg.content.lower() == "decline":
            await msg_b.delete()
            try:
                await msg.delete()
            except Exception:
                pass

            return

    @team.command(help="Check your teammate stats", name="stats")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def team_stats(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", member.id
        )
        if not data:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> {ctx.author.mention} this member is not a cuppy player."
            )

        teammate = data[0]["team_name"]
        if not teammate:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> Teammate not found."
            )

        name = Team.name(teammate)
        emoji = Team.emoji(teammate)
        moves = Team.get_moves(teammate)
        basic = moves["base"]
        special = moves["special"]

        special_final = []
        basic_final = []

        for move in basic:
            name1 = Team.get_move_name(move)
            emoji1 = Team.move_emoji(move)
            damage1 = Team.get_move_base_damage(move)
            basic_final.append(f"{emoji1} **{name1}** | 💥 {damage1}")

        for move in special:
            name2 = Team.get_move_name(move)
            emoji2 = Team.move_emoji(move)
            damage2 = Team.get_move_base_damage(move)
            special_final.append(f"{emoji2} **{name2}** | 💥 {damage2}")

        move3 = Team.get_moves(teammate)["ultra"]
        name3 = Team.get_move_name(move3)
        damage3 = Team.get_move_base_damage(move3)
        emoji3 = Team.move_emoji(move3)

        b_final = "\n".join(basic_final)
        s_final = "\n".join(special_final)
        u_final = f"{emoji3} **{name3}** | 💥 {damage3}"

        exp = data[0]["team_xp"]
        level = data[0]["team_level"]
        needed_xp = Team.calc_needed_xp(level, teammate.lower())
        wins = data[0]["team_wins"]
        loses = data[0]["team_loses"]
        draws = data[0]["team_ties"]
        friendship = data[0]["team_friendship"]

        ivs = Team.ivs_level_based(teammate.lower(), level)

        atk = ivs["atk"]
        defe = ivs["def"]
        speed = ivs["spd"]
        hp = ivs["hp"]
        magic = ivs["mag"]
        luck = ivs["luck"]

        if friendship > 100:
            friendship = 100

        f_cs = ((friendship) / 100) * 100
        f_calc = round(f_cs, 2)

        img = Team.images(teammate)
        story = Team.get_story(teammate)

        em = discord.Embed(
            title=f"{member.name}'s Teammate",
            description=f"<:alert_pink:867758260707000380> {emoji} **{name}**\n{story}\n\n**IVs**: ⚔ `{atk}` 🛡 `{defe}` 👟 `{speed}` ❤ `{hp}` ✨ `{magic}` 🍀 `{luck}`\n",
            color=self.bot.color,
        )
        em.add_field(name="Moveset", value=f"{b_final}\n{s_final}\n{u_final}")
        em.add_field(
            name="Progress",
            value=f"<:xp:867817838941437974> **EXP**: {humanize.intcomma(exp)} / {humanize.intcomma(needed_xp)}\n"
            f"<:level:868426330293821450> **Level**: {humanize.intcomma(level)}\n"
            f"🏅 **Wins**: {humanize.intcomma(wins)}\n"
            f"🥈 **Loses**: {humanize.intcomma(loses)}\n"
            f"🥉 **Draws**: {humanize.intcomma(draws)}",
        )
        em.set_thumbnail(url=img)
        em.set_footer(text=f"× Friendship: {f_calc}%")

        await ctx.send(embed=em)

    @team.command(
        help="A list with all the availables to buy teammates.", aliases=["sh", "s"]
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def shop(self, ctx):
        em = discord.Embed(
            title="Teammates Shop",
            description="Recruiting one of them will cost you <:cupcake:845632403405012992> **500**\n`ami team recruit <teammate_name>` to recruit one of these teammates.\n`ami team stats` to check your actual teammate stats.\nIVs will became higher leveling up your teammate.\n⚔ Attack, 🛡 Defense, 👟 Speed, ❤ HP, ✨ Magic, 🍀 Luck",
            color=self.bot.color,
        )

        teammates = [
            "kury",
            "anny",
            "fatima",
            "lilly",
            "luna",
            "celia",
            "micky",
            "vanessa",
            "ornella",
        ]
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

            em.add_field(
                name=f"{emoji} {name}",
                value=f"⚔ `{atk}` 🛡 `{defe}`\n👟 `{speed}` ❤ `{hp}`\n✨ `{magic}` 🍀 `{luck}`",
            )

        await ctx.send(embed=em)

    @commands.command(
        help="Fight other members with your teammate to earn xp and have a bit of fun maybe >:)",
        aliases=["fight", "b"],
    )
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def battle(self, ctx, opponent: discord.Member):

        if opponent.id == ctx.author.id:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> {ctx.author.mention} you can't battle against yourself."
            )

        data1 = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        data2 = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", opponent.id
        )

        if not data1:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> {ctx.author.mention} you are not registered into cuppy, type `ami balance` to register yourself."
            )

        if not data2:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> {opponent.mention} is not registered into cuppy."
            )

        if (
            data1[0]["xp_room_date"]
            and datetime.datetime.utcnow() < data1[0]["xp_room_date"]
        ):
            return await ctx.send(
                f"{ctx.author.mention} your 🏹 **XP-Room** is not ended yet, you can't battle while it's running."
            )

        if (
            data2[0]["xp_room_date"]
            and datetime.datetime.utcnow() < data2[0]["xp_room_date"]
        ):
            return await ctx.send(
                f"{ctx.author.mention} the opponent has the 🏹 **XP-Room** running, he can't battle now."
            )

        if data1[0]["xp_room_date"]:
            return await ctx.send(
                f"{ctx.author.mention} your 🏹 **XP-Room** is ended, please claim it before battling."
            )

        if data2[0]["xp_room_date"]:
            return await ctx.send(
                f"{ctx.author.mention} the opponent has not claimed the 🏹 **XP-Room** ended, he can't battle until he/she claim that."
            )

        team_author = data1[0]["team_name"]
        team_opponent = data2[0]["team_name"]

        if not team_author:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> {ctx.author.mention} you don't have a teammate to battle, check `ami team shop`."
            )

        if not team_opponent:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> {opponent.mention} doesn't have a teammate to battle with you."
            )

        n_team_author = Team.name(team_author)
        n_team_opponent = Team.name(team_opponent)

        e_team_author = Team.emoji(team_author)
        e_team_opponent = Team.emoji(team_opponent)

        m_team_author = Team.get_moves(team_author)
        m_team_opponent = Team.get_moves(team_opponent)

        level_team_author = data1[0]["team_level"]
        level_team_opponent = data2[0]["team_level"]

        ivs_author = Team.ivs_level_based(team_author, level_team_author)
        ivs_opponent = Team.ivs_level_based(team_opponent, level_team_opponent)

        atk_team_author = ivs_author["atk"]
        atk_team_opponent = ivs_opponent["atk"]

        hp_team_author = ivs_author["hp"] * 10
        hp_team_opponent = ivs_opponent["hp"] * 10

        basic_moves_author = m_team_author["base"]
        basic_moves_opponent = m_team_opponent["base"]

        special_moves_author = m_team_author["special"]
        special_moves_opponent = m_team_opponent["special"]

        ultra_moves_author = m_team_author["ultra"]
        ultra_moves_opponent = m_team_opponent["ultra"]

        b_msg = await ctx.send(
            f"<:alert_pink:867758260707000380> {ctx.author.mention} challenged {opponent.mention} to a battle!",
            embed=discord.Embed(color=self.bot.color)
            .add_field(
                name=f"{e_team_author} **{n_team_author}** ({ctx.author.name})",
                value=f"<:level:868426330293821450> **{level_team_author}** <:level:868426330293821450>",
            )
            .add_field(
                name=f"{e_team_opponent} **{n_team_opponent}** ({opponent.name})",
                value=f"<:level:868426330293821450> **{level_team_opponent}** <:level:868426330293821450>",
            )
            .set_footer(
                text=f'{opponent.name} in 30 seconds type "CONFIRM" to accept or "DECLINE" to abort.'
            ),
        )

        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author.id == opponent.id
                and m.channel.id == ctx.channel.id
                and m.content.lower() in ["confirm", "decline"],
                timeout=30,
            )
        except asyncio.TimeoutError:
            await b_msg.delete()
            return

        if msg.content.lower() == "decline":
            await b_msg.delete()
            return

        if msg.content.lower() == "confirm":

            if data1[0]["uuid_clan"]:
                data3 = await self.bot.db.fetch(
                    "SELECT * FROM clans WHERE clan_uuid = $1", data1[0]["uuid_clan"]
                )
                await self.bot.db.execute(
                    "UPDATE clans SET clan_battles = $1 WHERE clan_uuid = $2",
                    data3[0]["clan_battles"] + 1,
                    data1[0]["uuid_clan"],
                )
                await self.bot.db.execute(
                    "UPDATE clans SET clan_xp = $1 WHERE clan_uuid = $2",
                    data3[0]["clan_xp"] + random.randint(1, 45),
                    data1[0]["uuid_clan"],
                )
                data4 = await self.bot.db.fetch(
                    "SELECT * FROM clans WHERE clan_uuid = $1", data1[0]["uuid_clan"]
                )
                if data4[0]["clan_xp"] >= Clan.needed_xp(data4[0]["clan_league"]):
                    if Clan.needed_xp(data4[0]["clan_league"]) is not None:
                        await self.bot.db.execute(
                            "UPDATE clans SET clan_league = $1 WHERE clan_uuid = $2",
                            Clan.next_league(data4[0]["clan_league"]),
                            data1[0]["clan_uuid"],
                        )

            if data2[0]["uuid_clan"]:
                data3 = await self.bot.db.fetch(
                    "SELECT * FROM clans WHERE clan_uuid = $1", data2[0]["uuid_clan"]
                )
                await self.bot.db.execute(
                    "UPDATE clans SET clan_battles = $1 WHERE clan_uuid = $2",
                    data3[0]["clan_battles"] + 1,
                    data2[0]["uuid_clan"],
                )
                await self.bot.db.execute(
                    "UPDATE clans SET clan_xp = $1 WHERE clan_uuid = $2",
                    data3[0]["clan_xp"] + random.randint(1, 45),
                    data2[0]["uuid_clan"],
                )
                data4 = await self.bot.db.fetch(
                    "SELECT * FROM clans WHERE clan_uuid = $1", data2[0]["uuid_clan"]
                )
                if data4[0]["clan_xp"] >= Clan.needed_xp(data4[0]["clan_league"]):
                    if Clan.needed_xp(data4[0]["clan_league"]) is not None:
                        await self.bot.db.execute(
                            "UPDATE clans SET clan_league = $1 WHERE clan_uuid = $2",
                            Clan.next_league(data4[0]["clan_league"]),
                            data2[0]["clan_uuid"],
                        )

            current_hp_author = hp_team_author
            current_hp_opponent = hp_team_opponent

            em1 = discord.Embed(color=self.bot.color)
            em1.add_field(
                name=f"{e_team_author} {n_team_author} ({ctx.author.name})",
                value=f"❤ {humanize.intcomma(current_hp_author)} / {humanize.intcomma(hp_team_author)} ❤",
            )
            em1.add_field(
                name=f"{e_team_opponent} {n_team_opponent} ({opponent.name})",
                value=f"❤ {humanize.intcomma(current_hp_opponent)} / {humanize.intcomma(hp_team_opponent)} ❤",
            )

            msg_one = await ctx.send("The match will start in 5 seconds...", embed=em1)

            if data1[0]["drink_uses"] and data1[0]["drink_uses"] >= 1:
                await self.bot.db.execute(
                    "UPDATE cuppy SET drink_uses = $1 WHERE user_id = $2",
                    data1[0]["drink_uses"] - 1,
                    ctx.author.id,
                )

            if data2[0]["drink_uses"] and data2[0]["drink_uses"] >= 1:
                await self.bot.db.execute(
                    "UPDATE cuppy SET drink_uses = $1 WHERE user_id = $2",
                    data2[0]["drink_uses"] - 1,
                    ctx.author.id,
                )

            friend = 1
            await asyncio.sleep(5)

            while True:
                cc_1 = random.choice(range(1, 100))
                if cc_1 in range(1, 50):
                    move_author = random.choice(basic_moves_author)
                elif cc_1 in range(50, 95):
                    move_author = random.choice(special_moves_author)
                else:
                    move_author = ultra_moves_author

                cc_2 = random.choice(range(1, 100))
                if cc_2 in range(1, 50):
                    move_opponent = random.choice(basic_moves_opponent)
                elif cc_2 in range(50, 95):
                    move_opponent = random.choice(special_moves_opponent)
                else:
                    move_opponent = ultra_moves_opponent

                author_move_name = Team.get_move_name(move_author)
                author_move_emoji = Team.move_emoji(move_author)
                author_move_damage = Team.get_move_base_damage(move_author)

                opponent_move_name = Team.get_move_name(move_opponent)
                opponent_move_emoji = Team.move_emoji(move_opponent)
                opponent_move_damage = Team.get_move_base_damage(move_opponent)

                critical_author = False
                critical_opponent = False

                mex_crit_author = "!"
                mex_crit_opponent = "!"

                cf_1 = random.randint(1, 100)
                if cf_1 in range(1, 50):
                    pass
                elif cf_1 in range(50, 76):
                    mex_crit_author = " (**`CRITICAL`**)"
                    critical_author = True
                else:
                    mex_crit_opponent = " (**`CRITICAL`**)"
                    critical_opponent = True

                final_damage_author = 0
                final_damage_opponent = 0

                if critical_author:
                    final_damage_author = (
                        author_move_damage
                        + (int(atk_team_author / 5))
                        + random.randint(40, 100)
                    ) * 2
                else:
                    final_damage_author = (
                        author_move_damage + (int(atk_team_author / 5))
                    ) * 2

                if critical_opponent:
                    final_damage_opponent = (
                        opponent_move_damage
                        + (int(atk_team_opponent / 5))
                        + random.randint(40, 100)
                    ) * 2
                else:
                    final_damage_opponent = (
                        opponent_move_damage + (int(atk_team_opponent / 5))
                    ) * 2

                current_hp_author = current_hp_author - int(final_damage_opponent)
                current_hp_opponent = current_hp_opponent - int(final_damage_author)

                if current_hp_author < 1:
                    current_hp_author = 0

                if current_hp_opponent < 1:
                    current_hp_opponent = 0

                author_team_image = Team.images(team_author)
                opponent_team_image = Team.images(team_opponent)

                r = BattleRenderer(
                    author_team_image,
                    opponent_team_image,
                    char_1_stats={
                        "name": n_team_author.replace(
                            "<:prestiged:870289549190897664>", "Prestiged"
                        ),
                        "level": level_team_author,
                        "max_hp": hp_team_author,
                    },
                    char_2_stats={
                        "name": n_team_opponent.replace(
                            "<:prestiged:870289549190897664>", "Prestiged"
                        ),
                        "level": level_team_opponent,
                        "max_hp": hp_team_opponent,
                    },
                )
                file = await r.render(current_hp_author, current_hp_opponent)

                em2 = discord.Embed(
                    description=f"{e_team_author} **{n_team_author}** landed a {author_move_emoji} **{author_move_name}**: that dealt 💥 {humanize.intcomma(final_damage_author)}{mex_crit_author}\n"
                    f"{e_team_opponent} **{n_team_opponent}** landed a {opponent_move_emoji} **{opponent_move_name}**: that dealt 💥 {humanize.intcomma(final_damage_opponent)}{mex_crit_opponent}",
                    color=self.bot.color,
                )
                em2.set_image(url="attachment://battle.png")
                em2.set_footer(text="Moves were landed automatically each 5 seconds.")
                await ctx.send(embed=em2, file=file)

                if (
                    current_hp_opponent <= 0
                    and current_hp_author <= 0
                    or current_hp_author <= 0
                    and current_hp_opponent <= 0
                ):
                    await self.bot.db.execute(
                        "UPDATE cuppy SET team_ties = $1, team_friendship = $2 WHERE user_id = $3",
                        data1[0]["team_ties"] + 1,
                        data1[0]["team_friendship"] + friend,
                        ctx.author.id,
                    )
                    await self.bot.db.execute(
                        "UPDATE cuppy SET team_ties = $1, team_friendship = $2 WHERE user_id = $3",
                        data2[0]["team_ties"] + 1,
                        data2[0]["team_friendship"] + friend,
                        opponent.id,
                    )
                    await ctx.send(
                        f"{opponent.mention} {ctx.author.mention} the battle between {e_team_author} **{n_team_author}** & {e_team_opponent} **{n_team_opponent}** ended in a draw, no <:xp:867817838941437974> has been given out."
                    )
                    break

                if current_hp_opponent <= 0:
                    xp_amount = 100 * level_team_opponent
                    await self.bot.db.execute(
                        "UPDATE cuppy SET team_xp = $1, team_wins = $2, team_friendship = $3 WHERE user_id = $4",
                        data1[0]["team_xp"] + xp_amount,
                        data1[0]["team_wins"] + 1,
                        data1[0]["team_friendship"] + friend,
                        ctx.author.id,
                    )
                    await self.bot.db.execute(
                        "UPDATE cuppy SET team_loses = $1 WHERE user_id = $2",
                        data2[0]["team_loses"] + 1,
                        opponent.id,
                    )
                    data = await self.bot.db.fetch(
                        "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
                    )
                    lvl = data[0]["team_level"]

                    if data[0]["team_xp"] >= Team.calc_needed_xp(
                        lvl, n_team_author.lower()
                    ):
                        await ctx.send(
                            f"<:alert_pink:867758260707000380> {ctx.author.mention} {e_team_author} **{n_team_author}** won the battle against {e_team_opponent} **{n_team_opponent}** and gained <:xp:867817838941437974> **{xp_amount}**!\n"
                            f"<:alert_pink:867758260707000380> Oh! {e_team_author} **{n_team_author}** leveled up to <:level:868426330293821450> **{data[0]['team_level'] + 1}**!"
                        )
                        await self.bot.db.execute(
                            "UPDATE cuppy SET team_level = $1, team_xp = $2 WHERE user_id = $3",
                            data[0]["team_level"] + 1,
                            0,
                            ctx.author.id,
                        )

                        break

                    await ctx.send(
                        f"<:alert_pink:867758260707000380> {ctx.author.mention} {e_team_author} **{n_team_author}** won the battle against {e_team_opponent} **{n_team_opponent}** and gained <:xp:867817838941437974> **{xp_amount}**!"
                    )
                    break

                elif current_hp_author <= 0:
                    xp_amount = 100 * level_team_author
                    await self.bot.db.execute(
                        "UPDATE cuppy SET team_xp = $1, team_wins = $2, team_friendship = $3 WHERE user_id = $4",
                        data2[0]["team_xp"] + xp_amount,
                        data2[0]["team_wins"] + 1,
                        data2[0]["team_friendship"] + friend,
                        opponent.id,
                    )
                    await self.bot.db.execute(
                        "UPDATE cuppy SET team_loses = $1 WHERE user_id = $2",
                        data1[0]["team_loses"] + 1,
                        ctx.author.id,
                    )
                    data = await self.bot.db.fetch(
                        "SELECT * FROM cuppy WHERE user_id = $1", opponent.id
                    )
                    lvl = data[0]["team_level"]

                    if data[0]["team_xp"] >= Team.calc_needed_xp(
                        lvl, n_team_opponent.lower()
                    ):
                        await ctx.send(
                            f"<:alert_pink:867758260707000380> {opponent.mention} {e_team_opponent} **{n_team_opponent}** won the battle against {e_team_author} **{n_team_author}** and gained <:xp:867817838941437974> **{xp_amount}**!\n"
                            f"<:alert_pink:867758260707000380> Oh! {e_team_opponent} **{n_team_opponent}** leveled up to <:level:868426330293821450> **{data[0]['team_level'] + 1}**!"
                        )
                        await self.bot.db.execute(
                            "UPDATE cuppy SET team_level = $1, team_xp = $2 WHERE user_id = $3",
                            data[0]["team_level"] + 1,
                            0,
                            opponent.id,
                        )

                        break

                    await ctx.send(
                        f"<:alert_pink:867758260707000380> {opponent.mention} {e_team_opponent} **{n_team_opponent}** won the battle against {e_team_author} **{n_team_author}** and gained <:xp:867817838941437974> **{xp_amount}**!"
                    )
                    break

                await asyncio.sleep(5)
                continue

    @commands.command()
    @is_team()
    async def test(self, ctx, teammate: str, level: int):
        ivs = Team.ivs_level_based(teammate.lower(), level)
        return await ctx.send(ivs)

    @commands.command(
        help="A kinda of box where you can see all the availabes monsters to hunt, the sword means you've defeated it, the folder you've jailed it.",
        aliases=["mlist", "ml"],
    )
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def monsterlist(self, ctx):
        d = ["common", "rare", "super rare", "mystic", "special"]

        entries = []

        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )

        if not data:
            return await ctx.invoke(self.balance)

        for m in d:
            mon_list = Monster.rarity_ordered(m)
            for c in mon_list:
                mon_rar = Monster.get_rarity(c)
                mon_name = Monster.name(c)
                mon_emoji = Monster.emoji(c)
                rar_emoji = Rarity.emoji(mon_rar)
                mon_cup = Monster.cup_drop(c)
                mon_xp = Monster.xp_drop(c)
                mon_hp = Monster.get_hp(c)
                if data[0]["monsters_jailed"] is None:
                    caught = "<:not_caught:871473758186139698>"
                else:
                    caught = (
                        "<:caught:871473351309287434>"
                        if c in data[0]["monsters_jailed"]
                        else "<:not_caught:871473758186139698>"
                    )

                if data[0]["monsters_defeated"] is None:
                    deaf = "<:not_defeated:871498051032875048>"
                else:
                    deaf = (
                        "<:defeated:871498051209003059>"
                        if c in data[0]["monsters_defeated"]
                        else "<:not_defeated:871498051032875048>"
                    )

                entries.append(
                    f"{deaf} {caught} <:xp:867817838941437974> `{mon_xp*10}` ❤ `{mon_hp}` <:cupcake:845632403405012992> `{mon_cup}` | {rar_emoji} {mon_emoji} **{mon_name}** "
                )

        pages = Paginate(entries)
        paginator = menus.MenuPages(
            source=pages, timeout=45.5, delete_message_after=True
        )
        await paginator.start(ctx)

        # await ctx.send(embed = discord.Embed(
        # title = "Monsters List",
        # description = "Listed you can see all the current "
        # "spottable monsters with their rarity.\n\n" + '\n'.join(f),
        # color = self.bot.color
        # ))

    @commands.command(
        help="Go hunting monsters and try defeat or jail em with your teammate.",
        aliases=["mh", "mhunt"],
    )
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def monsterhunt(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        team = data[0]["team_name"]
        if not team:
            return await ctx.send(
                f"<:alert_pink:867758260707000380> {ctx.author.mention} you need a teammate to go hunting monsters, check out `ami team shop`!"
            )

        if (
            data[0]["xp_room_date"]
            and datetime.datetime.utcnow() < data[0]["xp_room_date"]
        ):
            return await ctx.send(
                f"{ctx.author.mention} your 🏹 **XP-Room** is not ended yet, you can't hunt monsters while it's running."
            )

        if data[0]["xp_room_date"]:
            return await ctx.send(
                f"{ctx.author.mention} your 🏹 **XP-Room** is ended, please claim it before going to hunt monsters."
            )

        team_level = data[0]["team_level"]
        team_name = Team.name(team)
        team_emoji = Team.emoji(team)
        ivs = Team.ivs_level_based(team, team_level)
        moves = Team.get_moves(team)

        atk = ivs["atk"]

        basic_moves = moves["base"]
        special_moves = moves["special"]
        ultra_moves = moves["ultra"]

        monste = None
        col = None
        mexuses = ""

        cvfd = random.randint(1, 100)
        if data[0]["bells_uses"] and data[0]["bells_uses"] >= 1:
            cvfd = random.randint(1, 130)
            await self.bot.db.execute(
                "UPDATE cuppy SET bells_uses = $1 WHERE user_id = $2",
                data[0]["bells_uses"] - 1,
                ctx.author.id,
            )
            if data[0]["bells_uses"] == 0:
                mexuses += f"{ctx.author.mention} your {Items.parse_all('common', 'bells')['emoji']} boost has expired."

        if cvfd in range(1, 50):
            monste = "common"
            col = int("000080", 16)
        elif cvfd in range(50, 76):
            monste = "rare"
            col = int("FF8C00", 16)
        elif cvfd in range(75, 95):
            monste = "super rare"
            col = int("FFFF00", 16)
        elif cvfd in range(95, 99):
            monste = "mystic"
            col = int("FF0000", 16)
        else:
            monste = "special"
            col = int("FFFFF0", 16)

        monste_s = Monster.rarity_ordered(monste)

        monster = random.choice(monste_s)

        mon_hp = Monster.get_hp(monster)

        mon_name = Monster.name(monster)
        mon_emoji = Monster.emoji(monster)

        mon_cup = Monster.cup_drop(monster)
        mon_xp = Monster.xp_drop(monster)
        mon_im = Monster.get_image(monster)

        mon_rar = Monster.get_rarity(monster)
        mon_rar_str = Rarity.find_rarity(mon_rar)

        c_c = random.randint(1, 90)
        j_c = random.randint(1, 90)

        if data[0]["cherries_uses"] and data[0]["cherries_uses"] >= 1:
            c_c = random.randint(40, 90)
            await self.bot.db.execute(
                "UPDATE cuppy SET cherries_uses = $1 WHERE user_id = $2",
                data[0]["cherries_uses"] - 1,
                ctx.author.id,
            )
            if data[0]["cherries_uses"] == 0:
                mexuses += f"{ctx.author.mention} your {Items.parse_all('common', 'cherries')['emoji']} boost has expired.\n"

        if data[0]["potion_uses"] and data[0]["potion_uses"] >= 1:
            j_c = random.randint(40, 90)
            await self.bot.db.execute(
                "UPDATE cuppy SET potion_uses = $1 WHERE user_id = $2",
                data[0]["potion_uses"] - 1,
                ctx.author.id,
            )
            if data[0]["potion_uses"] == 0:
                mexuses += f"{ctx.author.mention} your {Items.parse_all('common', 'potion')['emoji']} boost has expired."

        if data[0]["uuid_clan"]:
            data3 = await self.bot.db.fetch(
                "SELECT * FROM clans WHERE clan_uuid = $1", data[0]["uuid_clan"]
            )
            await self.bot.db.execute(
                "UPDATE clans SET clan_hunts = $1 WHERE clan_uuid = $2",
                data3[0]["clan_hunts"] + 1,
                data[0]["uuid_clan"],
            )
            await self.bot.db.execute(
                "UPDATE clans SET clan_xp = $1 WHERE clan_uuid = $2",
                data3[0]["clan_xp"] + random.randint(1, 45),
                data[0]["uuid_clan"],
            )
            data4 = await self.bot.db.fetch(
                "SELECT * FROM clans WHERE clan_uuid = $1", data[0]["uuid_clan"]
            )
            if data4[0]["clan_xp"] >= Clan.needed_xp(data4[0]["clan_league"]):
                if Clan.needed_xp(data4[0]["clan_league"]) is not None:
                    await self.bot.db.execute(
                        "UPDATE clans SET clan_league = $1 WHERE clan_uuid = $2",
                        Clan.next_league(data4[0]["clan_league"]),
                        data4[0]["clan_uuid"],
                    )

        mex = await ctx.send(
            f"{ctx.author.mention} type any of ⚔ `attack`, ⛓ `jail` or 🏃‍♂️ `escape`!",
            embed=discord.Embed(
                title="Monster Spotted!",
                description=f"{team_emoji} **{team_name}** spotted a wild {mon_emoji} **{mon_name}**!",
                color=col,
            )
            .set_image(url=mon_im)
            .set_footer(
                text=f"{mon_rar_str}\n\nHealth: {humanize.intcomma(mon_hp)}\nCrit. Chance: {c_c}%\nJail Chance: {j_c}%\n\n═════ Rates ═════\n"
                f"• Jailing it is {mon_cup} cupcakes valued!\n"
                f"• Attacking and defeating it is {humanize.intcomma(mon_xp*10)} XP valued!\n"
                f"• Escaping will make you lose 50 cupcakes!"
            ),
        )

        try:
            msg = await self.bot.wait_for(
                "message",
                check=lambda m: m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id
                and m.content.lower() in ["attack", "atk", "jail", "escape", "run"],
                timeout=15,
            )
        except asyncio.TimeoutError:
            await mex.edit(
                content=f"{ctx.author.mention} took too long to choose..",
                embed=discord.Embed(
                    title="Monster Escaped..",
                    description=f"{mon_emoji} **{mon_name}** ran away..",
                    color=col,
                ).set_image(url=mon_im),
            )
            if len(mexuses) > 1:
                return await ctx.send(mexuses)
            return

        if msg.content.lower() in ["attack", "atk"]:

            critical = False
            crit_chance = random.randint(1, 100)
            if crit_chance in range(1, c_c):
                critical = True

            chance = random.randint(1, 100)

            move = None

            if chance in range(1, 20):
                move = random.choice(basic_moves)
            elif chance in range(20, 75):
                move = random.choice(special_moves)
            else:
                move = ultra_moves

            move_name = Team.get_move_name(move)
            move_emoji = Team.move_emoji(move)
            move_damage = Team.get_move_base_damage(move)

            damage = (move_damage + (int(atk / 5))) * 2
            c_m = "!"
            if critical:
                c_m = " (**`CRITICAL`**)"
                damage = (move_damage + (int(atk / 5)) + random.randint(40, 100)) * 2

            if damage < mon_hp:
                await mex.edit(
                    content=f"{team_emoji} **{team_name}** landed a {move_emoji} **{move_name}**: that dealt 💥 {humanize.intcomma(damage)}{c_m}\n"
                    f"{mon_emoji} **{mon_name}** remained with ❤ {humanize.intcomma(mon_hp-damage)} / {humanize.intcomma(mon_hp)} and ran away.",
                    embed=discord.Embed(
                        title="Monster Escaped..",
                        description=f"{team_emoji} **{team_name}** failed defeating {mon_emoji} **{mon_name}**..",
                        color=col,
                    ).set_image(url=mon_im),
                )

                if len(mexuses) > 1:
                    return await ctx.send(mexuses)
                return

            elif damage > mon_hp:
                m = f"Rarity: {mon_rar_str}\n\n═════ Reward ═════\n[★] {team_name.strip('<:prestiged:870289549190897664>')} earned {humanize.intcomma(mon_xp*10)} XP!"
                await self.bot.db.execute(
                    "UPDATE cuppy SET team_xp = $1 WHERE user_id = $2",
                    data[0]["team_xp"] + mon_xp * 10,
                    ctx.author.id,
                )
                data2 = await self.bot.db.fetch(
                    "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
                )
                if data2[0]["team_xp"] >= Team.calc_needed_xp(
                    data2[0]["team_level"], team
                ):
                    await self.bot.db.execute(
                        "UPDATE cuppy SET team_level = $1, team_xp = $2 WHERE user_id = $3",
                        data2[0]["team_level"] + 1,
                        0,
                        ctx.author.id,
                    )
                    m = f"Rarity: {mon_rar_str}\n\n═════ Reward ═════\n[★] {team_name.strip('<:prestiged:870289549190897664>')} earned {humanize.intcomma(mon_xp*10)} XP!\n[★] Oh! {team_name.strip('<:prestiged:870289549190897664>')} leveled up to level {data2[0]['team_level'] + 1}!"

                if data2[0]["uuid_clan"]:
                    data3 = await self.bot.db.fetch(
                        "SELECT * FROM clans WHERE clan_uuid = $1",
                        data2[0]["uuid_clan"],
                    )
                    await self.bot.db.execute(
                        "UPDATE clans SET clan_defeats = $1 WHERE clan_uuid = $2",
                        data3[0]["clan_defeats"] + 1,
                        data2[0]["uuid_clan"],
                    )
                    await self.bot.db.execute(
                        "UPDATE clans SET clan_xp = $1 WHERE clan_uuid = $2",
                        data3[0]["clan_xp"] + random.randint(1, 45),
                        data2[0]["uuid_clan"],
                    )
                    data4 = await self.bot.db.fetch(
                        "SELECT * FROM clans WHERE clan_uuid = $1", data[0]["uuid_clan"]
                    )
                    if data4[0]["clan_xp"] >= Clan.needed_xp(data4[0]["clan_league"]):
                        if Clan.needed_xp(data4[0]["clan_league"]) is not None:
                            await self.bot.db.execute(
                                "UPDATE clans SET clan_league = $1 WHERE clan_uuid = $2",
                                Clan.next_league(data4[0]["clan_league"]),
                                data[0]["clan_uuid"],
                            )

                monsdc = data[0]["monsters_defeated"]
                if monsdc is None:
                    await self.bot.db.execute(
                        "UPDATE cuppy SET monsters_defeated = array_append(monsters_defeated, $1) WHERE user_id = $2",
                        monster,
                        ctx.author.id,
                    )
                else:
                    if monster not in monsdc:
                        await self.bot.db.execute(
                            "UPDATE cuppy SET monsters_defeated = array_append(monsters_defeated, $1) WHERE user_id = $2",
                            monster,
                            ctx.author.id,
                        )

                await mex.edit(
                    content=f"{team_emoji} **{team_name}** landed a {move_emoji} **{move_name}**: that dealt 💥 {humanize.intcomma(damage)}{c_m}\n"
                    f"{mon_emoji} **{mon_name}** fell for the damage, the hunt was a success!",
                    embed=discord.Embed(
                        title=f"Congratulations, {ctx.author.name}!",
                        description=f"{team_emoji} **{team_name}** defeated {mon_emoji} **{mon_name}**!",
                        color=col,
                    )
                    .set_image(url=mon_im)
                    .set_footer(text=f"{m}"),
                )

                if len(mexuses) > 1:
                    return await ctx.send(mexuses)
                return

        if msg.content.lower() == "jail":
            jchance = random.randint(1, 100)
            if jchance in range(1, j_c):

                jchancec = random.randint(1, 100)

                jmove = None

                if jchancec in range(1, 20):
                    jmove = random.choice(basic_moves)
                elif jchancec in range(20, 75):
                    jmove = random.choice(special_moves)
                else:
                    jmove = ultra_moves

                jmove_name = Team.get_move_name(jmove)
                jmove_emoji = Team.move_emoji(jmove)

                await self.bot.db.execute(
                    "UPDATE cuppy SET balance = $1, lifetime_earns = $2 WHERE user_id = $3",
                    data[0]["balance"] + mon_cup,
                    data[0]["lifetime_earns"] + mon_cup,
                    ctx.author.id,
                )
                if data[0]["uuid_clan"]:
                    data3 = await self.bot.db.fetch(
                        "SELECT * FROM clans WHERE clan_uuid = $1", data[0]["uuid_clan"]
                    )
                    await self.bot.db.execute(
                        "UPDATE clans SET clan_jails = $1 WHERE clan_uuid = $2",
                        data3[0]["clan_jails"] + 1,
                        data[0]["uuid_clan"],
                    )
                    await self.bot.db.execute(
                        "UPDATE clans SET clan_xp = $1 WHERE clan_uuid = $2",
                        data3[0]["clan_xp"] + random.randint(1, 45),
                        data[0]["uuid_clan"],
                    )
                    data4 = await self.bot.db.fetch(
                        "SELECT * FROM clans WHERE clan_uuid = $1", data[0]["uuid_clan"]
                    )
                    if data4[0]["clan_xp"] >= Clan.needed_xp(data4[0]["clan_league"]):
                        if Clan.needed_xp(data4[0]["clan_league"]) is not None:
                            await self.bot.db.execute(
                                "UPDATE clans SET clan_league = $1 WHERE clan_uuid = $2",
                                Clan.next_league(data4[0]["clan_league"]),
                                data[0]["clan_uuid"],
                            )

                monsdc = data[0]["monsters_jailed"]
                if monsdc is None:
                    await self.bot.db.execute(
                        "UPDATE cuppy SET monsters_jailed = array_append(monsters_jailed, $1) WHERE user_id = $2",
                        monster,
                        ctx.author.id,
                    )
                else:
                    if monster not in monsdc:
                        await self.bot.db.execute(
                            "UPDATE cuppy SET monsters_jailed = array_append(monsters_jailed, $1) WHERE user_id = $2",
                            monster,
                            ctx.author.id,
                        )

                await mex.edit(
                    content=f"{team_emoji} **{team_name}** landed a {jmove_emoji} **{jmove_name}** and succesfully jailed {mon_emoji} **{mon_name}**!",
                    embed=discord.Embed(
                        title=f"Congratulations, {ctx.author.name}!",
                        description=f"{team_emoji} **{team_name}** jailed {mon_emoji} **{mon_name}**!",
                        color=col,
                    )
                    .set_image(url=mon_im)
                    .set_footer(
                        text=f"※ Rarity: {mon_rar_str}\n\n═════ Reward ═════\n[★] You've earned {mon_cup} cupcakes!\n"
                    ),
                )

                if len(mexuses) > 1:
                    return await ctx.send(mexuses)
                return
            else:
                jchancec = random.randint(1, 100)

                jmove = None

                if jchancec in range(1, 20):
                    jmove = random.choice(basic_moves)
                elif jchancec in range(20, 75):
                    jmove = random.choice(special_moves)
                else:
                    jmove = ultra_moves

                jmove_name = Team.get_move_name(jmove)
                jmove_emoji = Team.move_emoji(jmove)

                await mex.edit(
                    content=f"{team_emoji} **{team_name}** landed a {jmove_emoji} **{jmove_name}** but failed jailing {mon_emoji} **{mon_name}**..",
                    embed=discord.Embed(
                        title="Monster Escaped..",
                        description=f"{team_emoji} **{team_name}** failed jailing {mon_emoji} **{mon_name}**..",
                        color=col,
                    ).set_image(url=mon_im),
                )

                if len(mexuses) > 1:
                    return await ctx.send(mexuses)
                return

        if msg.content.lower() in ["escape", "run"]:
            if data[0]["balance"] >= 5:
                await self.bot.db.execute(
                    "UPDATE cuppy SET balance = $1 WHERE user_id = $2",
                    data[0]["balance"] - 50,
                    ctx.author.id,
                )

            if data[0]["uuid_clan"]:
                data3 = await self.bot.db.fetch(
                    "SELECT * FROM clans WHERE clan_uuid = $1", data[0]["uuid_clan"]
                )
                await self.bot.db.execute(
                    "UPDATE clans SET clan_escapes = $1 WHERE clan_uuid = $2",
                    data3[0]["clan_escapes"] + 1,
                    data[0]["uuid_clan"],
                )
                await self.bot.db.execute(
                    "UPDATE clans SET clan_xp = $1 WHERE clan_uuid = $2",
                    data3[0]["clan_xp"] + random.randint(1, 45),
                    data[0]["uuid_clan"],
                )
                data4 = await self.bot.db.fetch(
                    "SELECT * FROM clans WHERE clan_uuid = $1", data[0]["uuid_clan"]
                )
                if data4[0]["clan_xp"] >= Clan.needed_xp(data4[0]["clan_league"]):
                    if Clan.needed_xp(data4[0]["clan_league"]) is not None:
                        await self.bot.db.execute(
                            "UPDATE clans SET clan_league = $1 WHERE clan_uuid = $2",
                            Clan.next_league(data4[0]["clan_league"]),
                            data[0]["clan_uuid"],
                        )

            await mex.edit(
                content=f"{ctx.author.mention} ran away with {team_emoji} **{team_name}**..",
                embed=discord.Embed(
                    title="You escaped..",
                    description=f"{mon_emoji} **{mon_name}** ran in the opposite direction..",
                    color=col,
                ).set_image(url=mon_im),
            )

            if len(mexuses) > 1:
                return await ctx.send(mexuses)
            return

    @commands.group(
        help="Clan main command, check subcommands for actions.",
        aliases=["c"],
        invoke_without_command=True,
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def clan(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        if not data[0]["uuid_clan"]:
            return await ctx.send(f"{ctx.author.mention} you are not in any clan!")

        data2 = await self.bot.db.fetch(
            "SELECT * FROM clans WHERE clan_uuid = $1", data[0]["uuid_clan"]
        )

        name = data2[0]["clan_name"]
        description = data2[0]["clan_description"]
        members = data2[0]["clan_members"]
        xp = data2[0]["clan_xp"]
        league = data2[0]["clan_league"]
        donations = data2[0]["clan_donations"]
        owner = data2[0]["clan_owner_id"]

        created_at = data2[0]["clan_timestamp"]
        f_created_at = f"<t:{int(created_at)}>"
        joined_at = (
            f"{f_created_at}"
            if ctx.author.id == owner
            else f"<t:{int(data[0]['clan_join'])}>"
        )

        hunts = data2[0]["clan_hunts"]
        jails = data2[0]["clan_jails"]
        mines = data2[0]["clan_mines"]
        defeats = data2[0]["clan_defeats"]
        escapes = data2[0]["clan_escapes"]
        battles = data2[0]["clan_battles"]

        await ctx.send(
            embed=discord.Embed(
                description=f"📅 **Created**: {f_created_at}\n📝 **Name**: {name}\n<:owner:871001714529009694> **Owner**: {self.bot.get_user(owner).name or (await self.bot.fetch_user(owner).name)}\n\n═════ `Description` ═════\n{description or 'This clan has no description set yet.'}\n\n═════ `Clan Information` ═════\n"
                f"{Clan.league_emoji(league)} **League**: {Clan.league_name(league)}\n📊 **Next League**: `{humanize.intcomma(xp)} / {humanize.intcomma(Clan.needed_xp(league))}` experience\n"
                f"👥 **Members**: {members} / {Clan.max_members(league)}\n<:cupcake:845632403405012992> **Treasurery**: `{humanize.intcomma(donations)}`\n\n"
                f"═════ `Clan Stats` ═════\n🔎 **Hunts**: {humanize.intcomma(hunts)} | ⛏ **Mines**: {humanize.intcomma(mines)}\n"
                f"🦴 **Defeats**: {humanize.intcomma(defeats)} | ⛓ **Jails**: {humanize.intcomma(jails)}\n"
                f"🏃‍♂️ **Escapes**: {humanize.intcomma(escapes)} | ⚔ **Battles**: {humanize.intcomma(battles)}\n\n"
                f"═════ `Your Information` ═════\n📅 **Joined**: {joined_at}",
                color=self.bot.color,
            )
            .set_footer(text=f"Clan UUID: {data[0]['uuid_clan']}")
            .set_thumbnail(url=Clan.league_image(league))
            .set_author(name="Ami Clan System", icon_url=self.bot.user.avatar_url)
        ) or await ctx.invoke(**{"command": "clan"})

    @clan.command(
        help="Rename your clan if you don't like anymore the name (must be the clan owner)."
    )
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def rename(self, ctx, *, new_name):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        if not data[0]["uuid_clan"]:
            return await ctx.send(f"{ctx.author.mention} you are not in any clan.")

        data2 = await self.bot.db.fetch(
            "SELECT * FROM clans WHERE clan_uuid = $1", data[0]["uuid_clan"]
        )

        if data2[0]["clan_owner_id"] != ctx.author.id:
            return await ctx.send(
                f"{ctx.author.mention} only the clan owner can set / edit the clan name."
            )

        await self.bot.db.execute(
            "UPDATE clans SET clan_name = $1 WHERE clan_uuid = $2",
            new_name,
            data[0]["uuid_clan"],
        )
        await ctx.send(
            f"{ctx.author.mention} the clan name was succesfully edited to **{new_name}**!"
        )

    @clan.command(
        help="Set / Edit the clan description (must be the clan owner).",
        aliases=["desc"],
    )
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def description(self, ctx, *, clan_description):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        if not data[0]["uuid_clan"]:
            return await ctx.send(f"{ctx.author.mention} you are not in any clan.")

        data2 = await self.bot.db.fetch(
            "SELECT * FROM clans WHERE clan_uuid = $1", data[0]["uuid_clan"]
        )

        if data2[0]["clan_owner_id"] != ctx.author.id:
            return await ctx.send(
                f"{ctx.author.mention} only the clan owner can set / edit the clan description."
            )

        await self.bot.db.execute(
            "UPDATE clans SET clan_description = $1 WHERE clan_uuid = $2",
            clan_description,
            data[0]["uuid_clan"],
        )
        await ctx.send(
            f"{ctx.author.mention} the clan description was succesfully edited!"
        )

    @clan.command(
        help="Create a clan and invite members into it to raise it in the top of the leaderboard, grind leagues and much more!"
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def create(self, ctx, *, name: str):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        c = data[0]["uuid_clan"]
        if c:
            return await ctx.send(
                f"{ctx.author.mention} you are already in a clan (UUID: `{c}`), leave this clan before creating a new one."
            )

        bal = data[0]["balance"]
        if bal < 50000:
            return await ctx.send(
                f"{ctx.author.mention} you need <:cupcake:845632403405012992> **50,000** to create a clan."
            )

        if len(name) > 20:
            return await ctx.send(
                f"{ctx.author.mention} the name can't be longer than 20 characters."
            )

        data2 = await self.bot.db.fetch("SELECT * FROM clans")

        for cln in data2:
            n = cln["clan_name"]
            if name.lower() == n.lower():
                return await ctx.send(
                    f"{ctx.author.mention} there's already a clan with this name, try again."
                )

        gen_id = uuid.uuid1()
        date = str(int(datetime.datetime.utcnow().timestamp()))
        await self.bot.db.execute(
            "INSERT INTO clans (clan_uuid, clan_name, clan_owner_id, clan_league, clan_timestamp) VALUES ($1, $2, $3, $4, $5)",
            str(gen_id),
            name,
            ctx.author.id,
            "silver",
            date,
        )
        await asyncio.sleep(2)
        await self.bot.db.execute(
            "UPDATE cuppy SET uuid_clan = $1, clan_join = $2, balance = $3 WHERE user_id = $4",
            str(gen_id),
            int(date),
            data[0]["balance"] - 50000,
            ctx.author.id,
        )
        await ctx.send(
            f"🎊 {ctx.author.mention} your clan **{name}** was succesfully created!\n"
            f"<:alert_pink:867758260707000380> Check the clan info with `ami clan info`!\n"
            f"<:alert_pink:867758260707000380> Invite new members with `ami clan invite @member`!\n"
            f"<:alert_pink:867758260707000380> Raise you clan league and be the first in the leaderboard!"
        )

    @clan.command(
        help="Delete the clan and remove all the members from it (must be the clan owner).",
        aliases=["del"],
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def delete(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        data2 = await self.bot.db.fetch(
            "SELECT * FROM clans WHERE clan_uuid = $1", data[0]["uuid_clan"]
        )

        if not data2:
            return await ctx.send(f"{ctx.author.mention} you are not owner of any clan.")

        if data2[0]["clan_owner_id"] != ctx.author.id:
            return await ctx.send(
                f"{ctx.author.mention} you are not the owner of this clan, you can't delete it."
            )

        name = data2[0]["clan_name"]
        league = data2[0]["clan_league"]
        uuid = data2[0]["clan_uuid"]

        mc = await ctx.send(
            f"❗ {ctx.author.mention} you are going to delete {Clan.league_emoji(league)} **{name}**, are you sure?\n"
            f'**`Deleting the clan will not refund any clan donation to the clan members`**\n<:alert_pink:867758260707000380> Type the clan UUID (`{uuid}`) to confirm or "DECLINE" to abort in 30 seconds.'
        )

        try:
            mex = await self.bot.wait_for(
                "message",
                check=lambda m: m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id
                and m.content.lower() in [uuid, "decline"],
                timeout=30,
            )
        except asyncio.TimeoutError:
            await mc.delete()
            return

        if mex.content.lower() == uuid.lower():
            await self.bot.db.execute("DELETE FROM clans WHERE clan_uuid = $1", uuid)
            await asyncio.sleep(2)
            dc = await self.bot.db.fetch("SELECT * FROM cuppy")
            for i in dc:
                if i["uuid_clan"] == uuid:
                    await self.bot.db.execute(
                        "UPDATE cuppy SET uuid_clan = $1, clan_join = $2 WHERE user_id = $3",
                        None,
                        None,
                        i["user_id"],
                    )

            await ctx.send(
                f"📍 {ctx.author.mention} you have succesfully deleted {Clan.league_emoji(league)} **{name}**, all the members has been kicked and the clan does not exist anymore."
            )
            return

        elif mex.content.lower() == "decline":
            await mc.delete()
            return

    @clan.command(
        help="Kick a member from the clan, must be mentioned or use the member ID."
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def kick(self, ctx, member: discord.Member):
        if member.id == ctx.author.id:
            return await ctx.send(f"{ctx.author.mention} you can't kick yourself.")

        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        if not data[0]["uuid_clan"]:
            return await ctx.send(f"{ctx.author.mention} you are not in any clan.")

        data2 = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", member.id
        )

        data3 = await self.bot.db.fetch(
            "SELECT * FROM clans WHERE clan_uuid = $1", data[0]["uuid_clan"]
        )

        if data3[0]["clan_owner_id"] != ctx.author.id:
            return await ctx.send(
                f"{ctx.author.mention} only the clan owner can kick other members."
            )

        if not data2:
            return await ctx.send(
                f"{ctx.author.mention} the member that you've mentioned is not registered into cuppy."
            )

        if not data2[0]["uuid_clan"]:
            return await ctx.send(
                f"{ctx.author.mention} this member is not in any clan."
            )

        if data2[0]["uuid_clan"] != data[0]["uuid_clan"]:
            return await ctx.send(
                f"{ctx.author.mention} this member is not in your clan."
            )

        await self.bot.db.execute(
            "UPDATE cuppy SET uuid_clan = $1, clan_join = $2 WHERE user_id = $3",
            None,
            None,
            member.id,
        )
        await self.bot.db.execute(
            "UPDATE clans SET clan_members = $1 WHERE clan_uuid = $2",
            data3[0]["clan_members"] - 1,
            data[0]["uuid_clan"],
        )
        await ctx.send(
            f"📝 {ctx.author.mention} you have succesfully kicked **{member.name}#{member.discriminator}** from the clan."
        )

    @clan.command(help="Leave the clan where you're are in.")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def leave(self, ctx):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        if not data[0]["uuid_clan"]:
            return await ctx.send(f"{ctx.author.mention} you are not in any clan.")

        data2 = await self.bot.db.fetch(
            "SELECT * FROM clans WHERE clan_uuid = $1", data[0]["uuid_clan"]
        )

        if ctx.author.id == data2[0]["clan_owner_id"]:
            return await ctx.send(
                f"{ctx.author.mention} you are the owner of the clan, use `ami clan delete` if you want to delete it."
            )

        name = data2[0]["clan_name"]
        league = data2[0]["clan_league"]
        uuid = data2[0]["clan_uuid"]
        emo = Clan.league_emoji(league)

        mc = await ctx.send(
            f'{ctx.author.mention} you\'re going to leave {emo} **{name}**, are you sure?\nType the clan UUID (`{uuid}`) in the chat to confirm or "DECLINE" to abort in 30 seconds.'
        )

        try:
            mex = await self.bot.wait_for(
                "message",
                check=lambda m: m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id
                and m.content.lower() in [uuid, "decline"],
                timeout=30,
            )
        except asyncio.TimeoutError:
            await mc.delete()
            return

        if mex.content.lower() == uuid.lower():
            await self.bot.db.execute(
                "UPDATE clans SET clan_members = $1 WHERE clan_uuid = $2",
                data2[0]["clan_members"] - 1,
                uuid,
            )
            await self.bot.db.execute(
                "UPDATE cuppy SET clan_join = $1, uuid_clan = $2 WHERE user_id = $3",
                None,
                None,
                ctx.author.id,
            )
            await ctx.send(
                f"💼 {ctx.author.mention} succesfully left {emo} **{name}** (`{uuid}`)"
            )
            await mc.delete()
            return

        elif mex.content.lower() == "decline":
            await mc.delete()
            return

    @clan.command(
        help="Invite some members into your clan to can farm toghether and league up faster!"
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def invite(self, ctx, user: discord.Member):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        if not data[0]["uuid_clan"]:
            return await ctx.send(
                f"{ctx.author.mention} you need to be in a clan to invite members."
            )

        data2 = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", user.id
        )
        if not data2:
            return await ctx.send(
                f"{ctx.author.mention} looks like {user.name} is not registered into cuppy."
            )

        if data2[0]["uuid_clan"] == data[0]["uuid_clan"]:
            return await ctx.send(
                f"{ctx.author.mention} this member is already into your clan."
            )

        if data2[0]["uuid_clan"]:
            return await ctx.send(
                f"{ctx.author.mention}, {user.name} is already in a clan (UUID: `{data2[0]['uuid_clan']}`)"
            )

        if data2[0]["lifetime_earns"] < 750:
            return await ctx.send(
                f"{ctx.author.mention}, you can't invite {user.name} in the clan because he/she has less than <:cupcake:845632403405012992> **750** lifetime earned."
            )

        data3 = await self.bot.db.fetch(
            "SELECT * FROM clans WHERE clan_uuid = $1", data[0]["uuid_clan"]
        )

        if data3[0]["clan_members"] >= Clan.max_members(data3[0]["clan_league"]):
            return await ctx.send(
                f"{ctx.author.mention} you can't invite other members into the clan, the capacity is full: go to the next league to increase the capacity or kick someone from the guild."
            )

        mc = await ctx.send(
            f"{ctx.author.mention} has invited {user.mention} into:\n<:alert_pink:867758260707000380> **{Clan.league_emoji(data3[0]['clan_league'])} {data3[0]['clan_name']}** (UUID: `{data3[0]['clan_uuid']}`)\n"
            f'{user.mention} please type "CONFIRM" to accept or "DECLINE" to abort in 30 seconds.'
        )

        try:
            mex = await self.bot.wait_for(
                "message",
                check=lambda m: m.author.id == user.id
                and m.channel.id == ctx.channel.id
                and m.content.lower() in ["confirm", "decline"],
                timeout=30,
            )
        except asyncio.TimeoutError:
            await mc.delete()
            return

        if mex.content.lower() == "confirm":
            date = str(int(datetime.datetime.utcnow().timestamp()))
            await self.bot.db.execute(
                "UPDATE clans SET clan_members = $1 WHERE clan_uuid = $2",
                data3[0]["clan_members"] + 1,
                data[0]["uuid_clan"],
            )
            await self.bot.db.execute(
                "UPDATE cuppy SET uuid_clan = $1, clan_join = $2 WHERE user_id = $3",
                data[0]["uuid_clan"],
                int(date),
                user.id,
            )
            await mc.delete()
            await ctx.send(
                f"🎉 {ctx.author.mention}, i'm happy to announce that {user.mention}... has accepted the invite!"
            )
            return

        elif mex.content.lower() == "decline":
            await ctx.send(
                f"🎉 {ctx.author.mention}, something went wrong, **{user.name}** has declined your invite."
            )
            await mc.delete()
            return

    @clan.command(
        help="Donate some cupcakes to the clan, they will be sent into the treasurery.",
        aliases=["don"],
    )
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def donate(self, ctx, amount: int):
        if amount < 10000:
            return await ctx.send(
                f"{ctx.author.mention} the minimum donation is <:cupcake:845632403405012992> **10,000**."
            )

        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id
        )
        if not data:
            return await ctx.invoke(self.balance)

        if not data[0]["uuid_clan"]:
            return await ctx.send(f"{ctx.author.mention} you are not in any clan!")

        data2 = await self.bot.db.fetch(
            "SELECT * FROM clans WHERE clan_uuid = $1", data[0]["uuid_clan"]
        )

        don = data2[0]["clan_donations"]

        if amount > data[0]["balance"]:
            return await ctx.send(
                f"{ctx.author.mention} you have only <:cupcake:845632403405012992> **{humanize.intcomma(data[0]['balance'])}**, you can't donate <:cupcake:845632403405012992> **{humanize.intcomma(amount)}**."
            )

        await self.bot.db.execute(
            "UPDATE clans SET clan_donations = $1 WHERE clan_uuid = $2",
            don + amount,
            data[0]["uuid_clan"],
        )
        await self.bot.db.execute(
            "UPDATE cuppy SET balance = $1 WHERE user_id = $2",
            data[0]["balance"] - amount,
            ctx.author.id,
        )
        await ctx.send(
            f"{ctx.author.mention} you've succesfully donated <:cupcake:845632403405012992> **{humanize.intcomma(amount)}** to {Clan.league_emoji(data2[0]['clan_league'])} **{data2[0]['clan_name']}**!"
        )

    @commands.command()
    @is_team()
    async def devgift(self, ctx, member: discord.Member, amount: int):
        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", member.id
        )
        await self.bot.db.execute(
            "UPDATE cuppy SET balance = $1 WHERE user_id = $2",
            data[0]["balance"] + amount,
            member.id,
        )
        await ctx.message.add_reaction("✅")

    @commands.command()
    @is_team()
    async def devbox(self, ctx, type: str, amount: int, member: discord.Member = None):
        if member is None:
            member = ctx.author

        data = await self.bot.db.fetch(
            "SELECT * FROM cuppy WHERE user_id = $1", member.id
        )
        if not data:
            return await ctx.message.add_reaction("❌")

        valid_lbs = ["common", "uncommon", "rare", "epic"]
        if type.lower() not in valid_lbs:
            return await ctx.message.add_reaction("❌")

        emoji = Lootbox.emoji(type.lower())
        name = Lootbox.name(type.lower())

        await self.bot.db.execute(
            f"UPDATE cuppy SET lootbox_{type.lower()} = $1 WHERE user_id = $2",
            data[0][f"lootbox_{type.lower()}"] + amount,
            member.id,
        )
        return await ctx.send(
            f"🎉 {member.mention} received {emoji} {amount}x **{name}** from {ctx.author.mention}!"
        )

    @commands.command()
    @is_team()
    async def image_captcha(self, ctx, font: str = None):
        if font is None:
            font = "standard"

        c = []

        for f in os.listdir("./fonts"):
            if f.endswith(".ttf"):
                c.append(f.strip(".ttf"))

        if font not in c:
            return await ctx.send("font not found.")

        image = ImageCaptcha(fonts=[f"fonts/{font}.ttf"])
        number = random.randint(1000, 99999)
        data = image.generate(str(number))
        buffer = BytesIO()
        image.write(str(number), buffer)
        buffer.seek(0)
        await ctx.send(file=discord.File(fp=buffer, filename="captcha.png"))


def setup(bot):
    bot.add_cog(Cuppy(bot))

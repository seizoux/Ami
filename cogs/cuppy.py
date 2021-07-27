import discord
from discord.ext import commands, tasks
import datetime
import random
import asyncio
import humanize
from util.defs import is_team

class Monster:
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
            "chaos dragon": "https://cdn.discordapp.com/attachments/869250340925624371/869559988207620166/chaos_dragon.png"
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
            "chaos dragon"
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
            "chaos dragon": "<:chaos_dragon:869555190951464990>"
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
            "chaos dragon": "Chaos Dragon"
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
            "slime": 5,
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
            "nergigante": 25,
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
            "chaos dragon": 100
        }

        return xp[monster]

    def get_hp(monster: str):
        hp = {
            "skull slime": 50,
            "silver crocodile": 50,
            "shadow": 50,
            "pumpkin witch": 50,
            "orc tauros": 150,
            "demon spirit": 150,
            "dark dragon": 200,
            "blue dragon": 200,
            "bat": 50,
            "ancient golem": 150,
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
            "devil octopus": 100,
            "decalion": 300,
            "cthulhu": 250,
            "chica": 100,
            "holidoom": 300,
            "quetzalcoatl": 300,
            "wolf fighter": 100,
            "stone golem": 100,
            "sea girl": 50,
            "sam": 150,
            "rathian": 200,
            "nergigante": 100,
            "magician": 50,
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
            "bugbear": 50,
            "chaos dragon": 300
        }

        return hp[monster]

    def cup_drop(monster: str):
        cup = {
            "skull slime": 1,
            "silver crocodile": 1,
            "shadow": 3,
            "pumpkin witch": 3,
            "orc tauros": 3,
            "demon spirit": 3,
            "dark dragon": 5,
            "blue dragon": 5,
            "bat": 1,
            "ancient golem": 3,
            "zombie": 1,
            "slime": 1,
            "skeleton": 1,
            "red oricorio": 5,
            "oricorio": 3,
            "molten iron golem": 10,
            "minotaur king": 10,
            "minotaur": 3,
            "magala": 15,
            "imperial dragon": 15,
            "ice dragon": 5,
            "grodd gorilla": 5,
            "godzilla": 10,
            "galaxy dragon": 10,
            "fire magician": 3,
            "devil octopus": 3,
            "decalion": 15,
            "cthulhu": 3,
            "chica": 3,
            "holidoom": 15,
            "quetzalcoatl": 10,
            "wolf fighter": 3,
            "stone golem": 1,
            "sea girl": 3,
            "sam": 5,
            "rathian": 10,
            "nergigante": 5,
            "magician": 3,
            "magala final form": 15,
            "laymon": 15,
            "kukulkan": 10,
            "ice golem": 5,
            "ice dino": 3,
            "gtruo": 3,
            "fat reaper": 1,
            "demon horse": 3,
            "demon girl": 5,
            "crystal golem": 10,
            "bugbear": 1,
            "chaos dragon": 15
        }

        return cup[monster]

class Team:
    def get_moves(team_name:str):
        moves = {
            "kury": {"base": ["punch", "kick"], "special" : ["energy beam", "tails smash"], "ultra": "evil eyes"},
            "anny": {"base": ["punch", "kick"], "special" : ["tsunami", "wave sonar"], "ultra": "ice realm"},
            "fatima": {"base": ["punch", "kick"], "special" : ["energy ball", "fairy fate"], "ultra": "dream dimension"},
            "lilly": {"base": ["punch", "kick"], "special" : ["loud cry", "crying punch"], "ultra": "water spin"},
            "luna": {"base": ["punch", "kick"], "special" : ["angry fist", "power fist"], "ultra": "ultra fist"},
            "celia": {"base": ["punch", "kick"], "special" : ["black hole", "big bang"], "ultra": "void gateway"},
            "micky": {"base": ["punch", "kick"], "special" : ["hammer smash", "pick-tick"], "ultra": "mjolnir"},
            "vanessa": {"base": ["punch", "kick"], "special" : ["last flame", "subzero flame"], "ultra": "meteor fall"},
            "ornella": {"base": ["punch", "kick"], "special" : ["ZzZ", "ZzZ 2"], "ultra": "ZzZ 3"}
        }

        return moves[team_name]

    def move_emoji(move_name:str):
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
            "dream dimension": "<:dream_dimension:869203680048586833>"
        }

        return emojises[move_name]

    def get_move_name(move_name:str):
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
            "dream dimension": "Dream Dimension"
        }        

        return nameses[move_name]

    def get_move_base_damage(move_name:str):
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
            "dream dimension": 130
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
            "kury": {"atk": 20, "def": 10, "spd": 10, "hp": 25, "mag": 20, "luck": 15},
            "anny": {"atk": 18, "def": 14, "spd": 15, "hp": 16, "mag": 18, "luck": 12},
            "fatima": {"atk": 19, "def": 10, "spd": 14, "hp": 15, "mag": 10, "luck": 13},
            "lilly": {"atk": 15, "def": 10, "spd": 10, "hp": 16, "mag": 15, "luck": 12},
            "luna": {"atk": 16, "def": 13, "spd": 15, "hp": 18, "mag": 11, "luck": 17},
            "celia": {"atk": 19, "def": 18, "spd": 13, "hp": 15, "mag": 18, "luck": 15},
            "micky": {"atk": 20, "def": 15, "spd": 10, "hp": 17, "mag": 19, "luck": 15},
            "vanessa": {"atk": 18, "def": 13, "spd": 14, "hp": 16, "mag": 15, "luck": 16},
            "ornella": {"atk": 19, "def": 15, "spd": 15, "hp": 10, "mag": 15, "luck": 13}
        }

        return team_ivs[team_name]

    def ivs_level_based(team_name:str, level:int):
        final_ivs = {}
        team = Team.ivs(team_name)
        for k, v in team.items():
            for i in range(0, level):
                v += 3
                final_ivs[k] = v

        return final_ivs

class Exchange:
    def calculate_exc(mineral:str, amount:int):
        exc = {
        "bronze": 250,
        "silver": 125,
        "gold": 25,
        "diamond": 5
        }
  
        return int(amount / exc[mineral])

    def exc_info(mineral:str):
        exci = {
        "bronze": 250,
        "silver": 125,
        "gold": 25,
        "diamond": 5
        }

        return exci[mineral]

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

    """async def cog_check(self, ctx):
        team = [144126010642792449, 410452466631442443, 711057339360477184, 590323594744168494, 691406006277898302, 343019667511574528]
        return ctx.author.id in team"""

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cuppy Loaded")

    @commands.group(aliases=["min"], help="Check your minerals, see minerals exchange values.", invoke_without_command=True)
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def minerals(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command":"minerals"})

    @minerals.command(aliases=["inv"])
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def inventory(self, ctx):
        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
        if not data:
            return await ctx.invoke(self.test_balance)

        bronze = data[0]["bronze"]
        silver = data[0]["silver"]
        gold = data[0]["gold"]
        diamond = data[0]["diamond"]

        await ctx.send(f"{ctx.author.mention} you currently have "
        f"{Mineral.emoji('bronze')} {bronze}x "
        f"{Mineral.emoji('silver')} {silver}x "
        f"{Mineral.emoji('gold')} {gold}x "
        f"{Mineral.emoji('diamond')} {diamond}x ")

    @minerals.command(aliases=["val"])
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def values(self, ctx):

        mines = ["bronze", "silver", "gold", "diamond"]

        cv = []

        for i in mines:
            name = Mineral.name(i)
            emoji = Mineral.emoji(i)
            exc = Exchange.exc_info(i)
            cv.append(f"`{exc}x` {emoji} **{name}** × <:cupcake:845632403405012992> **1**")

        c = '\n'.join(cv)
        await ctx.send(embed = discord.Embed(
            title = "Minerals Values",
            description = f"Listed you can see all the values according to the mineral type"
            f" for exchanges.\nE.g : if you trade `250` bronze, you will get 1 cupcake!\n\n{c}",
            color = self.bot.color)
            )


    @commands.command(aliases=["pro"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def profile(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        if not member:
            data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
            if not data:
                return await ctx.invoke(self.test_balance)
        
        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", member.id)
        if not data:
            return await ctx.send(f"<:alert_pink:867758260707000380> **{member.name}#{member.discriminator}** seems to be not registered into cuppy.")

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

        ivs = Team.ivs_level_based(team, level)

        atk = ivs["atk"]
        defe = ivs["def"]
        speed = ivs["spd"]
        hp = ivs["hp"]
        magic = ivs["mag"]
        luck = ivs["luck"]

        if team:
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
            color = self.bot.color
            )

        em.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=em)

    @commands.command(aliases=["gift"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def give(self, ctx, member : discord.Member, amount: int):
        if member == ctx.author:
            return await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} you can't gift to yourself.")

        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
        if not data:
            return await ctx.invoke(self.test_balance)

        data2 = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", member.id)
        if not data2:
            return await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} looks like **{member.name}#{member.discriminator}** is not registered into cuppy.")

        pick_earns = data2[0]["lifetime_earns"]
        if not pick_earns:
            return await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} you can't give <:cupcake:845632403405012992> to **{member.name}#{member.discriminator}** because he has less than <:cupcake:845632403405012992> **750** earned since started.")
        
        if pick_earns <= 750:
            return await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} you can't give <:cupcake:845632403405012992> to **{member.name}#{member.discriminator}** because he has less than <:cupcake:845632403405012992> **750** earned since started.")

        bal = data[0]["balance"]
        if amount > bal:
            return await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} you have only <:cupcake:845632403405012992> **{humanize.intcomma(bal)}**")

        await self.bot.db.execute("UPDATE cuppy SET balance = $1 WHERE user_id = $2", data[0]["balance"] - amount, ctx.author.id)
        await self.bot.db.execute("UPDATE cuppy SET balance = $1 WHERE user_id = $2", data2[0]["balance"] + amount, member.id)
        await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} sent <:cupcake:845632403405012992> **{humanize.intcomma(amount)}** to {member.mention}")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def test_balance(self, ctx):
        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
        if not data:
            date_today = str(int(datetime.datetime.utcnow().timestamp()))
            await self.bot.db.execute("INSERT INTO cuppy (user_id, balance, pickaxe_type, pickaxe_exp, pickaxe_durability, pickaxe_earnings, pickaxe_diamonds, pickaxe_golds, pickaxe_silvers, pickaxe_bronzes, pickaxe_needed_xp, bronze, silver, gold, diamond, join_date) VALUES ($1, 10, $2, 0, 100, 0, 0, 0, 0, 0, $3, 0, 0, 0, 0, $4)", ctx.author.id, "wood", 3500, date_today)
            return await ctx.send(f"{ctx.author.mention} **your balance is now ready!**\n<:alert_pink:867758260707000380> Earn minerals mining with your pickaxe using `ami mine`!\n"
                        f"<:alert_pink:867758260707000380> Vote to get <:lootbox:867758260622590002> and (**luckily**) <:uncommon:867764757733834793> <:rare:867764757670002698> or <:epic:867764757708406824> with `ami vote`!\n"
                        f"<:alert_pink:867758260707000380> Upgrade your pickaxe to even more good ones (<:nebula_pickaxe:862694657959395348> <:sky_pickaxe:862694658055340032> <:divine_pickaxe:862694657891631114>) with `ami pickaxe upgrade`!\n"
                        f"<:alert_pink:867758260707000380> Exchange the minerals you've got for <:cupcake:845632403405012992> with `ami exchange <mineral_name> <amount>`! Check `ami minerals values` for values of minerals!\n"
                        f"<:alert_pink:867758260707000380> Create your own clan, invite friends into it and raise it to the top!")

        bal = data[0]["balance"]
        await ctx.send(f"{ctx.author.mention} you currently have <:cupcake:845632403405012992> **{humanize.intcomma(bal)} Cupcakes!**")

    @commands.command(aliases=["exc"])
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

        needed = Exchange.exc_info(mineral_name.lower())
        if min < needed:
            return await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} you need at least {needed}x {emoji} to exchange for <:cupcake:845632403405012992> cupcakes.")

        exc = Exchange.calculate_exc(mineral_name.lower(), amount)
        await self.bot.db.execute(f"UPDATE cuppy SET {mineral_name.lower()} = $1, balance = $2, lifetime_earns = $3 WHERE user_id = $4", data[0][mineral_name.lower()] - amount, data[0]["balance"] + exc, data[0]["lifetime_earns"] + exc, ctx.author.id)
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
        await self.bot.db.execute("UPDATE cuppy SET balance = $1, lifetime_earns = $2 WHERE user_id = $3", data[0]["balance"] + cups, data[0]["lifetime_earns"] + cups, ctx.author.id)
        await self.bot.db.execute(f"UPDATE cuppy SET {lootbox_rarity.lower()}_opened = $1 WHERE user_id = $2", data[0][f"{lootbox_rarity.lower()}_opened"] + amount, ctx.author.id)

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
            await ctx.send(f"<:alert_pink:867758260707000380> Congratulations, **{ctx.author.name}**! You pickaxe was upgraded to {emoji} **{name}!**")
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
            return await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.name}, your {emoji} **{name}** durability is **0 / 100**, recharge it with `ami pickaxe recharge`!")

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
            await self.bot.db.execute("UPDATE cuppy SET balance = $1, pickaxe_earnings = $2, lifetime_earns = $3 WHERE user_id = $4", data2[0]["balance"] + fg, data2[0]["pickaxe_earnings"] + fg, data2[0]["lifetime_earns"] + fc, ctx.author.id)
            
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
            f"<:alert_pink:867758260707000380> This will reset all the stats (IVs, Level, XP, Wins Loses, Draws).\n<:alert_pink:867758260707000380> Reply in 30 seconds with \"CONFIRM\" to continue or with \"DECLINE\" to abort.")

            try:
                msg = await self.bot.wait_for("message", check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.content.lower() in ["confirm", "decline"], timeout = 30)
            except asyncio.TimeoutError:
                await msg_b.delete()
                return

            if msg.content.lower() == "confirm":
                fcg = Team.calc_needed_xp(0)
                await self.bot.db.execute("UPDATE cuppy SET team_name = $1, team_needed_xp = $2, team_wins = $3, team_loses = $4, team_ties = $5, team_level = $6, team_xp = $7, balance = $8 WHERE user_id = $9", teammate_name.lower(), fcg, 0, 0, 0, 1, 0, data[0]["balance"] - 500, ctx.author.id)

                await ctx.send(f"{ctx.author.mention} you've succesfully replaced your {t_emoji} **{t_name}** with {emoji} **{name}** for <:cupcake:845632403405012992> **500**!\n⚔ `{atk}` 🛡 `{defe}`\n👟 `{speed}` ❤ `{hp}`\n✨ `{magic}` 🍀 `{luck}`")

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

        b_final = '\n'.join(basic_final)
        s_final = '\n'.join(special_final)
        u_final = f"{emoji3} **{name3}** | 💥 {damage3}"

        exp = data[0]["team_xp"]
        level = data[0]["team_level"]
        needed_xp = data[0]["team_needed_xp"]
        wins = data[0]["team_wins"]
        loses = data[0]["team_loses"]
        draws = data[0]["team_ties"]
        friendship = data[0]["team_friendship"]

        ivs = Team.ivs_level_based(teammate, level)

        atk = ivs["atk"]
        defe = ivs["def"]
        speed = ivs["spd"]
        hp = ivs["hp"]
        magic = ivs["mag"]
        luck = ivs["luck"]

        if friendship > 100:
            friendship = 100

        f_cs = ((friendship)/100)*100
        f_calc = round(f_cs,2)

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
        f"🥈 **Loses**: {humanize.intcomma(loses)}\n"
        f"🥉 **Draws**: {humanize.intcomma(draws)}")
        em.add_field(name="Moveset", value=f"{b_final}\n{s_final}\n{u_final}")
        em.set_thumbnail(url=img)
        em.set_footer(text=f"× Friendship: {f_calc}%")

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

    @commands.command(aliases=["fight", "b"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
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

        b_msg = await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} challenged {opponent.mention} to a battle!",
                    embed=discord.Embed(color=self.bot.color)
                    .add_field(name=f"{e_team_author} **{n_team_author}** ({ctx.author.name})", value=f"<:level:868426330293821450> **{level_team_author}** <:level:868426330293821450>")
                    .add_field(name=f"{e_team_opponent} **{n_team_opponent}** ({opponent.name})", value=f"<:level:868426330293821450> **{level_team_opponent}** <:level:868426330293821450>")
                    .set_footer(text=f"{opponent.name} in 30 seconds type \"CONFIRM\" to accept or \"DECLINE\" to abort."))

        try:
            msg = await self.bot.wait_for("message", check=lambda m: m.author.id == opponent.id and m.channel.id == ctx.channel.id and m.content.lower() in ["confirm", "decline"], timeout = 30)
        except asyncio.TimeoutError:
            await b_msg.delete()
            return

        if msg.content.lower() == "decline":
            await b_msg.delete()
            return

        if msg.content.lower() == "confirm":
            current_hp_author = hp_team_author
            current_hp_opponent = hp_team_opponent

            em1 = discord.Embed(color = self.bot.color)
            em1.add_field(name=f"{e_team_author} {n_team_author} ({ctx.author.name})", value=f"❤ {humanize.intcomma(current_hp_author)} / {humanize.intcomma(hp_team_author)} ❤")
            em1.add_field(name=f"{e_team_opponent} {n_team_opponent} ({opponent.name})", value=f"❤ {humanize.intcomma(current_hp_opponent)} / {humanize.intcomma(hp_team_opponent)} ❤")

            msg_one = await ctx.send("The match will start in 5 seconds...", embed=em1)

            friend = 1
            await asyncio.sleep(5)

            while True:
                cc_1 = random.choice(range(1, 100))
                if cc_1 in range(1,50):
                    move_author = random.choice(basic_moves_author)
                elif cc_1 in range(50, 95):
                    move_author = random.choice(special_moves_author)
                else:
                    move_author = ultra_moves_author

                cc_2 = random.choice(range(1, 100))
                if cc_2 in range(1,50):
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
                    final_damage_author = (author_move_damage + (int(atk_team_author/5)) + random.randint(40, 100))*2
                else:
                    final_damage_author = (author_move_damage + (int(atk_team_author/5)))*2

                if critical_opponent:
                    final_damage_opponent = (opponent_move_damage + (int(atk_team_opponent/5)) + random.randint(40, 100))*2
                else:
                    final_damage_opponent = (opponent_move_damage + (int(atk_team_opponent/5)))*2

                current_hp_author = current_hp_author - int(final_damage_opponent)
                current_hp_opponent = current_hp_opponent - int(final_damage_author)

                if current_hp_author < 1:
                    current_hp_author = 0

                if current_hp_opponent < 1:
                    current_hp_opponent = 0

                em2 = discord.Embed(color = self.bot.color)
                em2.add_field(name=f"{e_team_author} {n_team_author} ({ctx.author.name})", value=f"❤ {humanize.intcomma(current_hp_author)} / {humanize.intcomma(hp_team_author)} ❤")
                em2.add_field(name=f"{e_team_opponent} {n_team_opponent} ({opponent.name})", value=f"❤ {humanize.intcomma(current_hp_opponent)} / {humanize.intcomma(hp_team_opponent)} ❤")
                em2.set_footer(text="Moves were landed automatically each 5 seconds.")
                m = await ctx.channel.history(limit=5).get(id=msg_one.id)
                if m:
                    await msg_one.edit(content=f"{e_team_author} **{n_team_author}** landed a {author_move_emoji} **{author_move_name}**: that dealt 💥 {humanize.intcomma(final_damage_author)}{mex_crit_author}\n"
                                    f"{e_team_opponent} **{n_team_opponent}** landed a {opponent_move_emoji} **{opponent_move_name}**: that dealt 💥 {humanize.intcomma(final_damage_opponent)}{mex_crit_opponent}")
                    await msg_one.edit(embed=em2)
                else:
                    try:
                        await msg_one.delete()
                    except Exception:
                        pass
                    msg_one = await ctx.send(content = f"{e_team_author} **{n_team_author}** landed a {author_move_emoji} **{author_move_name}**: that dealt 💥 {humanize.intcomma(final_damage_author)}{mex_crit_author}\n"
                                    f"{e_team_opponent} **{n_team_opponent}** landed a {opponent_move_emoji} **{opponent_move_name}**: that dealt 💥 {humanize.intcomma(final_damage_opponent)}{mex_crit_opponent}", embed=em2)

                if current_hp_opponent <= 0 and current_hp_author <= 0 or current_hp_author <= 0 and current_hp_opponent <= 0:
                    await self.bot.db.execute("UPDATE cuppy SET team_ties = $1, team_friendship = $2 WHERE user_id = $3", data1[0]["team_ties"] + 1, data1[0]["team_friendship"] + friend, ctx.author.id)
                    await self.bot.db.execute("UPDATE cuppy SET team_ties = $1, team_friendship = $2 WHERE user_id = $3", data2[0]["team_ties"] + 1, data2[0]["team_friendship"] + friend, opponent.id)
                    await ctx.send(f"{opponent.mention} {ctx.author.mention} the battle between {e_team_author} **{n_team_author}** & {e_team_opponent} **{n_team_opponent}** ended in a draw, no <:xp:867817838941437974> has been given out.")
                    break

                if current_hp_opponent <= 0:
                    xp_amount = 100*level_team_opponent
                    await self.bot.db.execute("UPDATE cuppy SET team_xp = $1, team_wins = $2, team_friendship = $3 WHERE user_id = $4", data1[0]["team_xp"] + xp_amount, data1[0]["team_wins"] + 1, data1[0]["team_friendship"] + friend, ctx.author.id)
                    await self.bot.db.execute("UPDATE cuppy SET team_loses = $1 WHERE user_id = $2", data2[0]["team_loses"] + 1, opponent.id)
                    data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)

                    if data[0]["team_xp"] >= data[0]["team_needed_xp"]:
                        c_nxp = Team.calc_needed_xp(data[0]["team_xp"])
                        await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} {e_team_author} **{n_team_author}** won the battle against {e_team_opponent} **{n_team_opponent}** and gained <:xp:867817838941437974> **{xp_amount}**!\n"
                                        f"<:alert_pink:867758260707000380> Oh! {e_team_author} **{n_team_author}** leveled up to <:level:868426330293821450> **{data[0]['team_level'] + 1}**!")
                        await self.bot.db.execute("UPDATE cuppy SET team_needed_xp = $1, team_level = $2, team_xp = $3 WHERE user_id = $4", c_nxp, data[0]["team_level"] + 1, 0, ctx.author.id)

                        break

                    await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} {e_team_author} **{n_team_author}** won the battle against {e_team_opponent} **{n_team_opponent}** and gained <:xp:867817838941437974> **{xp_amount}**!")
                    break

                elif current_hp_author <= 0:
                    xp_amount = 100*level_team_author
                    await self.bot.db.execute("UPDATE cuppy SET team_xp = $1, team_wins = $2, team_friendship = $3 WHERE user_id = $4", data2[0]["team_xp"] + xp_amount, data2[0]["team_wins"] + 1, data2[0]["team_friendship"] + friend, opponent.id)
                    await self.bot.db.execute("UPDATE cuppy SET team_loses = $1 WHERE user_id = $2", data1[0]["team_loses"] + 1, ctx.author.id)
                    data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", opponent.id)

                    if data[0]["team_xp"] >= data[0]["team_needed_xp"]:
                        c_nxp = Team.calc_needed_xp(data[0]["team_xp"])
                        await ctx.send(f"<:alert_pink:867758260707000380> {opponent.mention} {e_team_opponent} **{n_team_opponent}** won the battle against {e_team_author} **{n_team_author}** and gained <:xp:867817838941437974> **{xp_amount}**!\n"
                                        f"<:alert_pink:867758260707000380> Oh! {e_team_opponent} **{n_team_opponent}** leveled up to <:level:868426330293821450> **{data[0]['team_level'] + 1}**!")
                        await self.bot.db.execute("UPDATE cuppy SET team_needed_xp = $1, team_level = $2, team_xp = $3 WHERE user_id = $4", c_nxp, data[0]["team_level"] + 1, 0, opponent.id)

                        break

                    await ctx.send(f"<:alert_pink:867758260707000380> {opponent.mention} {e_team_opponent} **{n_team_opponent}** won the battle against {e_team_author} **{n_team_author}** and gained <:xp:867817838941437974> **{xp_amount}**!")
                    break

                await asyncio.sleep(5)
                continue

    @commands.command()
    @is_team()
    async def test(self, ctx, teammate: str, level: int):
        ivs = Team.ivs_level_based(teammate.lower(), level)
        return await ctx.send(ivs)

    @commands.command(aliases=["mh", "mhunt"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def monsterhunt(self, ctx):
        data = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
        if not data:
            return await ctx.invoke(self.test_balance)

        team = data[0]["team_name"]
        if not team:
            return await ctx.send(f"<:alert_pink:867758260707000380> {ctx.author.mention} you need a teammate to go hunting monsters, check out `ami team shop`!")
        
        team_level = data[0]["team_level"]
        team_name = Team.name(team)
        team_emoji = Team.emoji(team)
        ivs = Team.ivs_level_based(team, team_level)
        moves = Team.get_moves(team)

        atk = ivs["atk"]

        basic_moves = moves["base"]
        special_moves = moves["special"]
        ultra_moves = moves["ultra"]

        monster = random.choice(Monster.all_monsters())

        mon_hp = Monster.get_hp(monster)
        mon_name = Monster.name(monster)
        mon_emoji = Monster.emoji(monster)
        mon_cup = Monster.cup_drop(monster)
        mon_xp = Monster.xp_drop(monster)
        mon_im = Monster.get_image(monster)

        c_c = random.randint(1, 90)
        j_c = random.randint(1, 90)

        mex = await ctx.send(f"{ctx.author.mention} type any of ⚔ `attack`, ⛓ `jail` or 🏃‍♂️ `escape`!",
                    embed = discord.Embed(
                        title = "Monster Spotted!",
                        description = f"{team_emoji} **{team_name}** spotted a wild {mon_emoji} **{mon_name}**!",
                        color = self.bot.color)
                        .set_image(url=mon_im)
                        .set_footer(text=f"|═════ Hunt Info ═════|\n♥ Health: {humanize.intcomma(mon_hp)}\nΩ Crit. Chance: {c_c}%\n⌗ Jail Chance: {j_c}%\n\n|═════ Rates ═════|\n"
                                    f"• Jailing it is {mon_cup} cupcakes valued!\n"
                                    f"• Attacking and defeating it is {humanize.intcomma(mon_xp*10)} XP valued!\n"
                                    f"• Escaping will make you lose 5 cupcakes!")
                    )

        try:
            msg = await self.bot.wait_for("message", check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.content.lower() in ["attack", "atk", "jail", "escape", "run"], timeout = 15)
        except asyncio.TimeoutError:
            await mex.edit(content=f"{ctx.author.name} took too long to choose..",

                            embed = discord.Embed(
                        title = "Monster Escaped..",
                        description = f"{mon_emoji} **{mon_name}** runned away..",
                        color = self.bot.color)
                        .set_image(url=mon_im)
                    )
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
            elif chance in range (20, 75):
                move = random.choice(special_moves)
            else:
                move = ultra_moves

            move_name = Team.get_move_name(move)
            move_emoji = Team.move_emoji(move)
            move_damage = Team.get_move_base_damage(move)

            damage = (move_damage + (int(atk/5)))*2
            c_m = "!"
            if critical:
                c_m = " (**`CRITICAL`**)"
                damage = (move_damage + (int(atk/5)) + random.randint(40, 100))*2

            if damage < mon_hp:
                await mex.edit(content=f"{team_emoji} **{team_name}** landed a {move_emoji} **{move_name}**: that dealt 💥 {humanize.intcomma(damage)}{c_m}\n"
                                    f"{mon_emoji} **{mon_name}** remained with ❤ {humanize.intcomma(mon_hp-damage)} / {humanize.intcomma(mon_hp)} and ran away.",
                        
                        embed = discord.Embed(
                        title = "Monster Escaped..",
                        description = f"{team_emoji} **{team_name}** failed defeating {mon_emoji} **{mon_name}**..",
                        color = self.bot.color)
                        .set_image(url=mon_im)
                    )

                return

            elif damage > mon_hp:
                m = f"|═════ Reward ═════|\n[★] {team_name} earned {humanize.intcomma(mon_xp*10)} XP!"
                await self.bot.db.execute("UPDATE cuppy SET team_xp = $1 WHERE user_id = $2", data[0]["team_xp"] + mon_xp*10, ctx.author.id)
                data2 = await self.bot.db.fetch("SELECT * FROM cuppy WHERE user_id = $1", ctx.author.id)
                if data2[0]["team_xp"] >= data2[0]["team_needed_xp"]:
                        c_nxp = Team.calc_needed_xp(data2[0]["team_xp"])
                        await self.bot.db.execute("UPDATE cuppy SET team_needed_xp = $1, team_level = $2, team_xp = $3 WHERE user_id = $4", c_nxp, data2[0]["team_level"] + 1, 0, ctx.author.id)
                        m = f"|═════ Reward ═════|\n[★] {team_name} earned {humanize.intcomma(mon_xp*10)} XP!\n[★] Oh! {team_name} leveled up to level {data2[0]['team_level'] + 1}!"

                await mex.edit(content=f"{team_emoji} **{team_name}** landed a {move_emoji} **{move_name}**: that dealt 💥 {humanize.intcomma(damage)}{c_m}\n"
                                    f"{mon_emoji} **{mon_name}** fell for the damage, the hunt was a success!",

                                embed = discord.Embed(
                        title = f"Congratulations, {ctx.author.name}!",
                        description = f"{team_emoji} **{team_name}** defeated {mon_emoji} **{mon_name}**!",
                        color = self.bot.color)
                        .set_image(url=mon_im)
                        .set_footer(text=f"{m}")
                    )

                return

        if msg.content.lower() == "jail":
            jchance = random.randint(1, 100)
            if jchance in range(1, j_c):

                jchancec = random.randint(1, 100)

                jmove = None

                if jchancec in range(1, 20):
                    jmove = random.choice(basic_moves)
                elif jchancec in range (20, 75):
                    jmove = random.choice(special_moves)
                else:
                    jmove = ultra_moves

                jmove_name = Team.get_move_name(jmove)
                jmove_emoji = Team.move_emoji(jmove)

                await self.bot.db.execute("UPDATE cuppy SET balance = $1, lifetime_earns = $2 WHERE user_id = $3", data[0]["balance"] + mon_cup, data[0]["lifetime_earns"] + mon_cup, ctx.author.id)
                await mex.edit(content=f"{team_emoji} **{team_name}** landed a {jmove_emoji} **{jmove_name}** and succesfully jailed {mon_emoji} **{mon_name}**!",

                                embed = discord.Embed(
                                    title = f"Congratulations, {ctx.author.name}!",
                                    description = f"{team_emoji} **{team_name}** jailed {mon_emoji} **{mon_name}**!",
                                    color = self.bot.color)
                                    .set_image(url=mon_im)
                                    .set_footer(text=f"|═════ Reward ═════|\n[★] You've earned {mon_cup} cupcakes!\n")
                                )

                return
            else:
                jchancec = random.randint(1, 100)

                jmove = None

                if jchancec in range(1, 20):
                    jmove = random.choice(basic_moves)
                elif jchancec in range (20, 75):
                    jmove = random.choice(special_moves)
                else:
                    jmove = ultra_moves

                jmove_name = Team.get_move_name(jmove)
                jmove_emoji = Team.move_emoji(jmove)

                await mex.edit(content=f"{team_emoji} **{team_name}** landed a {jmove_emoji} **{jmove_name}** but failed jailing {mon_emoji} **{mon_name}**..",

                                embed = discord.Embed(
                                    title = "Monster Escaped..",
                                    description = f"{team_emoji} **{team_name}** failed jailing {mon_emoji} **{mon_name}**..",
                                    color = self.bot.color)
                                    .set_image(url=mon_im)
                                )

                return

        if msg.content.lower() in ["escape", "run"]:
            if data[0]["balance"] >= 5:
                await self.bot.db.execute("UPDATE cuppy SET balance = $1 WHERE user_id = $2", data[0]["balance"] - 5, ctx.author.id)

            await mex.edit(content=f"{ctx.author.mention} ran away with {team_emoji} **{team_name}**..",

                            embed = discord.Embed(
                        title = "You escaped..",
                        description = f"{mon_emoji} **{mon_name}** ran in the opposite direction..",
                        color = self.bot.color)
                        .set_image(url=mon_im)
                    )

            return
    

    @commands.command()
    @is_team()
    async def devgift(self, ctx, member: discord.Member, amount: int):
        await self.bot.db.execute("UPDATE cuppy SET balance = $1 WHERE user_id = $2", amount, member.id)
        await ctx.message.add_reaction("✅")

def setup(bot):
    bot.add_cog(Cuppy(bot))

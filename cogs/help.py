import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Help Loaded")


    @commands.command(help="Show this message.")
    async def help(self, ctx, *, command=None):
        if command:
            if command.lower() == "moderation":
                embed=discord.Embed(title="<:moderation:846314041991102474> Moderation commands", description=f"Moderation, i think you know what type of commands they are. Manage your server with easy commands, ban people when they break the rules, mute fast people who are spamming, and other stuff you can just read after!\n\n• `ban`, `kick`, `mute`, `muterole`, `unban`, `unmute`, `clear`, `roleinfo`, `slowmode`, `automod`, `addbadwords`, `rembadwords`, `deletechannel`, `createchannel`, `removerole`, `giverole`", color=0xffcff1)
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                return await ctx.send(embed=embed)
            elif command.lower() == "cuppy":
                embed=discord.Embed(title="<:cupcake:845632403405012992> Cuppy commands", description=f"Cuppy is a RPG-Idea economy in a discord bot, with monsters to hunt, defeat and jail, battles between members with teammates, teammates prestigable, mining with many pickaxe's to obtain and upgrade, clans to raise up and reach highers leagues and much more!\n\n**Minerals**\n> `minerals`, `minerals inventory`, `minerals values`\n**Info & Utils**\n> `profile`, `give`, `balance`, `exchange`, `open`, `boxinventory`, `leaderboard`, `daily`, `weekly`, `monthly`, `checklist`\n**Pickaxe**\n> `pickaxe`, `pickaxe upgrade`, `pickaxe stats`, `pickaxe list`, `pickaxe recharge`, `mine`\n**Battles & Teammates**\n> `team`, `team recruit`, `team prestige`, `team stats`, `team shop`, `battle`, `xproom`, `xproom run`, `xproom claim`, `xproom upgrade`\n**Hunting**\n> `monsterlist`, `monsterhunt`\n**Clans**\n> `clan`, `clan create`, `clan rename`, `clan description`, `clan leave`, `clan delete`, `clan kick`, `clan invite`, `clan info`, `clan donate`", color=0xffcff1)
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                return await ctx.send(embed=embed)
            elif command.lower() == "music":
                embed=discord.Embed(title="<:music:846314041743114272> Music commands", description=f"Make your members enjoy in one of the best music, online 24/7h, with support of live stream videos from youtube! Add equalizers to your favorite song, move the seek to skip segments, loop the song to can listen it forever!\n\n• `play`, `join`, `leave`, `volume`, `stop`, `24/7`, `lyrics`, `pause`, `resume`, `remove`, `seek`, `shuffle`, `loop`, `queue`, `skip`, `np`, `equalizer`, `filter`, `swap`", color=0xffcff1)
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                return await ctx.send(embed=embed)
            elif command.lower() == "image":
                embed=discord.Embed(title="<:image:846316572812509184> Image commands", description=f"Apply filters to member avatars, round avatars, create images with your texts, get the colors in HEXA from a member avatar, and other funny commands: have fun with our image manipulation!\n\n• `achievement`, `supreme`, `pixel`, `polaroid`, `ascii`, `angel`, `paint`, `colors`, `triangle`, `satan`, `wasted`, `jail`, `charchoal`, `rainbow`, `wide`, `round`, `stonks`, `amongus`, `waifu`, `neko`, `shinobu`, `megumin`", color = 0xffcff1)
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                return await ctx.send(embed=embed)
            elif command.lower() == "fun":
                embed=discord.Embed(title="<:misc:846314042071056384> Fun commands", description=f"Fun commands. Have fun with some cool commands such like a gaymeter, a pp size generator, ship, fake nitro gift and ton of others.\n\n• `nitro`, `ship`, `gaymeter`, `reactspeed`, `penis-size`, `textttospeech`, `roast`, `count`, `lick`, `kiss`, `kill`, `slap`, `hug`, `punch`, `pat`, `poke`", color=0xffcff1)
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                return await ctx.send(embed=embed)
            elif command.lower() == "utility":
                embed=discord.Embed(title="<:AGC_k3llyLUL:771033767434518539> Utility commands", description=f"Utility commands. Retrive info about users, search something on google directly here, and yes, ton of other commands.\n\n• `choose`, `fact`, `password`, `binary`, `reverse`, `mock`, `twitch`, `time`, `translate`, `membercount`, `urban`, `info`, `invite`, `calculate`, `vote`, `userinfo`, `serverinfo`, `memberlist`, `google`, `html`, `avatar`, `searchanime`, `check`, `afk`, `remind`, `rtfm`", color=0xffcff1)
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                return await ctx.send(embed=embed)
            elif command.lower() == "leveling":
                embed=discord.Embed(title="<:8853_Uno_Nanbaka_Hum:852002554691059724> Leveling commands", description=f"Leveling, engage your server members with an easy leveling system, make them chat to can level-up faster, edit the message for level-up & the channel where send it!\n\n`level`, `setleveling set`, `setleveling settings`, `setleveling message`, `setleveling channel`, `setleveling levelup-image`", color = 0xffcff1)
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                return await ctx.send(embed=embed)
            elif command.lower() == "boosting":
                embed=discord.Embed(title="<:2158takolaugh:852220010830889021> Boosting commands", description=f"Boosting, track every new boost that comes in your guild, set a channel and a message to send when someone boost the server, also enable or disable the embed, customize the embed title, footer, image and have fun!\n\n`setboost modality`, `setboost embed`, `setboost message`, `setboost channel`, `setboost embed-title`, `setboost embed-footer`, `setboost settings`, `setboost preview`, `setboost embed-image`", color = 0xffcff1)
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                return await ctx.send(embed=embed)
            elif command.lower() == "welcome":
                embed=discord.Embed(title="<:welcome:846316342226845746> Welcome commands (click here for youtube tutorial)", url="https://youtu.be/dKFYxT3Yn3g", description="Setup a total customizable welcome for your discord server, customize the message, enable the embed for the message, choose what role give at new members (up to 20), choose in what channel send the message, and give a cute welcome to new people! Oh right, there's also a cute image when embed is enabled ;)\n\n• `welcome set`, `welcome settings`, `welcome message`, `welcome setroles`, `welcome delroles`, `welcome assignrole`, `welcome channel`, `welcome embed`, `welcome mex-out`, `welcome image`, `welcome wel`\n\n**You can also use some variables in the welcome message!**\n```py\n{name} > will return the member name\n{member} > will return like Name#1234\n{mention} > will return the member mention\n{count} > will return the position where it joined\n{age} > will return the account date creation\n{guild} > will return the guild name\n```", color = 0xffcff1)
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                return await ctx.send(embed=embed)

        if command is None:
            ss = "[Support Server](https://discord.gg/ZcErEwmVYu)"
            ss2 = "[Donate](https://donatebot.io/checkout/800176902765674496)"
            ss3 ="[Vote Here](https://top.gg/bot/801742991185936384)"
            em = discord.Embed(description=f"{ss} | {ss2} | {ss3}\nType `ami help <command>` for more info on a specific command!\nCheck out `ami news` for last updates!", color = 0xffcff1)
            em.add_field(name="<:moderation:846314041991102474> Moderation", value = f"`ami help moderation`")
            em.add_field(name="<:cupcake:845632403405012992> Cuppy", value = f"`ami help cuppy`")
            em.add_field(name="<:music:846314041743114272> Music", value = f"`ami help music`")
            em.add_field(name="<:image:846316572812509184> Image", value = f"`ami help image`")
            em.add_field(name="<:misc:846314042071056384> Fun", value = f"`ami help fun`")
            em.add_field(name="<:AGC_k3llyLUL:771033767434518539> Utility", value = f"`ami help utility`")
            em.add_field(name="<:welcome:846316342226845746> Welcome", value = f"`ami help welcome`")
            em.add_field(name="<:8853_Uno_Nanbaka_Hum:852002554691059724> Leveling", value="`ami help leveling`")
            em.add_field(name="<:2158takolaugh:852220010830889021> Boosting", value="`ami help boosting`")
            em.set_thumbnail(url=self.bot.user.avatar_url)
            em.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=em)


        else:
            if len(command) >= 20:
                return
            command = self.bot.get_command(command)
            if command == None:
                return await ctx.send("<:redTick:596576672149667840> Command not found.")
            hel = command.help
            if not hel:
                hel = "No help provided for this command."
            
            cmd_alias = command.aliases
            if not cmd_alias:
                cmd_alias = ["No aliases"]

            try:
                if not cmd_alias[1]:
                    m = " ".join(cmd_alias)
                else:
                    m = ", ".join(cmd_alias)
            except IndexError:
                m = " ".join(cmd_alias)
                

            SCmd = ""  # make an empty string to add the subcommands on

            if isinstance(command, commands.Group):  # check if it has subcommands
                for subcommmand in command.walk_commands():  # iterate through all of the command's parents/subcommands

                    if subcommmand.parents[0] == command:  # check if the latest parent of the subcommand is the command itself
                        SCmd += "`{0.name}` ".format(subcommmand)  # then add it in the string if it is.
                    else:  # the else statement is optional.
                        continue

            check = True if await command.can_run(ctx) else False
            if check:
                em = discord.Embed(title=f"**ami {command.qualified_name} {command.signature}**", description = f"{hel}\n\nAliases: `{m}`\nSubcommands: {SCmd or '`N/A`'}", color = 0xffcff1)
                em.set_footer(text="[] = Optional | <> = Required | []... = Required (can be multiple)", icon_url=ctx.author.avatar_url)
                await ctx.send(embed=em)


def setup(bot):
	bot.add_cog(Help(bot))

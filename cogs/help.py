import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound
from asyncdagpi import Client, ImageFeatures

dagpi = Client("token")

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
                embed=discord.Embed(title="<:moderation:846314041991102474> Moderation commands", description=f"Moderation, i think you know what type of commands they are. Manage your server with easy commands, ban people when they break the rules, mute fast people who are spamming, and other stuff you can just read after!\n\n• `ban`, `kick`, `mute`, `muterole`, `unban`, `unmute`, `cleanup`, `slowmode`, `automod`, `addbadwords`, `rembadwords`, `deletechannel`, `createchannel`, `removerole`, `giverole`", color=0xffcff1)
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                return await ctx.send(embed=embed)
            elif command.lower() == "cuppy":
                embed=discord.Embed(title="<:cupcake:845632403405012992> Cuppy commands", description=f"Cuppy is a type of economy, well that's an economy, but with some major features, such like mining, games, investments, pet's and a currency based on **cupcakes**! Start farming cupcakes and be the richest one.\n\n• `bal`, `dep`, `wd`, `shop`, `buyitem`, `garage`, `drink`, `hunt`, `smoke`, `fish`, `bankrob`, `openchest`, `openchat`, `rob`, `send`, `daily`, `mine`, `tictactoe`, `invest`, `petshop`, `buypet`, `petname`, `leaderboard`, `glbc`", color=0xffcff1)
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                return await ctx.send(embed=embed)
            elif command.lower() == "music":
                embed=discord.Embed(title="<:music:846314041743114272> Music commands", description=f"Make your members enjoy in one of the best music, online 24/7h, with support of live stream videos from youtube! Add equalizers to your favorite song, move the seek to skip segments, loop the song to can listen it forever!\n\n• `play`, `join`, `leave`, `volume`, `stop`, `24/7`, `lyrics`, `pause`, `resume`, `remove`, `seek`, `shuffle`, `loop`, `queue`, `skip`, `np`, `equalizer`, `filter`, `swap`", color=0xffcff1)
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                return await ctx.send(embed=embed)
            elif command.lower() == "manip":
                embed=discord.Embed(title="<:image:846316572812509184> Manipulation commands", description=f"Apply filters to member avatars, round avatars, create images with your texts, get the colors in HEXA from a member avatar, and other funny commands: have fun with our image manipulation!\n\n• `achievement`, `supreme`, `pixel`, `polaroid`, `ascii`, `angel`, `paint`, `colors`, `triangle`, `satan`, `wasted`, `jail`, `charchoal`, `rainbow`, `wide`, `round`, `stonks`, `amongus`", color = 0xffcff1)
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                return await ctx.send(embed=embed)
            elif command.lower() == "misc":
                embed=discord.Embed(title="<:misc:846314042071056384> Misc commands", description=f"Miscellaneous, commands which have no category, placed here for that. Retrive info about users, search something on google directly here, and yes, ton of other commands.\n\n• `nitro`, `ship`, `gaymeter`, `reactspeed`, `choose`, `fact`, `textttospeech`, `time`, `roast`, `count`, `membercount`, `info`, `invite`, `calculate`, `vote`, `userinfo`, `memberlist`, `google`, `html`, `avatar`, `searchanime`, `check`, `afk`, `remind`, `rtfm`, `waifu`, `neko`, `shinobu`, `megumin`, `lick`, `kiss`, `kill`, `slap`, `hug`, `punch`, `pat`", color=0xffcff1)
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
                embed=discord.Embed(title="<:welcome:846316342226845746> Welcome commands (click here for youtube tutorial)", url="https://youtu.be/dKFYxT3Yn3g", description="Setup a total customizable welcome for your discord server, customize the message, enable the embed for the message, choose what role give at new members (up to 20), choose in what channel send the message, and give a cute welcome to new people! Oh right, there's also a cute image when embed is enabled ;)\n\n• `setwelc`, `welcset`, `setmex`, `setroles`, `delroles`, `setassign`, `setchannel`, `emb`, `wel`\n\n**You can also use some variables in the welcome message!**\n```py\n{name} > will return the member name\n{member} > will return like Name#1234\n{mention} > will return the member mention\n{count} > will return the position where it joined\n{age} > will return the account date creation\n{guild} > will return the guild name\n```", color = 0xffcff1)
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                return await ctx.send(embed=embed)

        if command is None:
            ss = "[Support Server](https://discord.gg/ZcErEwmVYu)"
            ss2 = "[Donate](https://donatebot.io/checkout/800176902765674496)"
            ss3 ="[Vote Here](https://top.gg/bot/801742991185936384)"
            em = discord.Embed(description=f"{ss} | {ss2} | {ss3}\nType `ami help <command>` for more info on a specific command", color = 0xffcff1)
            em.add_field(name="<:moderation:846314041991102474> Moderation", value = f"`ami help moderation`")
            em.add_field(name="<:cupcake:845632403405012992> Cuppy", value = f"`ami help cuppy`")
            em.add_field(name="<:music:846314041743114272> Music", value = f"`ami help music`")
            em.add_field(name="<:image:846316572812509184> Manipulation", value = f"`ami help manip`")
            em.add_field(name="<:misc:846314042071056384> Misc", value = f"`ami help misc`")
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
                        SCmd += "`{0.name}`, ".format(subcommmand)  # then add it in the string if it is.
                    else:  # the else statement is optional.
                        continue

            em = discord.Embed(title=f"`ami {command.name} {command.signature}`", description = f"{hel}\n\nAliases : `{m}`\nSubcommands : {SCmd or '`N/A`'}", color = 0xffcff1)
            em.set_footer(text="[] = Optional | <> = Required | []... = Required (can be multiple)", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=em)


def setup(bot):
	bot.add_cog(Help(bot))

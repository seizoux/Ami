import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandNotFound
from asyncdagpi import Client, ImageFeatures

dagpi = Client("t35iaK4gi36TH3N2q0zd95A1h9m4TeInrLP6oyibSaK97q9SCRggzMUlCMWLkklU")

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Help Loaded")


    @commands.command(help="Show this message.")
    async def help(self, ctx, command=None):
        if command == "moderation":
            embed=discord.Embed(title="Moderation commands", description=f"• `ban`, `kick`, `mute`, `muterole`, `unban`, `unmute`, `cleanup`, `slowmode`, `antispam`", color=0xffcff1)
            embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            return await ctx.send(embed=embed)
        elif command == "economy":
            embed=discord.Embed(title="Economy commands", description=f"• `bal`, `dep`, `wd`, `shop`, `buyitem`, `garage`, `drink`, `hunt`, `smoke`, `fish`, `bankrob`, `openchest`, `oc`, `rob`, `send`, `daily`, `mine`, `invest`, `petshop`, `buypet`, `petname`, `lb`, `glbc`", color=0xffcff1)
            embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            return await ctx.send(embed=embed)
        elif command == "music":
            embed=discord.Embed(title="Music commands", description=f"• `play`, `join`, `leave`, `volume`, `stop`, `pause`, `resume`, `remove`, `seek`, `shuffle`, `loop`, `queue`, `skip`, `np`, `equalizer`, `swap`", color=0xffcff1)
            embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            return await ctx.send(embed=embed)
        elif command == "image":
            embed=discord.Embed(title="Image Manipulation Commands", description=f"• `ach`, `sup`, `px`, `pl`, `asc`, `agl`, `pnt`, `clr`, `trl`, `st`, `wst`, `jl`, `chc`, `rnbw`, `wide`, `round`, `stk`, `amg`", color = 0xffcff1)
            embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            return await ctx.send(embed=embed)
        elif command == "fun":
            embed=discord.Embed(title="Fun commands", description=f"• `lick`, `kiss`, `kill`, `slap`, `hug`, `punch`, `pat`, `nitro`, `ship`, `rspeed`, `ph`, `choose`, `time`, `roast`, `count`", color=0xffcff1)
            embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            return await ctx.send(embed=embed)
        elif command == "utility":
            embed=discord.Embed(title="Utility commands", description=f"• `mc`, `info`, `invite`, `calc`, `vote`, `ui`, `ggl`, `html`, `avatar`, `searchanime`, `check`, `afk`, `remind`", color = 0xffcff1)
            embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            return await ctx.send(embed=embed)
        elif command == "reddit":
            embed=discord.Embed(title="Reddit commands", description=f"• `mizuhara`, `nezuko`, `anime`, `meme`, `sftw`, `prgmh`, `bdb`, `linux`, `cpics`, `fpalm`, `cdesign`, `justwtf`, `pshop`", color = 0xffcff1)
            embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            return await ctx.send(embed=embed)
        elif command == "nsfw":
            if ctx.channel.is_nsfw():
                embed=discord.Embed(title="NSFW commands", description=f"• `neko`, `yuri`, `hentai`, `porn`, `waifu`, `cum`, `amateur`, `thot`, `college`, `porngif`, `phcomm`", color = 0xffcff1)
                embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                return await ctx.send(embed=embed)
            else:
                url = str(ctx.author.avatar_url_as(format="png"))
                img = await dagpi.image_process(ImageFeatures.jail(), url)
                file = discord.File(fp=img.image,filename=f"jail.{img.format}")
                await ctx.send("<:redTick:596576672149667840> **HORNY ALERT!!** <:redTick:596576672149667840>")
                return await ctx.send(file=file)
        elif command == "welcome":
            embed=discord.Embed(title="Welcome commands (click here for youtube tutorial)", url="https://youtu.be/dKFYxT3Yn3g", description="`setwelc`, `welcset`, `setmex`, `setroles`, `delroles`, `setassign`, `setchannel`, `emb`, `wel`\n\n**You can also use some variables in the welcome message!**\n```py\n{name} > will return the member name\n{member} > will return like Name#1234\n{mention} > will return the member mention\n{count} > will return the position where it joined\n{age} > will return the account date creation\n{guild} > will return the guild name\n```", color = 0xffcff1)
            embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            return await ctx.send(embed=embed)

        if command == None:
            ss = "[Support](https://discord.gg/ZcErEwmVYu)"
            ss2 = "[Donate](https://donatebot.io/checkout/800176902765674496)"
            lat = (round(self.bot.latency*1000, 2))
            em = discord.Embed(description=f"```diff\n--- Commands Menu ---\n- Total commands » {len(self.bot.commands)} -\n! Latency » {lat}ms !\n```", color = 0xffcff1)
            em.add_field(name="\u200b", value = f"<:1713_rem_neutral_face:819689871009382481> × **Moderation** <- `Moderation commands.`\n<:6730_1_first:819689872267673600> × **Economy** <- `Economy commands.`\n<a:7337_Furry_Dance_Green:819689872923033631> × **Music** <- `Music commands.`\n<:4626_FoxWave:819689871550971905> × **Image** <- `Images commands.`\n<:7280_PandaGrimReaper:819689872117465118> × **Fun** <- `Fun commands.`\n<:1739_CMD:819689870393999380> × **Utility** <- `Utility commands.`\n<:bigbrain:744344773229543495> × **Reddit** <- `Reddit commands.`\n<:pepoS:596577130893279272>  × **NSFW** <- `NSFW commands.`\n<:Hehe:729328041301508146> × **Welcome** <- `Welcome commands.`\n\n♪ `ami support` / {ss} <- __Support Server__\n♪ `ami donate` / {ss2} <- __Donations__\n♪ `ami feature` <- __To suggest new commands/features__\n")
            em.add_field(name="\u200b", value = "<a:7041_loading:819689872599285770> __Click on reaction to see commands in categories__ <a:7041_loading:819689872599285770>", inline = False)
            em.set_footer(text="Type ami help <command> for more info on a specific command!")
            msg = await ctx.send(embed=em)
            await msg.add_reaction("<:1713_rem_neutral_face:819689871009382481>")
            await msg.add_reaction("<:6730_1_first:819689872267673600>")
            await msg.add_reaction("<a:7337_Furry_Dance_Green:819689872923033631>")
            await msg.add_reaction("<:4626_FoxWave:819689871550971905>")
            await msg.add_reaction("<:7280_PandaGrimReaper:819689872117465118>")
            await msg.add_reaction("<:1739_CMD:819689870393999380>")
            await msg.add_reaction("<:bigbrain:744344773229543495>")
            if ctx.channel.is_nsfw():
                await msg.add_reaction("<:pepoS:596577130893279272>")
            await msg.add_reaction("<:Hehe:729328041301508146>")
            await msg.add_reaction("<a:no:819689870284816415>")

            while True:
                lists = ["1713_rem_neutral_face", "6730_1_first", "7337_Furry_Dance_Green", "4626_FoxWave", "7280_PandaGrimReaper", "1739_CMD", "no", "bigbrain", "pepoS", "Hehe"]
                def check(payload):
                    return payload.message_id == msg.id and payload.emoji.name in lists and payload.user_id == ctx.author.id
                    
                payload = await self.bot.wait_for("raw_reaction_add", check=check)

                if payload.emoji.name == "no":
                    return await msg.delete()

                elif payload.emoji.name == "1713_rem_neutral_face":
                    embed=discord.Embed(title="Moderation commands", description=f"• `ban`, `kick`, `mute`, `muterole`, `unban`, `unmute`, `cleanup`, `slowmode`, `antispam`", color=0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "6730_1_first":
                    embed=discord.Embed(title="Economy commands", description=f"• `bal`, `dep`, `wd`, `shop`, `buyitem`, `garage`, `drink`, `hunt`, `smoke`, `fish`, `bankrob`, `openchest`, `oc`, `rob`, `send`, `daily`, `mine`, `invest`, `petshop`, `buypet`, `petname`, `lb`, `glbc`", color=0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "7337_Furry_Dance_Green":
                    embed=discord.Embed(title="Music commands", description=f"• `play`, `join`, `leave`, `volume`, `stop`, `pause`, `resume`, `remove`, `seek`, `shuffle`, `loop`, `queue`, `skip`, `np`, `equalizer`, `swap`", color=0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "4626_FoxWave":
                    embed=discord.Embed(title="Image Manipulation Commands", description=f"• `ach`, `sup`, `px`, `pl`, `asc`, `agl`, `pnt`, `clr`, `trl`, `st`, `wst`, `jl`, `chc`, `rnbw`, `wide`, `round`, `stk`, `amg`", color = 0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "7280_PandaGrimReaper":
                    embed=discord.Embed(title="Fun commands", description=f"• `lick`, `kiss`, `kill`, `slap`, `hug`, `punch`, `pat`, `nitro`, `ship`, `rspeed`, `ph`, `choose`, `time`, `roast`, `count`", color=0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "1739_CMD":
                    embed=discord.Embed(title="Utility commands", description=f"• `mc`, `info`, `invite`, `calc`, `vote`, `ui`, `ggl`, `html`, `avatar`, `sa`, `check`, `afk`, `remind`", color = 0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "bigbrain":
                    embed=discord.Embed(title="Reddit commands", description=f"• `mizuhara`, `nezuko`, `anime`, `meme`, `sftw`, `prgmh`, `bdb`, `linux`, `cpics`, `fpalm`, `cdesign`, `justwtf`, `pshop`", color = 0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "pepoS":
                    embed=discord.Embed(title="NSFW commands", description=f"• `neko`, `yuri`, `hentai`, `porn`, `waifu`, `cum`, `amateur`, `thot`, `college`, `porngif`, `phcomm`", color = 0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "Hehe":
                    embed=discord.Embed(title="Welcome commands (click here for youtube tutorial)", url="https://youtu.be/dKFYxT3Yn3g", description="`setwelc`, `welcset`, `setmex`, `setroles`, `delroles`, `setassign`, `setchannel`, `emb`, `wel`\n\n**You can also use some variables in the welcome message!**\n```py\n{name} > will return the member name\n{member} > will return like Name#1234\n{mention} > will return the member mention\n{count} > will return the position where it joined\n{age} > will return the account date creation\n{guild} > will return the guild name\n```", color = 0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

        else:
            command = self.bot.get_command(command)
            if command == None:
                return await ctx.send("<:redTick:596576672149667840> Command not found.")
            hel = command.help
            if not hel:
                hel = "No help provided for this command."
            
            cmd_alias = command.aliases
            if not cmd_alias:
                cmd_alias = ["No aliases"]

            m = "".join(cmd_alias)
            em = discord.Embed(title=f"Help for {command.name}", description = f"{hel}", color = 0xffcff1)
            em.add_field(name='Syntax', value=f"> `ami {command.name} {command.signature}`")
            em.add_field(name='Aliases', value=f"> `{m}`")
            em.set_footer(text="[] = Optional | <> = Required | []... = Required (can be multiple)", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=em)


def setup(bot):
	bot.add_cog(Help(bot))

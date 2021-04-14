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
    async def help(self, ctx, command=None):
        if command == None:
            ss = "[Support](https://discord.gg/ZcErEwmVYu)"
            ss2 = "[Donate](https://donatebot.io/checkout/800176902765674496)"
            lat = (round(self.bot.latency*1000, 2))
            em = discord.Embed(description=f"```diff\n--- Commands Menu ---\n- Total commands » {len(self.bot.commands)} -\n! Latency » {lat}ms !\n```", color = 0xffcff1)
            em.add_field(name="\u200b", value = f"<:1713_rem_neutral_face:819689871009382481> × **Moderation** <- `Moderation commands.`\n<:6730_1_first:819689872267673600> × **Economy** <- `Economy commands.`\n<a:7337_Furry_Dance_Green:819689872923033631> × **Music** <- `Music commands.`\n<:4626_FoxWave:819689871550971905> × **Images** <- `Images commands.`\n<:7280_PandaGrimReaper:819689872117465118> × **Fun** <- `Fun commands.`\n<:1739_CMD:819689870393999380> × **Utility** <- `Utility commands.`\n<:bigbrain:744344773229543495> × **Reddit** <- `Reddit commands.`\n<:pepoS:596577130893279272>  × **NSFW** <- `NSFW commands.`\n<:Hehe:729328041301508146> × **Welcome** <- `Welcome commands`\n\n♪ `ami support` / {ss} <- __Support Server__\n♪ `ami donate` / {ss2} <- __Donations__\n♪ `ami feature` <- __To suggest new commands/features__\n")
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
                    embed=discord.Embed(title="Moderation commands", description=f"• `ban`, `kick`, `mute`, `unban`, `unmute`, `clear`", color=0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "6730_1_first":
                    embed=discord.Embed(title="Economy commands", description=f"• `bal`, `dep`, `wd`, `shop`, `buyitem`, `garage`, `drink`, `hunt`, `smoke`, `fish`, `bankrob`, `openchest`, `oc`, `rob`, `send`, `daily`, `mine`, `invest`, `type`, `lvl`, `setlevelbg`, `lvlup`, `petshop`, `buypet`, `petname`, `lb`, `glbc`", color=0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "7337_Furry_Dance_Green":
                    embed=discord.Embed(title="Music commands", description=f"• `play`, `leave`, `stop`, `pause`, `resume`, `summon`, `shuffle`, `queue`, `remove`, `skip`, `now`", color=0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "4626_FoxWave":
                    embed=discord.Embed(title="Image(s) commands", description=f"• `ach`, `sup`, `px`, `pl`, `asc`, `agl`, `pnt`, `clr`, `trl`, `st`, `wst`, `slr`, `jl`, `chc`, `rnbw`", color = 0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "7280_PandaGrimReaper":
                    embed=discord.Embed(title="Fun commands", description=f"• `lick`, `kiss`, `kill`, `slap`, `hug`, `echo`, `nitro`, `ship`, `rspeed`, `ph`, `devquiz`, `choose`, `time`, `emojis`, `roast`, `amg`, `wide`, `stk`", color=0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "1739_CMD":
                    embed=discord.Embed(title="Utility commands", description=f"• `syt`, `mc`, `info`, `emoji`, `covid`, `invite`, `calc`, `vote`, `ui`, `ggl`, `html`, `avatar`, `sa`, `sm`, `check`, `afk`", color = 0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "bigbrain":
                    embed=discord.Embed(title="Subreddits commands", description=f"• `mizuhara`, `nezuko`, `anime`, `meme`, `sftw`, `prgmh`, `bdb`, `linux`, `cpics`, `fpalm`, `cdesign`, `justwtf`, `pshop`", color = 0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "pepoS":
                    embed=discord.Embed(title="NSFW commands", description=f"• `neko`, `yuri`, `hentai`, `porn`, `waifu`, `cum`, `amateur`, `thot`, `college`, `porngif`, `phcomm`", color = 0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "Hehe":
                    embed=discord.Embed(title="Welcome commands", description="• **setwelc** > `Set a custom welcome message!` -> (__ami setwelc__)\n• **welcset** > `See welcome settings` -> (__ami welcset__)\n• **setmex** > `Change welcome message` -> (__ami setmex <message>__)\n• **setrolename** > `Change role assigned` -> (__ami setrolename <rolename>__)\n• **setassign** > `Enable or disable role assignment` -> (__ami setassign <on/off>__)\n• **setchannel** > `Change channel for the welcome message` -> (__ami setchannel <channelID>__)\n• **emb** > `Enable or disable embed` -> (__ami emb <on/off>__)\n• **wel** > `Enable or disable welcome message` -> (__ami wel <on/off>__)\n\n**You can also use some variables in the welcome message!**\n```py\n{name} > will return the member name\n{member} > will return like Name#1234\n{mention} > will return the member mention\n{count} > will return the position where it joined\n{age} > will return the accout date creation\n{guild} > will return the guild name\n```", color = 0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

        else:
            command = self.bot.get_command(command)
            if command == None:
                return await ctx.send("Command not found.")
            hel = command.help
            if not hel:
                hel = "No help for this command."
            
            em = discord.Embed(title=f"Help for {command.name}", description = f"`{hel}`", color = 0xffcff1)
            em.add_field(name='Syntax', value=f"> `ami {command.name} {command.signature}`")
            em.add_field(name='Aliases', value=f"> `{command.aliases}`")
            em.set_footer(text="[] = Optional | <> = Required", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=em)


def setup(bot):
	bot.add_cog(Help(bot))
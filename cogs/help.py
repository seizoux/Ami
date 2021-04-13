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
                    embed=discord.Embed(title="Moderation commands", description=f"• **ban** > `Ban someone` -> (__ami ban @member__)\n• **kick** > `Kick someone` -> (__ami kick @member__)\n• **mute** > `Mute someone` -> (__ami mute @member__)\n• **unban** > `Unban someone` -> (__ami unban name#1234__)\n• **unmute** > `Unmute someone` -> (__ami unmute @member__)\n• **clear** > `Clear tot messages.` -> (__ami clear number__)", color=0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "6730_1_first":
                    embed=discord.Embed(title="Economy commands", description=f"• **bal** > `Open/see your/a balance` -> (__ami bal / ami bal @member__)\n• **dep** > `Deposit coins` -> (__ami dep amount__)\n• **wd** > `Whitdraw coins` -> (__ami wd amount__)\n• **oc** > `Talk with me and earn coins for talked time` -> (__ami oc__)\n• **rob** > `Rob coins to a member (pocket)` -> (__ami rob @member__)\n• **send** > `Send coins to a member` -> (__ami send @member__)\n• **daily** > `Recive the daily coins gift` -> (__ami daily__)\n• **mine** > `Mine coins` -> (__ami mine__)\n• **invest** > `Invest coins to earn more coins` -> (__ami invest amount__)\n• **type** > `Earn coins with your type speed!` -> (__ami type__)\n• **lvl** > `See your level card` -> (__ami lvl__)\n• **setlevelbg** > `Set your level card background` -> (__ami setlevelbg link__)\n• **lvlup** > `Use coins to level up` -> (__ami lvlup__)\n• **petshop** > `Check what pet can you buy` -> (__ami petshop__)\n• **buypet** > `Buy a pet` -> (__ami buypet petname__)\n• **petname** > `Change the name of your pet` -> (__ami petname newpetname__)\n• **lb** > `See the economy leaderboard` -> (__ami lb__)\n• **glbc** > `See how much coins ami has stored` -> (__ami glbc__)", color=0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "7337_Furry_Dance_Green":
                    embed=discord.Embed(title="Music commands", description=f"• **play** > `Play something in VC` -> (__ami play songname / ami play url__)\n• **leave** > `Leave the current VC` -> (__ami leave__)\n• **stop** > `Stop the current song` -> (__ami stop__)\n• **pause** > `Pause the current song` -> (__ami pause__)\n• **resume** > `Resume the paused song` -> (__ami resume__)\n• **summon** > `Summon ami in a VC` -> (__ami summon vcname__)\n• **shuffle** > `Shuffle the queue` -> (__ami shuffle__)\n• **queue** > `See the queue` -> (__ami queue__)\n• **remove** > `Remove a song from the queue` -> (__ami remove songnumber__)\n• **skip** > `Skip the current song and play the next in the queue` -> (__ami skip__)\n• **now** > `See the current song in playing` -> (__ami now__)", color=0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "4626_FoxWave":
                    embed=discord.Embed(title="Image(s) commands", description=f"• **ach** > `Get an achievement` -> (__ami ach text__)\n• **sup** > `Get a supreme text` -> (__ami sup text__)\n• **px** > `Get the pixel effect with a member avatar.` -> (__ami px @member__)\n• **pl** > `Get the polaroid effect with a member avatar.` -> (__ami pl @member__)\n• **asc** > `Get the ascii effect with a member avatar.` -> (__ami asc @member__)\n• **agl** > `Get the angel effect with a member avatar.` -> (__ami agl @member__)\n• **pnt** > `Get the paint effect with a member avatar.` -> (__ami pnt @member__)\n• **clr** > `Get the colors hexa of a member avatar.` -> (__ami clr @member__)\n• **trl** > `Get the triangle effect with a member avatar.` -> (__ami trl @member__)\n• **st** > `Get the satan effect with a member avatar.` -> (__ami st @member__)\n• **wst** > `Get the wasted effect with a member avatar.` -> (__ami wst @member__)\n• **slr** > `Get the solarize effect with a member avatar.` -> (__ami slr @member__)\n• **jl** > `Get the jail effect with a member avatar.` -> (__ami jl @member__)\n• **chc** > `Get the charcoal effect with a member avatar.` -> (__ami chc @member__)\n• **rnbw** > `Get the rainbow effect with a member avatar.` -> (__ami rnbw @member__)", color = 0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "7280_PandaGrimReaper":
                    embed=discord.Embed(title="Fun commands", description=f"• **lick** > `Lick a member` -> (__ami lick @member__)\n• **kiss** > `Kiss a member` -> (__ami kiss @member__)\n• **kill** > `Kill a member` -> (__ami kill @member__)\n• **slap** > `Slap a member` -> (__ami slap @member__)\n• **hug** > `Hug a member` -> (__ami hug @member__)\n• **echo** > `Say something for ami to repeat.` -> (__ami echo text__)\n• **nitro** > `Recive a nitro gift` -> (__ami nitro__)\n• **ship** > `Ship two members` -> (__ami ship @member1 @member2__)\n• **rspeed** > `Reaction game` -> (__ami rspeed time__)\n• **ph** > `Simulate the PH career of a member` -> (__ami ph @member__)\n• **devquiz** > `Play a quiz on development (Need DM's open)` -> (__ami devquiz__)\n• **choose** > `Choose between multiple choices` -> (__ami choose text1 text2__)\n• **time** > `See your actual time or a member time` -> (__ami time / ami time @member__)\n• **emojis** > `Get a list of all Ami emojis` -> (__ami emojis__)\n• **roast** > `Roast someone` -> (__ami roast @member__)\n• **amg** > `Generate an Among Us image` -> (__ami amg @member color true/false__)\n• **wide** > `Get the wide effect with a member avatar.` -> (__ami wide @member__)\n• **stk** > `Generate a Stonks image.` -> (__ami stk @member true/false__)", color=0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "1739_CMD":
                    embed=discord.Embed(title="Utility commands", description=f"• **syt** > `Search something on youtube` -> (__ami syt text__)\n• **mc** > `See the total members of the server` -> (__ami mc__)\n• **info** > `See ami info` -> (__ami info__)\n• **emoji** > `Create an emoji with image links` -> (__ami emoji imagelink__)\n• **covid** > `See covid stats by country name` -> (__ami covid country__)\n• **invite** > `Invite ami to your server` -> (__ami invite__)\n• **calc** > `Evaluate an expression` -> (__ami calc expression__)\n• **vote** > `Ami vote redirect link` -> (__ami vote__)\n• **ui** > `Get user info` -> (__ami ui @member__)\n• **ggl** > `Search something on google` -> (__ami ggl something__)\n• **html** > `Convert a test from discord markdown into HTML` -> (__ami html text__)\n• **avatar** > `Get a member avatar` -> (__ami avatar @member__)\n• **sa** > `Search an anime on MyAnimeList` -> (__ami sa animename__)\n• **sm** > `Search a manga on MyAnimeList` -> (__ami sm manganame__)\n• **check** > `Check if a photo is NSFW or SFW` -> (__ami check @member / ami check photourl__)\n• **afk** > `Set your AFK mode` -> (__ami afk reason__)", color = 0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "bigbrain":
                    embed=discord.Embed(title="Subreddits commands", description=f"• **mizuhara** > `Mizuhara artworks` -> (__ami mizuhara__)\n• **nezuko** > `Nezuko artworks` -> (__ami nezuko__)\n• **anime** > `Get anime pics` -> (__ami anime__)\n• **meme** > `Get meme pics` -> (__ami meme__)\n• **sftw** > `Get software pics` -> (__ami sftw__)\n• **prgmh** > `Get programmers pics` -> (__ami prgmh__)\n• **bdb** > `Get discord bots (bad) pics` -> (__ami bdb__)\n• **linux** > `Get linux pics` -> (__ami linux__)\n• **cpics** > `Get cute pics` -> (__ami cpics__)\n• **fpalm** > `Get chat (facepalm) pics` -> (__ami fpalm__)\n• **cdesign** > `Get crappy design pics` -> (__ami cdesign__)\n• **justwtf** > `Get WTF pics` -> (__ami justwtf__)\n• **pshop** > `Get photoshop pics` -> (__ami pshop__)", color = 0xffcff1)
                    embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                    await msg.edit(embed=embed)

                elif payload.emoji.name == "pepoS":
                    embed=discord.Embed(title="NSFW commands", description=f"• **neko** > `Catgirls from reddit` -> (__ami neko__)\n• **yuri** > `Girls who love girls` -> (__ami yuri__)\n• **hentai** > `Fap` -> (__ami hentai__)\n• **porn** > `Fap2` -> (__ami porn__)\n• **waifu** > `Fap3` -> (__ami waifu__)\n• **cum** > `Ami fap time` -> (__ami cum @member__)\n• **amateur** > `Get amateur pics` -> (__ami amateur__)\n• **thot** > `Get hot gifs from Tenor` -> (__ami thot__)\n• **college** > `Get college pics` -> (__ami college__)\n• **porngif** > `Get porn gifs` -> (__ami porngif__)\n• **phcomm** > `Get funny p*rnhub comments pics` -> (__ami phcomm__)", color = 0xffcff1)
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
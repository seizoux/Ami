import discord
from discord.ext import commands
import humanize

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command("help")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Help Loaded")


    @commands.command(help="Show the help menu about commands and features.", aliases=["commands"])
    async def help(self, ctx, *, command=None):
        if command is None:
            return await ctx.send(f"<a:AGC_Wave:833708920086069300> To see all commands that Ami has, visit https://amibot.gg/commands\n🔎 Else use `ami help <command>` to get more info about commands.")

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
                    SCmd += "{0.name}, ".format(subcommmand)  # then add it in the string if it is.
                else:  # the else statement is optional.
                    continue

        cd_mapping = command._buckets
        cd = cd_mapping._cooldown
        if cd:
            s = f'{cd.rate}x{humanize.precisedelta(cd.per)} ({cd.type.name})'


        em = discord.Embed(title=f"**ami {command.qualified_name} {command.signature}**", description = f"{hel}\n\n**Aliases**: {m}\n**Subcommands**: {SCmd or 'N/A'}\n**Cooldown**: {s if cd_mapping._cooldown else 'N/A'}", color = self.bot.color)
        em.set_footer(text="[] = Optional | <> = Required | []... = Required (can be multiple)", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=em)


def setup(bot):
	bot.add_cog(Help(bot))

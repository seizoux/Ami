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


	@commands.command(name='help')
	async def _help(self, ctx, *, command: str = None):
		"""Shows help about a command or the bot"""
		try:
			if command is None:
				p = await HelpPaginator.from_bot(ctx)
			else:
				entity = bot.get_cog(command) or bot.get_command(command)

				if entity is None:
					clean = command.replace('@', '@\u200b')
					return await ctx.send(f'Command or category "{clean}" not found.')
				elif isinstance(entity, commands.Command):
					p = await HelpPaginator.from_command(ctx, entity)
				else:
					p = await HelpPaginator.from_cog(ctx, entity)

			await p.paginate()
		except Exception as error:
		  print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
		  traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
		  await ctx.send(error)


def setup(bot):
	bot.add_cog(Help(bot))

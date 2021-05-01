from collections import Counter

import discord
from discord.ext import commands

from jishaku.paginators import WrappedPaginator, PaginatorInterface


class commandsusage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.command_counter = 0
        self.bot.commandsusages = Counter()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Cmdusage Loaded")

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        self.bot.command_counter += 1
        self.bot.commandsusages[ctx.command.qualified_name] += 1

    @commands.command(help="See the commands usage")
    @commands.is_owner()
    async def cmdus(self, ctx):
        lists = []
        lists.append(f"Total usages » {self.bot.command_counter}")
        for i, (n, v) in enumerate(self.bot.commandsusages.most_common()):
            lists.append(f"{n:<30} {v:<15}")
        paginator = WrappedPaginator(max_size=1024, prefix="```coffeescript", suffix="```")
        paginator.add_line("\n".join(lists))
        interface = PaginatorEmbedInterface(ctx.bot, paginator, owner=ctx.author)
        return await interface.send_to(ctx)


class PaginatorEmbedInterface(PaginatorInterface):

    def __init__(self, *args, **kwargs):
        self._embed = discord.Embed()
        super().__init__(*args, **kwargs)

    @property
    def send_kwargs(self) -> dict:
        display_page = self.display_page
        self._embed.description = f"{self.pages[display_page]}"
        self._embed.set_footer(text=f'Page {display_page + 1}/{self.page_count}')
        return {'embed': self._embed}

    max_page_size = 2048

    @property
    def page_size(self) -> int:
        return self.paginator.max_size


def setup(bot):
    bot.add_cog(commandsusage(bot))

import discord
from discord.ext import commands
import time
from jishaku.paginators import WrappedPaginator, PaginatorInterface

class Socket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Socket Loaded")

    @commands.Cog.listener()
    async def on_socket_response(self, msg):
        self.bot.socket_receive += 1
        if msg.get("op") != 0:
            self.bot.socket_stats[self.bot.codes[msg.get("op")]] += 1
        else:
            self.bot.socket_stats[msg.get('t')] += 1


    @commands.command(help="Check the socket")
    async def socket(self, ctx):
        current_time = time.time()
        lists = []
        difference = int(current_time - self.bot.start_time)/60
        lists.append(f"Received {self.bot.socket_receive} / {self.bot.socket_receive//difference} sockets per minute")
        for i, (n, v) in enumerate(self.bot.socket_stats.most_common()):
            lists.append(f"{n:<30} {v:<15} {round(v/difference, 3)} /minute")
        paginator = commands.Paginator(max_size=500, prefix="```ml", suffix="```")
        for i in lists:
            paginator.add_line(i)
        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
        return await interface.send_to(ctx)


        
def setup(bot):
    bot.add_cog(Socket(bot))


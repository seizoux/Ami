from discord.ext import commands, tasks


class Chunk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chunk.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Chunk Loaded")

    @tasks.loop(minutes=1)
    async def chunk(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            if not guild.chunked:
                await guild.chunk()


def setup(bot):
    bot.add_cog(Chunk(bot))

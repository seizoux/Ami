import discord
import asyncio
from discord.ext import commands, tasks

class Chunk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chunk.start()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Chunk Loaded")

    @tasks.loop(minutes=30)
    async def chunk(self):
        await self.bot.wait_until_ready()
        try:
            await asyncio.gather(*[guild.chunk() for guild in self.bot.guilds if not guild.chunked])
        except Exception:
            pass

def setup(bot):
    bot.add_cog(Chunk(bot))

from discord.ext import commands, ipc

class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @ipc.server.route()
    async def get_guilds_count(self) -> int:
        return len(self.bot.guilds)
    
    @ipc.server.route()
    async def get_user_count(self) -> int:
        return len(self.bot.users)

def setup(bot):
    bot.add_cog(IpcRoutes(bot))

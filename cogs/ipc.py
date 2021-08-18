import sys

from discord.ext import commands, ipc

class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ipc_ready(self):
        """Called upon the IPC Server being ready"""
        print("Ipc is ready.")

    @commands.Cog.listener()
    async def on_ipc_error(self, endpoint, error):
        """Called upon an error being raised within an IPC route"""
        print(endpoint, "raised", error, file=sys.stderr)
    
    @ipc.server.route()
    async def get_guilds_count(self, data) -> int:
        return len(self.bot.guilds)
    
    @ipc.server.route()
    async def get_user_count(self, data) -> int:
        return len(self.bot.users)

def setup(bot):
    bot.add_cog(IpcRoutes(bot))

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
    async def get_bot_stats(self, data) -> int:
        return {"guilds": len(self.bot.guilds), "users": len(self.bot.users)}

    @ipc.server.route()
    async def bot_top_guilds(self, data) -> list:
        c = []
        s = sorted(self.bot.guilds, key=lambda m: m.member_count, reverse=True)[:5]

        for guild in s:
            if f"{guild.icon_url}".startswith("https://"):
                c.append(f"{guild.icon_url}")
            else:
                c.append("https://img.icons8.com/color/452/discord-logo.png")
        return c

def setup(bot):
    bot.add_cog(IpcRoutes(bot))

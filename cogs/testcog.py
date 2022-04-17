import asyncio
from discord.ext import commands

from util.subclasses import Ami


class IpcTest(commands.Cog):
    def __init__(self, bot: Ami) -> None:
        self.bot = bot
        super().__init__()

    @commands.command()
    @commands.is_owner()
    async def post(self, ctx: commands.Context) -> None:
        await self.bot.websocket.send_json(
            {"cmd": "broadcast", "data": {"payload": {"cmd": "eval", "data": {"payload": 'return 1'}}}}
        )
        self.bot.ws_waiter = asyncio.Future()
        js = await self.bot.ws_waiter
        await ctx.send(js)

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx: commands.Context, cog: str) -> None:
        await self.bot.websocket.send_json(
            {"cmd": "broadcast", "data": {"payload": {"cmd": "unload", "extension": cog}}}
        )
        self.bot.ws_waiter = asyncio.Future()
        js = await self.bot.ws_waiter
        await ctx.send("Cog has been unloaded on all clusters")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx: commands.Context, cog: str) -> None:
        await self.bot.websocket.send_json(
            {"cmd": "broadcast", "data": {"payload": {"cmd": "load", "extension": cog}}}
        )
        self.bot.ws_waiter = asyncio.Future()
        js = await self.bot.ws_waiter
        await ctx.send("Cog has been loaded on all clusters")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, cog: str) -> None:
        await self.bot.websocket.send_json(
            {"cmd": "broadcast", "data": {"payload": {"cmd": "unload", "extension": cog}}}
        )
        self.bot.ws_waiter = asyncio.Future()
        js = await self.bot.ws_waiter
        await self.bot.websocket.send_json(
            {"cmd": "broadcast", "data": {"payload": {"cmd": "load", "extension": cog}}}
        )
        self.bot.ws_waiter = asyncio.Future()
        js = await self.bot.ws_waiter
        await ctx.send("Reloaded!")

    @commands.command()
    @commands.is_owner()
    async def testcogtest(self, ctx):
        await self.bot.websocket.send_json(
            {"cmd": "connected_clusters"}
        )
        self.bot.ws_waiter = asyncio.Future()
        js = await self.bot.ws_waiter
        await ctx.send(f"sent via `test` cmd: {js}")
        await ctx.send(f"okay {self.js.shards}")



def setup(bot: Ami) -> None:
    bot.add_cog(IpcTest(bot))

from discord.ext import commands
import discord
import random
import aiohttp
import logging

log = logging.getLogger("discord")

class Websocket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.bot.loop.create_task(self.connect_ws())

    async def connect_ws(self):
        """
        Connect to the client websocket to send data and open
        the while loop to keep the connection alive as long as
        you don't stop it
        """
        if not hasattr(self.bot, "web_ws"):
            self.bot.web_ws = await self.bot.session.ws_connect('wss://amibot.gg/dashboard/ws/playing')
            log.info("Websocket Connected")

        while True:
            msg = await self.bot.web_ws.receive()

            if msg.tp == aiohttp.MsgType.text:
                if msg.data == 'close':
                    await self.bot.web_ws.close()
                    log.error('Websocket closed by msg.data closed text')
                    break
                else:
                    await self.send_and_retreive(msg)
                    log.info("Invoked send_and_receive for websocket")
            elif msg.tp == aiohttp.MsgType.closed:
                log.erro("Websocket closed")
                break
            elif msg.tp == aiohttp.MsgType.error:
                log.error("Websocket errored.")
                break

    @commands.Cog.listener()
    async def on_ready(self):
        print("Websocket loaded")
        
def setup(bot):
    bot.add_cog(Websocket(bot))
from discord.ext import commands
import discord
import random
import aiohttp
import logging
import asyncio

log = logging.getLogger("discord")

class Websocket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        if hasattr(bot, 'web_ws'):
            if bot.web_ws.closed:
                self.bot.loop.create_task(self.connect_ws())
        else:
            self.bot.loop.create_task(self.connect_ws())

    def cog_unload(self):
        del self.bot.web_ws

    async def handshake_handler_start(self):
        await self.bot.web_ws.send_json({'text': 'ping'})
        await asyncio.sleep(30)

    async def connect_ws(self):
        """
        Connect to the client websocket to send data and open
        the while loop to keep the connection alive as long as
        you don't stop it
        """

        self.bot.web_ws = await self.bot.session.ws_connect('wss://amibot.gg/dashboard/ws/playing')
        log.info("Websocket Connected")

        while self.bot.web_ws.closed != True:
            self.bot.loop.create_task(self.handshake_handler_start())
            log.info("Started receiving...")
            msg = await self.bot.web_ws.receive()

            log.info(f"Received {msg}, going next..")

            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await self.bot.web_ws.close()
                    log.error('Websocket closed by msg.data closed text')
                    break
                else:
                    log.info(f"Websocket received: {msg}")
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                log.error("Websocket closed")
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                log.error("Websocket errored.")
                break

    @commands.Cog.listener()
    async def on_ready(self):
        print("Websocket loaded")
        
def setup(bot):
    bot.add_cog(Websocket(bot))
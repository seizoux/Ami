import discord
from discord.ext import commands, tasks
import datetime
import random
from util.defs import is_team
import asyncio
import typing
import weakref

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._lock = weakref.WeakValueDictionary()
        self._webhook = discord.WebhookAdapter()

        self._cached = {}

    async def get_mod_logs(self, guild: int):
        if guild in self._cached:
            data = self._cached[guild]
        else:
            data = await self.bot.db.fetch("SELECT * FROM modlogs WHERE guild_id = $1", guild)
            self._cached[guild] = data

        if not data:
            return False

        return data

    async def send_log(self, guild: int, content: typing.Union[str, discord.Embed], channel: discord.TextChannel, webhook: str = None):
        lock = self._lock.get(guild)
        if lock is None:
            self._lock[guild] = lock = asyncio.Lock()
        
        async with lock:
            if webhook:
                if type(content) is discord.Embed:
                    return await self._webhook(webhook).send(embed=content)
                return await self._webhook(webhook).send(content)

            ch = self.bot.get_channel(channel)
            if ch:
                if type(content) is discord.Embed:
                    return await ch.send(embed=content)
                return await ch.send(embed=content)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Logging loaded")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild.id != 800176902765674496:
            return

        if message.channel.id != 880917439179792574:
            return

        d = await self.get_mod_logs(message.guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"Message Deleted",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )

        entries = await message.guild.audit_logs(action=discord.AuditLogAction.message_delete).flatten()
        c = entries[0]
        em.add_field(name='Message', value=message.content)
        em.add_field(name="Channel", value=message.channel.mention)
        em.set_author(name=str(c.user), icon_url=c.user.avatar_url)
        em.set_thumbnail(url=c.user.avatar_url)
        await self.send_log(message.guild.id, em, d[0]['channel_id'], d[0]['webhook'] and None)

def setup(bot):
    bot.add_cog(Logging(bot))

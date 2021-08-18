import os
import discord
from discord import client
from discord.ext import commands, tasks
import logging
from collections import Counter
import time
import datetime
import random
import asyncio
import humanize

import util.config as config
from util.defs import is_team
from util.subclasses import Ami

client = Ami()

class LoggerHandler(logging.Handler):
    def setBot(self, bot: commands.Bot):
        self._bot = bot 

    def send_via_hook(self, log: str):
        try:
            _ = self._bot
        except AttributeError:
            print("No bot logging set")
            return

        self._bot.loop.create_task(self._bot.send_via_hook("https://discord.com/api/webhooks/868112473511833670/J3RoOiJbwqQUBZvzsL0ePhwyTBGIcgueiyydLJGyKPKPIFnUYAkS_NRlULiFpqmwhlLf", log)) # create task to send data through webhook

    def handle(self, record: logging.LogRecord):
        fmted_string = self.formatter.format(record)
        self.send_via_hook(f"```sh\n{fmted_string}\n```")


logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

handler = LoggerHandler(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s\n%(name)s :: %(levelname)s\n%(message)s'))
logger.addHandler(handler)
handler.setBot(client)

start_time = datetime.datetime.utcnow()

os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
client.load_extension('jishaku')

client.socket_receive = 0
client.socket_stats = Counter()
client.start_time = time.time()

client.codes = {
      1: "HEARTBEAT",
      2: "IDENTIFY",
      3: "PRESENCE",
      4: "VOICE_STATE",
      5: "VOICE_PING",
      6: "RESUME",
      7: "RECONNECT",
      8: "REQUEST_MEMBERS",
      9: "INVALIDATE_SESSION",
      10: "HELLO",
      11: "HEARTBEAT_ACK",
      12: "GUILD_SYNC"
  }

logging.getLogger('asyncio').setLevel(logging.CRITICAL)

async def log_blacklist():
    await client.wait_until_ready()
    db = await client.db.fetch("SELECT * FROM blacklist")
    for i in db:
        client.bl[i["user_id"]] = i["reason"]
        print(f"Blacklisted: {i['user_id']}")
client.loop.create_task(log_blacklist())

@tasks.loop(minutes=30)
async def status():
    watcher = f'{humanize.intcomma(len(client.guilds))} guilds! | a;help'
    await client.change_presence(status=discord.Status.online,activity=discord.Activity(type=discord.ActivityType.watching, name=watcher))


@client.check
def check_commands(ctx):
    return ctx.guild

@client.event
async def on_ready():
    print(f"Name : {client.user.name}\nID : {client.user.id}\nLoading all cogs...")
    await status.start()

@client.group(invoke_without_command=True)
@is_team()
async def blacklist(ctx):
    await ctx.invoke(client.get_command("help"), **{"command":"blacklist"})

@blacklist.command()
async def add(ctx, user : discord.User, *, reason):
    if len(reason) >= 150:
        return await ctx.send("`reason` argument must be less than 150 chars.")

    await client.db.execute("INSERT INTO blacklist (user_id, reason) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET reason = $2", user.id, reason)
    client.bl[user.id] = reason
    return await ctx.send(f"<:4430checkmark:848857812632076314> **`{user.name}#{user.discriminator}`** has been blacklisted for : {reason}")

@blacklist.command()
async def remove(ctx, user: discord.User):
    db = await client.db.fetch("SELECT * FROM blacklist WHERE user_id = $1", user.id)
    if not db:
        return await ctx.send("<:4318crossmark:848857812565229601> This dude is not blacklisted.")

    if user.id not in client.bl:
        return await ctx.send("<:4318crossmark:848857812565229601> This dude is not blacklisted.")

    await client.db.execute("DELETE FROM blacklist WHERE user_id = $1", user.id)
    del client.bl[user.id]
    return await ctx.send(f"<:4430checkmark:848857812632076314> **`{user.name}#{user.discriminator}`** has been unblacklisted poggies.")

@client.check
async def is_blacklisted(ctx):
    if ctx.author.id in client.bl:
        await ctx.send(f"{ctx.author.mention} you are permanently banned from using the bot.")
        return False
    return True

@client.command(help="See the ami uptime from the last reboot", pass_context=True)
async def uptime(ctx: commands.Context):
    now = datetime.datetime.utcnow() # Timestamp of when uptime function is run
    delta = now - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    if days:
        time_format = "for {d}d {h}h {m}m {s}s so far"
    else:
        time_format = "for {h}h {m}m {s}s so far"
    uptime_stamp = time_format.format(d=days, h=hours, m=minutes, s=seconds)
    await ctx.send(uptime_stamp)

# RUN CLIENT -- IF U DELETE THIS, THE BOT DON'T WORK!!
client.run(config.BOT_TOKEN)

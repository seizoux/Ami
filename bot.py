# There is an amateur and simple python source to config a really useful discord bot.
# Contact me con Telegram for any issues ↪ @fyjxre.
# Discord Server : https://discord.gg/8ppmk2MyM4


# Requirements, Command Prefix & Start Console Message
import os
import discord # library
from discord import client  # library
from discord.ext import commands, ipc  # library
import asyncpg
import logging
from collections import Counter
import time
import datetime
import os
import discord


# THIS IS THE TRIGGER PREFIX OF UR COMMANDS, LIKE ".BAN" "/BAN" "!BAN" "?BAN" "$BAN"
intents=discord.Intents.default()
client = commands.AutoShardedBot(command_prefix=["ami ", "Ami ", "a!"], intents=intents)
start_time = datetime.datetime.utcnow()

os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
client.load_extension('jishaku')

for filename in os.listdir('./cogs'):
  if filename.endswith('.py'):
    client.load_extension(f'cogs.{filename[:-3]}')
    
  else:
    print(f'Unable to load {filename[:-3]}')

async def create_db_pool():
    client.pg_con = await asyncpg.create_pool(database="postgres", user="postgres", password="postgres")


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

@client.event
async def on_ready():
    print(f"Name : {client.user.name}\nID : {client.user.id}\nLoading all cogs...")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"amidiscord.xyz"))


# WARNING: HERE PUT THE TOKEN OF UR BOT!!
token="Ami Token Omitted"


@client.command(help="See the ami uptime from the last reboot", pass_context=True)
async def uptime(ctx: commands.Context):
    now = datetime.datetime.utcnow() # Timestamp of when uptime function is run
    delta = now - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    if days:
        time_format = "**{d}** days, **{h}** hours, **{m}** minutes, and **{s}** seconds."
    else:
        time_format = "**{h}** hours, **{m}** minutes, and **{s}** seconds."
    uptime_stamp = time_format.format(d=days, h=hours, m=minutes, s=seconds)
    em = discord.Embed(description="From the last restart, i've been online for:\n{}".format(uptime_stamp), color=0xffcff1)
    await ctx.send(embed=em)


# RUN CLIENT -- IF U DELETE THIS, THE BOT DON'T WORK!!
client.loop.run_until_complete(create_db_pool())
client.run(token)

import os
import discord
from discord import client
from discord.ext import commands, tasks, ipc
import logging
import websockets
from collections import Counter
import humanize
import asyncio
import io
import json
import logging
import textwrap
import traceback
from contextlib import redirect_stdout

import util.config as config
from util.defs import is_team
from util.subclasses import Ami

client = Ami()

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('[%(levelname)s] -> %(name)s: %(message)s'))
logger.addHandler(handler)

os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"
client.load_extension('jishaku')

client.socket_receive = 0
client.socket_stats = Counter()

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

@tasks.loop(minutes=5)
async def status():
    watcher = f'{humanize.intcomma(len(client.guilds))} guilds! | a;help'
    await client.change_presence(status=discord.Status.online,activity=discord.Activity(type=discord.ActivityType.watching, name=watcher))

@client.check
def check_commands(ctx):
    return ctx.guild

@client.check
def check_if_ready(ctx):
    return client.is_ready()

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

class ClusterBot(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        self.pipe = kwargs.pop('pipe')
        self.cluster_name = kwargs.pop('cluster_name')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        super().__init__(**kwargs, loop=loop)
        self.websocket = None
        self._last_result = None
        self.ws_task = None
        self.responses = asyncio.Queue()
        self.eval_wait = False
        log = logging.getLogger(f"Cluster#{self.cluster_name}")
        log.setLevel(logging.DEBUG)
        log.handlers = [logging.FileHandler(f'cluster-{self.cluster_name}.log', encoding='utf-8', mode='a')]

        log.info(f'[Cluster#{self.cluster_name}] {kwargs["shard_ids"]}, {kwargs["shard_count"]}')
        self.log = log
        self.loop.create_task(self.ensure_ipc())
        self.run(kwargs['token'])

    async def on_ready(self):
        self.log.info(f'[Cluster#{self.cluster_name}] Ready called.')
        self.pipe.send(1)
        self.pipe.close()
        self.load_extension('jishaku')
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                self.load_extension(f"cogs.{file[:-3]}")

    async def on_shard_ready(self, shard_id):
        self.log.info(f'[Cluster#{self.cluster_name}] Shard {shard_id} ready')

    async def on_command_error(self, ctx, exc):
        if not isinstance(exc, (commands.CommandNotFound, commands.NotOwner)):
            self.log.critical(''.join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
            await ctx.send("check logs")

    async def on_error(self, *args, **kwargs):
        self.log.critical(traceback.format_exc())

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    async def close(self, *args, **kwargs):
        self.log.info("shutting down")
        await self.websocket.close()
        await super().close()

    async def exec(self, code):
        env = {
            'bot': self,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(code)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return f'{e.__class__.__name__}: {e}'

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            f'{value}{traceback.format_exc()}'
        else:
            value = stdout.getvalue()

            if ret is None:
                if value:
                    return str(value)
                else:
                    return 'None'
            else:
                self._last_result = ret
                return f'{value}{ret}'

    async def websocket_loop(self):
        while True:
            try:
                msg = await self.websocket.recv()
            except websockets.ConnectionClosed as exc:
                if exc.code == 1000:
                    return
                raise
            data = json.loads(msg, encoding='utf-8')
            if self.eval_wait and data.get('response'):
                await self.responses.put(data)
            cmd = data.get('command')
            if not cmd:
                continue
            if cmd == 'ping':
                ret = {'response': 'pong'}
                self.log.info("received command [ping]")
            elif cmd == 'eval':
                self.log.info(f"received command [eval] ({data['content']})")
                content = data['content']
                data = await self.exec(content)
                ret = {'response': str(data)}
            else:
                ret = {'response': 'unknown command'}
            ret['author'] = self.cluster_name
            self.log.info(f"responding: {ret}")
            try:
                await self.websocket.send(json.dumps(ret).encode('utf-8'))
            except websockets.ConnectionClosed as exc:
                if exc.code == 1000:
                    return
                raise

    async def ensure_ipc(self):
        self.websocket = w = await websockets.connect('ws://localhost:42069')
        await w.send(self.cluster_name.encode('utf-8'))
        try:
            await w.recv()
            self.ws_task = self.loop.create_task(self.websocket_loop())
            self.log.info("ws connection succeeded")
        except websockets.ConnectionClosed as exc:
            self.log.warning(f"! couldnt connect to ws: {exc.code} {exc.reason}")
            self.websocket = None
            raise

# RUN CLIENT -- IF U DELETE THIS, THE BOT DON'T WORK!!
#client.run(config.BOT_TOKEN)
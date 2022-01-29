import discord
from discord.ext import commands, ipc
import aiohttp, re, sys, ujson, signal, asyncio, asyncpg, os, datetime, humanize
from ratelimiter import RateLimiter
from io import BytesIO
from util.context import AmiCtx
from discord import Webhook, AsyncWebhookAdapter
from aioredis import Redis

def _cancel_tasks(loop):
    tasks = {t for t in asyncio.all_tasks(loop=loop) if not t.done()}

    if not tasks:
        return

    for task in tasks:
        task.cancel()
    try:
        loop.run_until_complete(asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=10))
    except asyncio.TimeoutError:
        pass

    for task in tasks:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler(
                {
                    "message": "Unhandled exception during Client.run shutdown.",
                    "exception": task.exception(),
                    "task": task,
                }
            )

def _cleanup_loop(loop):
    try:
        _cancel_tasks(loop)
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        loop.close()


class Ami(commands.AutoShardedBot):
    def __init__(self):
        self.connector = aiohttp.TCPConnector(limit=200)
        self._logging_ratelimiter = RateLimiter(max_calls=2, period=5)
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(
            command_prefix=["ami ", "Ami ", "a;"],
            max_messages=5000,
            connector=self.connector,
            intents=intents,
            description=r"""a discord bot""",
            chunk_guilds_at_startup=False,
            case_insensitive=False,
            allowed_mentions=discord.AllowedMentions(users=True, roles=True, everyone=False, replied_user=True),
        )

    async def send_via_hook(self, url: str, *args, **kwargs):
        with self._logging_ratelimiter:
            webhook = discord.Webhook.from_url(url, adapter=AsyncWebhookAdapter(self.session))
            await webhook.send(*args, **kwargs)

    async def run_constants(self):
        self.default_prefix = ["ami "]
        self.context = AmiCtx
        self.color = 0xb81217
        self.launch_time = datetime.datetime.utcnow()

        db = await asyncpg.create_pool('postgres://postgres1:postgres@localhost:5432/ami')

        self.db = db
        self.bl = {}

        self.url_regex = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", re.IGNORECASE,)
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": f"python-requests/2.25.1 Ami /1.1.0 Python/{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]} aiohttp/{aiohttp.__version__}"},
            connector=self.connector,
            json_serialize=ujson.dumps,
            timeout=aiohttp.ClientTimeout(total=60),
        )

    def load_all_extensions(self):
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                try:
                    self.load_extension(f"cogs.{file[:-3]}")
                except Exception:
                    pass

    def unload_all_extensions(self):
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                try:
                    self.unload_extension(f"cogs.{file[:-3]}")
                except Exception:
                    pass

    def run(self, *args, **kwargs):
        self.load_all_extensions()
        self.loop.run_until_complete(self.run_constants()) 
    
        loop = self.loop

        try:
            loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
            loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())
        except NotImplementedError:
            pass

        async def runner():
            try:
                await self.start(*args, **kwargs)
            finally:
                if not self.is_closed():
                    await self.close()

        def stop_loop_on_completion(f):
            loop.stop()

        future = asyncio.ensure_future(runner(), loop=loop)
        future.add_done_callback(stop_loop_on_completion)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            future.remove_done_callback(stop_loop_on_completion)
            _cleanup_loop(loop)

        if not future.cancelled():
            try:
                return future.result()
            except KeyboardInterrupt:
                return None

    async def close(self):
        self.unload_all_extensions()
        await self.loop.shutdown_default_executor()
        await self.session.close()
        await super().close()

    def get_message(self, message_id):
        return self._connection._get_message(message_id)

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=self.context)

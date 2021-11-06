import discord
from discord.ext import commands
import datetime
from io import BytesIO
import random
from cogs.cuppy import Lootbox


class AmiCtx(commands.Context):

    async def send(self, content=None, **kwargs):
        ph = random.choice(
            [
                "⭐ Join  the support server now to get notified on new features / bug fixes, `ami support`!",
                f"⭐ If you have not voted yet, `ami vote` and vote now: if you're lucky, you can get a {Lootbox.emoji('common')},{Lootbox.emoji('uncommon')},{Lootbox.emoji('rare')} or {Lootbox.emoji('epic')}!",
                "⭐ Wanna support the project? You can donate to support me and keep me alive as longer as possible, `ami donate` (If you are in the support server, you may receive a special role!)"
            ]
        )
        if random.randint(1, 100) == 1:
            content = f"{ph}\n\n{str(content) if content else ''}"
            return await super().send(content, **kwargs)

        return await super().send(content, **kwargs)

    async def db(self, attr:str, query, *sets):
        attrs_valid = {
            "fetch" : self.bot.db.fetch,
            "execute" : self.bot.db.execute,
            "fetchrow" : self.bot.db.fetchrow,
            "fetchval" : self.bot.db.fetchval,
            "acquire" : self.bot.db.acquire,
            "close" : self.bot.db.close,
            "executemany" : self.bot.db.executemany,
            "expire_connections" : self.bot.db.expire_connections,
            "release" : self.bot.db.release,
            "set_connect_args" : self.bot.db.set_connect_args,
            "terminate" : self.bot.db.terminate
        }

        if attr not in attrs_valid:
            raise TypeError("Attribute passed is not a valid database query.")

        final_result = await attrs_valid[attr](query, ', '.join(sets))
        return await self.send(final_result)

    async def delsend(self, delete_time:int, *args, **kwargs):
        """
        Same as `delete_after` keyword for `ctx.send`, just
        using discord.utils.sleep_until to wait until delete
        Time must be int, not float, use `content="your message"`
        to set the message to send.
        """
        msg = await self.send(" ".join(args))
        real_del_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=delete_time)
        await discord.utils.sleep_until(real_del_time)
        await msg.delete()

    async def safe_send(self, content, *, escape_mentions=True, **kwargs):
        """
        Safe ctx.send, if the message is too long, we want to
        send a .txt file named `message_too_long`, instead get
        the raised error for the long content message.
        """
        if escape_mentions:
            content = discord.utils.escape_mentions(content)

        if len(content) > 2000:
            fp = BytesIO(content.encode())
            kwargs.pop('file', None)
            return await self.send(file=discord.File(fp, filename='message_too_long_dude.txt'), **kwargs)
        else:
            return await self.send(content)

    def tick(self, option:bool, *args, **kwargs):
        """
        Tick property which makes us able to
        get base ticks with our context 
        e.g:
        [await ctx.tick(True)] -> ticks[True] -> <:4430checkmark:848857812632076314>
        [await ctx.tick(False)] -> ticks[False] -> <:4318crossmark:848857812565229601>

        We can also attach a message to make this function return our tick + the message.
        """

        ticks = {
            True : "<:4430checkmark:848857812632076314>",
            False : "<:4318crossmark:848857812565229601>"
        }

        if not args:
            return ticks[option]
        else:
            return f"{ticks[option]} {' '.join(args)}"

def setup(bot):
    bot.context = AmiCtx

def teardown(bot):
    bot.context = commands.Context
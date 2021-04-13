import discord
from discord.ext import commands
import asyncio
import datetime
import time
import humanize
import random

class Devquizz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Devquizz Loaded")



    @commands.command(help="A quiz based on development things")
    @commands.cooldown(1, 1800, commands.BucketType.user)
    async def devquiz(self, ctx):
        user = self.bot.get_user(ctx.author.id)
        em = discord.Embed(title="<:1739_CMD:819689870393999380> Dev. Quiz Requested!", description="This quiz is intended for **developers**: if you have **never** entered this world, I **strongly** recommend to don't trying to take this quiz, it could be frustrating.", color = 0xffcff1)
        em.add_field(name="<:qmark:819702268479012974> How it works?", value = "I will propose one question at a time, waiting for **your answer**: if you answer **correctly**, I will modify the message with the **next question**. If you answer **incorrectly**, I will **stop the quiz**.")
        em.add_field(name="<:qmark:819702268479012974> How many questions?", value = "There are **30** questions, all **different**, some **more complicated** than others.", inline = False)
        em.add_field(name="\u2800", value ="<a:earth:819707227790376991> **To start the quiz, click on the reaction!** <a:earth:819707227790376991>", inline = False)
        em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
        em.set_footer(text="Maybe can be hard, stay chill.")
        em.set_thumbnail(url="https://openetech.com/files/website-development.png")
        em.timestamp = datetime.datetime.utcnow()
        message = await user.send(embed=em)
        await message.add_reaction("<:4626_FoxWave:819689871550971905>")

        def check(payload):
            return payload.message_id == message.id and payload.emoji.name == "4626_FoxWave" and payload.user_id == ctx.author.id

        payload = await self.bot.wait_for("raw_reaction_add", check=check)
        start = time.time()
        embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Question N.1 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, how can you **print** something on your console? **Send the answer.**", color=0xffcff1)
        await message.edit(embed=embed)

        msg = await self.bot.wait_for('message', check=lambda message: message.author  == ctx.author)

        if msg.content in ("print()", "print", 'print("hello")'):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.2 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, what is the **most simple** developing language? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg1 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg1.content in ("python", "Python"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.3 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, if you'd like to make your own **Exception**, what would you do? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg2 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg2.content in ("subclass exception", "class exception(exception):", "class", "subclass", "subclass it"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.4 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, how can you eval something? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg3 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg3.content in ("eval()", "eval"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.5 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, how can you **define** a function? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg4 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg4.content in ("def", "def e()"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.6 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, how can you **import** something? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg5 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg5.content in ("import", "import module"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.7 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, in **software development process**, what is the meaning of **debugging**? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg6 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg6.content in ("removal of error.", "fetch errors", "errors", "error", "find errors", "find error", "find", "to find errors in your code", "finding errors"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.8 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, what is the difference between **list** and **tuples** in Python? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg7 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg7.content in ("lists are mutable", "tuples are immutable"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.9 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, what type of language is python? **programming** or **scripting**? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg8 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg8.content in ("scripting"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.10 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, what is the difference between **yield** and **return**? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg9 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg9.content in ("return can return only a single value", "yalds return a series of value", "return", "single value", "yalds", "multiple value", "results"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.11 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, is python **case sensitive**? **Yes** or **No**? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg10 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg10.content in ("yes", "sure"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.12 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, what are python **iterators**? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg11 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg11.content in ("iterators are objects which can be traversed though or iterated upon.", "iterators", "object", "traversed"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.13 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, wich module do you need to import to generate **random** numbers in Python? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg12 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg12.content in ("random", "import random", "import", "random.random"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.14 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, how do you write **comments** in python? with which **character**? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg13 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg13.content in ("#", "with #", "with"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.15 <:4228_discord_bot_dev:819689871307440200>", description=f"```py\ndef 8ball():\n```\n{ctx.author.name}, in this code, what is wrong with the **def** function? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg14 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg14.content in ("def", "number", "numbers", "def function cannot have numbers"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.16 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, what are the **generators** in python? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg15 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg15.content in ("functions that return an iterable set of items are called generators", "items", "iterable", " functions"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.17 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, how will you convert a string to **all lowercase**? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg16 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg16.content in ("to convert a string to lowercase, lower() function can be used.", "lower", "lower()", "function"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.18 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, what does **len()** do? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg17 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg17.content in ("it is used to determine the length of a string, a list, an array, etc", "lenght", "string", "calculate"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.19 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, what are python **packages**? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg18 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg18.content in ("python packages are namespaces containing multiple modules", "namespaces", "modules", "multiple"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.20 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, how to add **values** to a python array? with wich functions? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg19 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg19.content in ("append()", "insert ()", "extend()", "append", "extend", "insert"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.21 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, how to **remove values** to a python array? with wich functions? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg20 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg20.content in ("pop()", "remove()", "pop", "remove()"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.22 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, does python have **OOps** concepts? **Yes** or **No**? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg21 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg21.content in ("yes", "Yes"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.23 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, what are python **libraries**? collections of `...`? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg22 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg22.content in ("python", "package", "packages"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.24 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, how can you create **classes** in python? with wich **keyword**? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg23 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg23.content in ("class", "class something", "class smh"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.25 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, does python support **multiple** inheritance? **Yes** or **No**? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg24 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg24.content in ("no", "No"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.26 <:4228_discord_bot_dev:819689871307440200>", description=f"```py\ndef pyfunc(r):\n    for `...` in `...`(r):\n     print(' '*(r-`...`-1)+'*'*(2*`...`+1))\npyfunc(9)\n```\n\n{ctx.author.name}, copy this code, place in the empty field (`...`) the correct things to generate a **triangle**! **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg25 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg25.content in ("def pyfunc(r):\n    for x in range(r):\n     print(' '*(r-x-1)+'*'*(2*x+1))\npyfunc(9)", "for x in range", "r-x-1", "2*x+1"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.27 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, what is **PEP 8**? A **coding convention** or a **scripting convention**? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg26 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg26.content in ("coding", "coding convention"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.28 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, what is lambda in python? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg27 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg27.content in ("it is a single expression anonymous function often used as inline function.", "function", "inline function", "anonymous", "expression"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.29 <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, what is docstring in python? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg28 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg28.content in ("functions, modules and classes", "function", "modules", "classes", "function,modules,classes"):
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Correct! Question N.30! <:4228_discord_bot_dev:819689871307440200>", description=f"{ctx.author.name}, did you liked this quiz? **Send the answer.**", color=0xffcff1)
            await message.edit(embed=embed)
        else:
            em = discord.Embed(description="<:allert:819708576796114994> Whoops! Uncorrectly answer, quiz failed: you can retry it in **30 min**!")
            em.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            await user.send(embed=em)
            return

        msg29 = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)

        if msg29:
            channel = self.bot.get_channel(809087142194184202)
            end = time.time()
            total = round(end-start, 2)
            tmq = random.randint(1,6)
            embed=discord.Embed(title="<:4228_discord_bot_dev:819689871307440200> Congrats! You've finished the quiz! <:4228_discord_bot_dev:819689871307440200>", description=f"This quiz is in **beta**, so if you have seen any errors or some bugs, report that to the support server!", color=0xffcff1)
            embed.add_field(name=f"<:stats:819702267850260480> Finished in", value="`{}`".format(humanize.precisedelta(total)))
            embed.add_field(name=f"<:stats:819702267850260480> Approximate time per question", value=f"`{tmq} seconds`")
            embed.set_author(name=f"{ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
            embed.set_footer(text="Your result will be published into #quiz-masters, in the support server!")
            rc = await user.send(embed=embed)

            em = discord.Embed(title=f"<a:KannaOOF:819739316128841728> We have a new quiz master!", color = 0xffcff1)
            em.add_field(name=f"<a:ablobnod:820999192863834152> Master", value=f"`{ctx.author.name}`")
            em.add_field(name=f"<a:ablobnod:820999192863834152> Time", value="`{}`".format(humanize.precisedelta(total)))
            em.set_footer(text="Congratulations!", icon_url=self.bot.user.avatar_url)
            em.timestamp = datetime.datetime.utcnow()
            em.set_thumbnail(url=ctx.author.avatar_url)
            await channel.send(embed=em)





def setup(bot):
    bot.add_cog(Devquizz(bot))
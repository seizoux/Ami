import discord, os
from discord.errors import NotFound
from discord.ext import commands, tasks
from urllib.request import urlretrieve
import time
from jishaku.paginators import WrappedPaginator, PaginatorInterface
import random
from jishaku.codeblocks import codeblock_converter
from util.defs import is_team
import re
from io import BytesIO
import typing
import humanize
from twemoji_parser import emoji_to_url
from nudenet import NudeClassifier
import aiofiles
import datetime
import statcord
import asyncio

MAX_FILE_SIZE = 15000000

Image_Union = typing.Union[
    discord.Member,
    discord.User,
    discord.PartialEmoji,
    discord.Emoji,
    str,
]


class InvalidImage(Exception):
    pass


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "Admin"
        self.key = "statcord.com-DQqjdgAE3RoUYOucBZN3"
        self.api = statcord.Client(self.bot,self.key)
        self.final = None
        self.api.start_loop()
        self.guilds_task.start()

    async def get_url(
        self,
        ctx: commands.Context,
        thing: typing.Optional[str],
        **kwargs: typing.Dict[str, typing.Any],
    ) -> str:
        url = None
        avatar = kwargs.get("avatar", True)
        check = kwargs.get("check", True)
        checktype = kwargs.get("checktype", True)
        gif = kwargs.get("gif", False)

        if ctx.message.reference:
            message = ctx.message.reference.resolved

            if message.embeds and message.embeds[0].type == "image":
                url = message.embeds[0].thumbnail.url

            elif message.embeds and message.embeds[0].type == "rich":
                if message.embeds[0].image.url:
                    url = message.embeds[0].image.url

                elif message.embeds[0].thumbnail.url:
                    url = message.embeds[0].thumbnail.url

            elif (
                message.attachments
                and message.attachments[0].width
                and message.attachments[0].height
            ):
                url = message.attachments[0].url

            if message.stickers:
                sticker = message.stickers[0]

                if sticker.format != discord.StickerType.lottie:
                    url = str(sticker.image.url)
                else:
                    return False

        if (
            ctx.message.attachments
            and ctx.message.attachments[0].width
            and ctx.message.attachments[0].height
        ):
            url = ctx.message.attachments[0].url

        if ctx.message.stickers:
            sticker = ctx.message.stickers[0]

            if sticker.format != discord.StickerType.lottie:
                url = str(sticker.image.url)
            else:
                return False

        if thing is None and avatar and url is None:
            if gif:
                url = str(ctx.author.avatar_url_as(static_format="png", size=512))
            else:
                url = str(ctx.author.avatar_url_as(format="png", size=512))

        elif isinstance(thing, (discord.PartialEmoji, discord.Emoji)):
            if gif:
                url = f"https://cdn.discordapp.com/emojis/{thing.id}.{'gif' if thing.animated else 'png'}"
            else:
                url = f"https://cdn.discordapp.com/emojis/{thing.id}.png"

        elif isinstance(thing, (discord.Member, discord.User)):
            if gif:
                url = str(thing.avatar_url_as(static_format="png", size=512))
            else:
                url = str(thing.avatar_url_as(format="png", size=512))

        elif url is None:
            thing = str(thing).strip("<>")

            if self.bot.url_regex.match(thing):
                url = thing
            else:
                url = await emoji_to_url(thing)
                if url == thing:
                    return False

        if not avatar:
            return False

        if not url:
            return False

        if check:
            async with self.bot.session.get(url) as resp:
                if resp.status != 200:
                    return False

                if not any(f in resp.content_type for f in ["image", "video"]):
                    return False

                if checktype:
                    b = await resp.content.read(50)
                    if b.startswith(
                        b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"
                    ) or b.startswith(
                        b"\x89PNG"
                    ):  # PNG Signature
                        pass

                    elif b[0:3] == b"\xff\xd8\xff" or b[6:10] in (b"JFIF", b"Exif"):
                        pass

                    elif b.startswith(
                        (b"\x47\x49\x46\x38\x37\x61", b"\x47\x49\x46\x38\x39\x61")
                    ):  # GIF Signature
                        pass

                    elif b[:2] in (b"MM", b"II"):
                        pass

                    elif (
                        len(b) >= 3
                        and b[0] == ord(b"P")
                        and b[1] in b"25"
                        and b[2] in b" \t\n\r"
                    ):
                        pass

                    elif b.startswith(b"BM"):
                        pass

                    elif not b.startswith(b"RIFF") or b[8:12] != b"WEBP":
                        return False

                    if (
                        resp.headers.get("Content-Length")
                        and int(resp.headers.get("Content-Length")) > MAX_FILE_SIZE
                    ):
                        return False
        return url

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Admin Loaded")

    @commands.Cog.listener()
    async def on_command(self,ctx):
        self.api.command_run(ctx)

    @tasks.loop(hours=24)
    async def guilds_task(self):
        db = await self.bot.db.fetch("SELECT * FROM guilds ORDER BY date DESC LIMIT 7")
        if not db:
            return await self.bot.db.execute("INSERT INTO guilds (date, guilds, stat, users) VALUES ($1, $2, $3)", datetime.datetime.utcnow(), len(self.bot.guilds), 'N/A', sum([g.member_count for g in self.bot.guilds]))

        if len(db) != 7:
            return await self.bot.db.execute("INSERT INTO guilds (date, guilds, stat, users) VALUES ($1, $2, $3)", datetime.datetime.utcnow(), len(self.bot.guilds), f"+ {len(self.bot.guilds) - db[len(db)-1]}" if (len(self.bot.guilds) - db[len(db)-1]) >= 0 else f"- {len(self.bot.guilds) - db[len(db)-1]}", sum([g.member_count for g in self.bot.guilds]))
        else:
            d = db[6]['date']
            await self.bot.db.execute("DELETE FROM guilds WHERE date = $1", d)
            return await self.bot.db.execute("INSERT INTO guilds (date, guilds, stat, users) VALUES ($1, $2, $3)", datetime.datetime.utcnow(), len(self.bot.guilds), f"+ {len(self.bot.guilds) - db[len(db)-1]}" if (len(self.bot.guilds) - db[len(db)-1]) >= 0 else f"- {len(self.bot.guilds) - db[len(db)-1]}", sum([g.member_count for g in self.bot.guilds]))

    @commands.command()
    @is_team()
    async def update(self, ctx, *, name = 'update'):
        proc = await asyncio.create_subprocess_shell(
            f"git add . && git commit -m '{name}' && git push",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        stdout, stderr = await proc.communicate()

        await ctx.send(embed=discord.Embed(
            description = f"```py\n{stdout.decode()}\n{stderr.decode()}\n\nExited with {proc.returncode}\n```",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        ).set_author(name=f"Spooky skeleton {str(ctx.author)}!", icon_url=ctx.author.avatar_url))

    @commands.command(
        help="Take a screenshot of the page on the given url.", aliases=["ss"]
    )
    @is_team()
    async def screenshot(self, ctx, *, url: str):
        url = url.strip("<>")
        if not re.match(self.bot.url_regex, url):
            return await ctx.send("The url must contain any of http/https.")

        res = await self.bot.session.get(f"https://image.thum.io/get/{url}")
        byt = BytesIO(await res.read())

        em = discord.Embed(description=f"`URL:` {url}\n`Author:` {ctx.author.mention}")
        em.set_image(url=f"attachment://{ctx.command.name}.png")
        await ctx.send(
            embed=em, file=discord.File(byt, filename=f"{ctx.command.name}.png")
        )

    @commands.group(
        help="Developer commands group, runnable only by team.",
        aliases=["dev", "d"],
        invoke_without_command=True,
    )
    @is_team()
    async def developer(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command": "developer"})

    @developer.command()
    async def sendto(
        self, ctx, channel: discord.TextChannel, type: str, image: str, *, content
    ):
        valid_types = ["embed", "message"]
        image_url_check = re.match(
            "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            image,
        )

        if not image_url_check:
            return await ctx.send("The image url provided is not a valid url.")

        if type not in valid_types:
            return await ctx.send(
                f"The type is not valid, choose from `{', '.join(valid_types)}`"
            )

        if len(content) >= 2000:
            return await ctx.send("The content is too long.")

        ch = self.bot.get_channel(channel.id)
        if not ch:
            return

        if type.lower() == "embed":
            em = discord.Embed(description=content, color=self.bot.color)
            em.set_image(url=image)
            await ch.send(embed=em)
            return await ctx.send(f"Sent to {ch.mention}.")

        elif type.lower() == "message":
            await ch.send(f"{content}")
            return await ctx.send(f"Sent to {ch.mention}.")

    @developer.command()
    @is_team()
    async def load(self, ctx, *file):
        try:
            for files in file:
                self.bot.load_extension(f"cogs.{files}")
            return await ctx.send(
                f"<:4430checkmark:848857812632076314> Loaded cogs: **{', '.join(file)}**"
            )
        except Exception as e:
            try:
                for files in file:
                    self.bot.load_extension(f"util.{files}")
                return await ctx.send(
                    f"<:4430checkmark:848857812632076314> Loaded cogs: **{', '.join(file)}**"
                )
            except Exception as e:
                return await ctx.send(
                    f"<:4318crossmark:848857812565229601> Something went wrong while loading **{file}**:\n```py\n{e}\n```"
                )

    @developer.command()
    @is_team()
    async def unload(self, ctx, *file):
        try:
            for files in file:
                self.bot.unload_extension(f"cogs.{files}" or f"util.{files}")
            return await ctx.send(
                f"<:4430checkmark:848857812632076314> Unloaded cogs: **{', '.join(file)}**"
            )
        except Exception as e:
            try:
                for files in file:
                    self.bot.unload_extension(f"util.{files}")
                return await ctx.send(
                    f"<:4430checkmark:848857812632076314> Unloaded util: **{', '.join(file)}**"
                )
            except Exception as e:
                return await ctx.send(
                    f"<:4318crossmark:848857812565229601> Something went wrong while unloading **{file}**:\n```py\n{e}\n```"
                )

    @developer.command(name="reload all", aliases=["ra"])
    @is_team()
    async def reload_all(self, ctx):
        check = []
        errors = {}

        extensions = self.bot.extensions.copy()
        for file in extensions:
            try:
                self.bot.reload_extension(f"{file}")
            except Exception as e:
                errors[f"{file}"] = e
            finally:
                check.append(f"{file}")

        text = "\n".join(
            f"<:4430checkmark:848857812632076314> {module}"
            if module not in errors
            else f"<:4318crossmark:848857812565229601> {module}\n{errors[module]}"
            for module in check
        )
        title = (
            "Reloaded all."
            if len(check) - len(list(errors)) == len(extensions)
            else f"{len(check)-len(list(errors))}/{len(extensions)} cogs reloaded."
        )

        await ctx.send(
            embed=discord.Embed(title=title, description=text, color=self.bot.color)
        )

    @developer.command()
    @is_team()
    async def reload(self, ctx, *file):
        try:
            for files in file:
                self.bot.reload_extension(f"cogs.{files}" or f"util.{files}")
            return await ctx.send(
                f"<:4430checkmark:848857812632076314> Reloaded cogs: **{', '.join(file)}**"
            )
        except Exception as e:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> Something went wrong while reloading **{file}**:\n```py\n{e}\n```"
            )

    @commands.command(aliases=["exe", "run", "eval"])
    @is_team()
    async def evaluate(self, ctx, *, code: codeblock_converter):
        await ctx.invoke(self.bot.get_command("jishaku python"), **{"argument": code})

    @commands.command()
    @is_team()
    async def reboot(self, ctx):
        await ctx.send("<:greenTick:596576670815879169> Rebooting...")
        await self.bot.close()

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.embeds and not before.embeds:
            return

        if before.content != after.content:
            ctx = await self.bot.get_context(after)
            if ctx.valid:
                await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 820733298225315880:
            try:
                if message.content.isdigit():
                    await message.add_reaction("<:AtriYES:819739315579912203>")
                else:
                    pass
            except NotFound:
                pass

    @commands.command()
    @is_team()
    async def changename(self, ctx, *, newname=None):
        if newname == None:
            return await ctx.reply("No name specified")

        await ctx.guild.me.edit(nick=newname)
        await ctx.message.add_reaction("💌")

    @commands.command()
    async def rows(self, ctx):
        s = await self.bot.pg_con.fetch("SELECT COUNT(*) FROM users")
        t = s[0]
        f = sum(t)
        await ctx.send(
            f"<:thumbsup:819703492481908776> I can see **{f}** total rows in `users` database!"
        )

    @commands.command(help="Disable a command (globally)")
    @is_team()
    async def disable(self, ctx, command):
        command = self.bot.get_command(command)
        if not command.enabled:
            return await ctx.send("This command is disabled for now.")
        command.enabled = False
        em = discord.Embed(
            description=f"• `{command.name}` disabled.\n• Use `ami enable <command>` to re-enable it.",
            color=self.bot.color,
        )
        await ctx.send(embed=em)

    @commands.command(help="Enable a command (globally)")
    @is_team()
    async def enable(self, ctx, command):
        command = self.bot.get_command(command)
        if command.enabled:
            return await ctx.send("This command is already enabled.")
        command.enabled = True
        em = discord.Embed(
            description=f"• `{command.name}` enabled.\n• Use `ami disable <command>` to disable it.",
            color=self.bot.color,
        )
        await ctx.send(embed=em)

    @commands.Cog.listener()
    async def on_socket_response(self, msg):
        self.bot.socket_receive += 1
        if msg.get("op") != 0:
            self.bot.socket_stats[self.bot.codes[msg.get("op")]] += 1
        else:
            self.bot.socket_stats[msg.get("t")] += 1

    @commands.command(help="Check the socket")
    async def socket(self, ctx):
        current_time = datetime.datetime.utcnow()
        lists = []
        difference = ((current_time - self.bot.launch_time).seconds) / 60
        lists.append(
            f"Received {self.bot.socket_receive} / {self.bot.socket_receive//difference} sockets per minute"
        )
        for i, (n, v) in enumerate(self.bot.socket_stats.most_common()):
            lists.append(f"{n:<30} {v:<15} {round(v/difference, 3)} /minute")
        paginator = commands.Paginator(max_size=500, prefix="```ml", suffix="```")
        for i in lists:
            paginator.add_line(i)
        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
        return await interface.send_to(ctx)


def setup(bot):
    bot.add_cog(Admin(bot))

import discord, os
from discord.errors import NotFound
from discord.ext import commands
from urllib.request import urlretrieve
import time
from jishaku.paginators import WrappedPaginator, PaginatorInterface
import random
from jishaku.codeblocks import codeblock_converter
from util.defs import is_team
import re
from io import BytesIO
import typing

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "Admin"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Admin Loaded")


    @commands.command()
    @is_team()
    async def upload(self, ctx, *, data: typing.Optional[typing.Union[discord.PartialEmoji, str]]):

        if isinstance(data, discord.PartialEmoji):
            data = data.url

        elif attachments := ctx.message.attachments:
            data = attachments[0].url

        async with self.bot.session.get(str(data)) as resp:
            b = await resp.read()

        auth = {'Authorization': 'imagine'}
        async with self.bot.session.post("https://amidiscord.xyz/api/upload", data={"file": b}, headers=auth) as resp:
            final = await resp.json()
            c = final["url"]
            d = final["delete_url"]
            await ctx.send(embed = discord.Embed(
                description = f"You can find the uploaded file [here!]({c})",
                color = self.bot.color
            .set_footer(f"{ctx.author} check your DMs to delete the file!")
            ).set_author(name="File uploaded!", icon_url = self.bot.user.avatar_url))

            await ctx.author.send(embed=discord.Embed(description=f"To delete your recently uploaded file, go [here]({d})\n\nYour uploaded [file]({c})"))


    @commands.group(help="Update commands group, runnable only by team.", invoke_without_command=True)
    @is_team()
    async def update(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command":"update"})

    @update.command()
    @is_team()
    async def set(self, ctx, *, content):
        if len(content) >= 2000:
            return

        db = await self.bot.db.fetch("SELECT * FROM updates WHERE sussybaka = $1", 144126010642792449)
        if not db:
            await self.bot.db.execute("INSERT INTO updates (sussybaka, update_content) VALUES ($1, $2)", 144126010642792449, content)
            return await ctx.message.add_reaction("<:4430checkmark:848857812632076314>")

        await self.bot.db.execute("UPDATE updates SET update_content = $1 WHERE sussybaka = $2", content, 144126010642792449)
        
        await ctx.message.add_reaction("<:4430checkmark:848857812632076314>")

    @commands.command(help="Check the last updates done and changes.", aliases=["news"])
    async def updates(self, ctx):
        data = await self.bot.db.fetch("SELECT * FROM updates WHERE sussybaka = $1", 144126010642792449)
        await ctx.send(data[0]['update_content'])

    @commands.group(help="Developer commands group, runnable only by team.", aliases=["dev", "d"], invoke_without_command=True)
    @is_team()
    async def developer(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command":"developer"})

    @developer.command()
    async def sendto(self, ctx, channel: discord.TextChannel, type:str, image:str, *, content):
        valid_types = ["embed", "message"]
        image_url_check = re.match("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", image)
        
        if not image_url_check:
            return await ctx.send("The image url provided is not a valid url.")

        if type not in valid_types:
            return await ctx.send(f"The type is not valid, choose from `{', '.join(valid_types)}`")

        if len(content) >= 2000:
            return await ctx.send("The content is too long.")

        ch = self.bot.get_channel(channel.id)
        if not ch:
            return

        if type.lower() == "embed":
            em = discord.Embed(description=content, color = self.bot.color)
            em.set_image(url=image)
            await ch.send(embed=em)
            return await ctx.send(f"Sent to {ch.mention}.")
        
        elif type.lower() == "message":
            await ch.send(f"{content}")
            return await ctx.send(f"Sent to {ch.mention}.")

    @developer.command()
    async def load(self, ctx, file):
        try:
            self.bot.load_extension(f"cogs.{file}")
            return await ctx.send(f"<:4430checkmark:848857812632076314> Loaded **{f'cogs.{file}'}**")
        except Exception as e:
            try:
                self.bot.load_extension(f"util.{file}")
                return await ctx.send(f"<:4430checkmark:848857812632076314> Loaded **{f'util.{file}'}**")
            except Exception as e:
                return await ctx.send(f"<:4318crossmark:848857812565229601> Something went wrong while loading **{file}**:\n```py\n{e}\n```")
    
    @developer.command()
    async def unload(self, ctx, file):
        try:
            self.bot.unload_extension(f"cogs.{file}")
            return await ctx.send(f"<:4430checkmark:848857812632076314> Unloaded **{f'cogs.{file}'}**")
        except Exception as e:
            try:
                self.bot.unload_extension(f"util.{file}")
                return await ctx.send(f"<:4430checkmark:848857812632076314> Unloaded **{f'util.{file}'}**")
            except Exception as e:
                return await ctx.send(f"<:4318crossmark:848857812565229601> Something went wrong while unloading **{file}**:\n```py\n{e}\n```")

    @developer.command(name="reload all", aliases=["ra"])
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

        text = "\n".join(f"<:4430checkmark:848857812632076314> {module}" if module not in errors else f"<:4318crossmark:848857812565229601> {module}\n{errors[module]}" for module in check)
        title = "Reloaded all." if len(check)-len(list(errors)) == len(extensions) else f"{len(check)-len(list(errors))}/{len(extensions)} cogs reloaded."
                    
        await ctx.send(embed=discord.Embed(title=title, description=text, color = 0xffcff1))

    @developer.command()
    async def reload(self, ctx, file):
        try:
            self.bot.reload_extension(f"cogs.{file}" or f"util.{file}")
            return await ctx.send(f"<:4430checkmark:848857812632076314> Reloaded **cogs.{file}**")
        except Exception as e:
            return await ctx.send(f"<:4318crossmark:848857812565229601> Something went wrong while reloading **{file}**:\n```py\n{e}\n```")

    @commands.command(aliases=["exe", "run", "eval"])
    @is_team()
    async def evaluate(self, ctx, *, code : codeblock_converter):
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
        await ctx.send(f"<:thumbsup:819703492481908776> I can see **{f}** total rows in `users` database!")



    @commands.command(help="Disable a command (globally)")
    @is_team()
    async def disable(self, ctx, command):
        command = self.bot.get_command(command)
        if not command.enabled:
                return await ctx.send("This command is disabled for now.")
        command.enabled = False
        em = discord.Embed(description=f"• `{command.name}` disabled.\n• Use `ami enable <command>` to re-enable it.", color = 0xffcff1)
        await ctx.send(embed=em)

    @commands.command(help="Enable a command (globally)")
    @is_team()
    async def enable(self, ctx, command):
        command = self.bot.get_command(command)
        if command.enabled:
            return await ctx.send("This command is already enabled.")
        command.enabled = True
        em = discord.Embed(description=f"• `{command.name}` enabled.\n• Use `ami disable <command>` to disable it.", color = 0xffcff1)
        await ctx.send(embed=em)


    @commands.Cog.listener()
    async def on_socket_response(self, msg):
        self.bot.socket_receive += 1
        if msg.get("op") != 0:
            self.bot.socket_stats[self.bot.codes[msg.get("op")]] += 1
        else:
            self.bot.socket_stats[msg.get('t')] += 1


    @commands.command(help="Check the socket")
    async def socket(self, ctx):
        current_time = time.time()
        lists = []
        difference = int(current_time - self.bot.start_time)/60
        lists.append(f"Received {self.bot.socket_receive} / {self.bot.socket_receive//difference} sockets per minute")
        for i, (n, v) in enumerate(self.bot.socket_stats.most_common()):
            lists.append(f"{n:<30} {v:<15} {round(v/difference, 3)} /minute")
        paginator = commands.Paginator(max_size=500, prefix="```ml", suffix="```")
        for i in lists:
            paginator.add_line(i)
        interface = PaginatorInterface(ctx.bot, paginator, owner=ctx.author)
        return await interface.send_to(ctx)



def setup(bot):
    bot.add_cog(Admin(bot))

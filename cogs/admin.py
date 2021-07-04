import discord, os
from discord.errors import NotFound
from discord.ext import commands
from urllib.request import urlretrieve
import time
from jishaku.paginators import WrappedPaginator, PaginatorInterface
import random
from jishaku.codeblocks import codeblock_converter
from util.defs import is_team

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "Admin"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Admin Loaded")

    @commands.group(help="Developer commands group, runnable only by team.", aliases=["dev", "d"], invoke_without_command=True)
    @is_team()
    async def developer(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command":"developer"})

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
            return await ctx.send(f"<:4430checkmark:848857812632076314> Reloaded **{file}**")
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

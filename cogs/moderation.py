import discord
from discord.ext import commands
import asyncio


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "Moderation"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Moderation Loaded")

    @commands.command()
    @commands.is_owner()
    async def dugongo(self, ctx):
        toleave = self.bot.get_guild(802339719152271361)
        await toleave.leave()
        print("Left Server")


    @commands.command(help="Set the slowmode of the channel where you send this command")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, time):
        valid_times = ["remove", "5s", "10s", "15s", "30s", "1m", "2m", "5m", "10m", "15m", "30m", "1h", "2h", "6h"]
        if time not in valid_times:
            return await ctx.reply(f"This slowmode time can't be set, `ami slowmode remove` to remove the slowmode, else the available slowmodes are:\n`5s`, `10s`, `15s`, `30s`, `1m`, `2m`, `5m`, `10m`, `15m`, `30m`, `1h`, `2h`, `6h`")
        
        slow = 0
        if time in valid_times:
            if time == "remove":
                slow = 0
                await ctx.channel.edit(slowmode_delay=slow)
                await ctx.send(f"<:slowmode:585790802979061760> Channel slowmode **removed!**")
                return
            if time == "5s":
                slow = 5
            elif time == "10s":
                slow = 10
            elif time == "15s":
                slow = 15
            elif time == "30s":
                slow = 30
            elif time == "1m":
                slow = 60
            elif time == "2m":
                slow = 120
            elif time == "5m":
                slow = 300
            elif time == "10m":
                slow = 600
            elif time == "15m":
                slow = 900
            elif time == "30m":
                slow = 1800
            elif time == "1h":
                slow = 3600
            elif time == "2h":
                slow = 7200
            elif time == "6h":
                slow = 21600

        await ctx.channel.edit(slowmode_delay=slow)
        await ctx.send(f"<:slowmode:585790802979061760> Channel slowmode set to **{time}!**")

# Clear Command
    @commands.has_permissions(manage_messages=True)
    @commands.command(description="Clear x messages from the channel sent by the member specified.")
    async def cleanup(self, ctx, amount: int, target: discord.Member=None):
        if amount > 500 or amount < 0:
            return await ctx.send("<:redTick:596576672149667840> Maximum is `500` due to __Discord API Limitations__.")

        def msgcheck(amsg):
            if target:
                return amsg.author.id == target.id
            else:
                return amsg.author.id == self.bot.user.id


        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, check=msgcheck)
        await ctx.send(f'<:greenTick:596576670815879169> Cleared **{len(deleted)}/{amount}** messages.', delete_after=10)
        

# Ban Command
    @commands.command(help="Ban a member from the guild.\nThis supports multiple mentions.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, members: commands.Greedy[discord.Member], *, reason):
        for i in members:
            if isinstance(i, discord.Member):
                if i.top_role >= ctx.author.top_role:
                    await ctx.reply(f"<:redTick:596576672149667840> You can't ban {i.name} (Higher Role).")
            id = i.id
            try:
                await ctx.send(f'<:greenTick:596576670815879169> Successfully banned {i.mention} for `{reason}`.')
                await ctx.guild.ban(discord.Object(id=id), reason=reason)
            except discord.NotFound:
                await ctx.send(f"<:redTick:596576672149667840> Member(s) **{i.name}** not found.")

# Unban Command
    @commands.command(help="Unban a member banned in this guild using their IDs.\nThis supports also multiple members at the same time.\n")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, members: commands.Greedy[discord.User]):
        for i in members:
            try:
              await ctx.guild.unban(discord.Object(id=i.id))
            except discord.NotFound:
              #don't have to stop all other bans
              return await ctx.send(f"<:redTick:596576672149667840> Member(s) **{i.name}** not found / not banned.")
        
        await ctx.send(f'<:greenTick:596576670815879169> Successfully unbanned **{", ".join([i.name for i in members])}**.')

# Kick Command
    @commands.command(help="Kick a member from the guild.\nThis supports also multiple mentions.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *, reason):
        for i in members:
            id = i.id
            try:
                await ctx.send(f'<:greenTick:596576670815879169> Successfully kicked {i.mention} for `{reason}`.')
                await ctx.guild.kick(discord.Object(id=id))
            except discord.NotFound:
                await ctx.send(f"<:redTick:596576672149667840> Member(s) {i.name} not found.")

    @commands.command(help="Set the role i need to use when you invoke `ami mute`.\nThis role will be set to the members you send in `ami mute` as muted role, so be sure to have set the right permissions on this role.")
    @commands.has_permissions(manage_guild=True)
    async def muterole(self, ctx, role: discord.Role):
        role = discord.utils.get(ctx.guild.roles, id=role.id)
        if not role:
            return await ctx.reply(f"<:redTick:596576672149667840> {role} was not found in the guild roles.")

        guild_id = str(ctx.guild.id)
        db = await self.bot.pg_con.fetch("SELECT * FROM moderation WHERE guild_id = $1", guild_id)
        if not db:
            await self.bot.pg_con.execute("INSERT INTO moderation (guild_id, muted_role) VALUES ($1, $2)", guild_id, role.id)
            return await ctx.reply(f"<:greenTick:596576670815879169> {role.mention} set as muted role. This role will be used for `ami mute`, so check out if this role have the permissions you want muted members have.")

        await self.bot.pg_con_execute("UPDATE moderation SET muted_role = $1 WHERE guild_id = $2", role.id, guild_id)
        await ctx.reply(f"<:greenTick:596576670815879169> {role.mention} set as the new muted role.")

    @commands.command(help="Mute a member in the guild giving to him/her the muted role set with `ami muterole`.\nThis supports also multiple members provied.")
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, members: commands.Greedy[discord.Member]):
        guild_id = str(ctx.guild.id)
        db = await self.bot.pg_con.fetch("SELECT * FROM moderation WHERE guild_id = $1", guild_id)
        if not db:
            return await ctx.reply("<:redTick:596576672149667840> This guild has no muted role set up yet, use `ami muterole` to set the muted role and can use this command.")

        id = db[0]["muted_role"]
        muted_role = discord.utils.get(ctx.guild.roles, id=id)

        if not muted_role:
            return await ctx.reply("<:redTick:596576672149667840> The muted role set before for this guild was not found, re-set it.")

        for i in members:
            if isinstance(i, discord.Member):
                if i.top_role >= ctx.author.top_role:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't mute {i.mention} (Higher Role).")
            id = i.id
            try:
                await ctx.send(f'<:greenTick:596576670815879169> Successfully muted {i.name}.')
                await i.add_roles(muted_role)
            except discord.NotFound:
                await ctx.send(f"<:redTick:596576672149667840> Member(s) **{i.name}** not found.")


    @commands.command(help="Unmute a muted member in the guild, removing them the muted role.\nThis supports also multiple members at the same time.")
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, members: commands.Greedy[discord.Member]):
        guild_id = str(ctx.guild.id)
        db = await self.bot.pg_con.fetch("SELECT * FROM moderation WHERE guild_id = $1", guild_id)
        if not db:
            return await ctx.reply("<:redTick:596576672149667840> This guild has no muted role set up yet, use `ami muterole` to set the muted role and can use this command.")

        muted_id = db[0]["muted_role"]
        muted_role = discord.utils.get(ctx.guild.roles, id=muted_id)

        if not muted_role:
            return await ctx.reply("<:redTick:596576672149667840> The muted role set before for this guild was not found, re-set it.")
    

        for i in members:
            if isinstance(i, discord.Member):
                if i.top_role >= ctx.author.top_role:
                    await ctx.reply(f"<:redTick:596576672149667840> You can't unmute {i.mention} (Higher Role).")
            mutedRole = discord.utils.get(ctx.guild.roles, id=muted_id)
            if not mutedRole in i.roles:
                await ctx.reply(f"<:redTick:596576672149667840> {i.mention} is not muted, skipping.")
            try:
                await ctx.send(f'<:greenTick:596576670815879169> Successfully unmuted {i.mention}.')
                await i.remove_roles(mutedRole)
            except discord.NotFound:
                return await ctx.send(f"<:redTick:596576672149667840> Member(s) **{i.name}** not found.")
    

    @commands.command(help="Enable or disable the antispam in the guild! \"toogle\" must be 'on' or 'off'")
    @commands.has_permissions(manage_messages=True)
    async def antispam(self, ctx, toggle):
        guild_id = str(ctx.guild.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM antispam WHERE guild_id = $1", guild_id)

        if not data:
            s = "off"
            await self.bot.pg_con.execute("INSERT INTO antispam (guild_id, toggle) VALUES ($1, $2)", guild_id, s)
            return await ctx.send("This guild was not found in the database, so i've automatically added it, now you can set the antispam!")

        toggles = ["On", "on", "Off", "off"]
        if toggle not in toggles:
            return await ctx.send("Only `on` or `off` are accepted.")

        tg = data["toggle"]
        if toggle == tg:
            return await ctx.send(f"The antispam for this guild is already on `{toggle}`.")

        await self.bot.pg_con.execute("UPDATE antispam SET toggle = $1 WHERE guild_id = $2", toggle, guild_id)
        if toggle == "on":
            return await ctx.send(f"Antispam was succesfully set on **`{toggle}`**, from now all links sent will be deleted.")
        elif toggle == "off":
            return await ctx.send(f"Antispam was succesfully set on **`{toggle}`**, now no messages will be deleted.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild == None:
            return
        guild_id = str(message.guild.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM antispam WHERE guild_id = $1", guild_id)
        if not data:
            return
        
        tg = data["toggle"]
        if tg == "on":
            for channel in message.guild.channels:
                if message.content.startswith("https://cdn.discord") and not message.author.bot:
                    return

                if message.content.startswith("https://media.discord") and not message.author.bot:
                    return

                if message.content.startswith("https://canary.discord") and not message.author.bot:
                    return 

                if message.content.startswith("https://") and not message.author.bot:
                    try:
                        await message.delete()
                        await message.channel.send(f"{message.author.mention}, you can't send links in this guild while the **antispam** is __on__.")
                    except Exception:
                        pass

                elif message.content.startswith("http://") and not message.author.bot:
                    try:
                        await message.delete()
                        await message.channel.send(f"{message.author.mention}, you can't send links in this guild while the **antispam** is __on__.")
                    except Exception:
                        pass
        else:
            return



def setup(bot):
    bot.add_cog(Moderation(bot))

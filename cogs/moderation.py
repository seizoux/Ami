import discord
from discord.ext import commands, menus
import asyncio
import re
import humanize
import typing

class Paginate(menus.ListPageSource):

    def __init__(self, entries, *, per_page=15):
        entries = [f'`{index}.` {name}' for index, name in enumerate(entries, 1)]
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        embed = discord.Embed(color = 0xb81217)
        embed.set_author(name=f"{menu.ctx.guild.name} member list ({len(menu.ctx.guild.members)})")
        embed.description = '\n'.join(page)

        return embed

class Paginate2(menus.ListPageSource):

    def __init__(self, entries, *, per_page=15):
        entries = [f'`{index}.` {name}' for index, name in enumerate(entries, 1)]
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        embed = discord.Embed(color = 0xb81217)
        embed.description = '\n'.join(page)

        return embed

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(17, 12.0, commands.BucketType.user)
        self.category = "Moderation"
        self.lock = asyncio.Lock()
        self.guilds_dict = {}
        self.bad_words = {}
        self.bad_links = {}
        self.bot.loop.create_task(self.cache())   

    async def cache(self):
        await self.bot.wait_until_ready()
        db = await self.bot.db.fetch("SELECT * FROM antispam")
        for i in db:
            if i["toggle"] == "on":
                self.guilds_dict[int(i["guild_id"])] = True
            if i["bad_words"]:
                self.bad_words[int(i["guild_id"])] = i["bad_words"]

    def ratelimit_check(self, message):
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Moderation Loaded")

    @commands.command(help="Retrive a paginated list with all members in the guild, and the member top role (returns `No Roles` if no roles).",aliases=["memlist"])
    async def memberlist(self, ctx):
        p = sorted(ctx.guild.members, key=lambda m: m.top_role.position, reverse=True)
        entries = [f"**{member.name}#{member.discriminator}** | `{member.id}` | {f'<@&{member.top_role.id}>' if member.roles[1:] else 'No Roles'}" for member in p]
        pages = Paginate(entries)
        paginator = menus.MenuPages(source=pages, timeout=None, delete_message_after=True)
        await paginator.start(ctx)

    @commands.command(help="Retrive information about the mentioned role for the server, such like date creation.", aliases=["ri"])
    async def roleinfo(self, ctx, role: discord.Role):
        role = discord.utils.get(ctx.guild.roles, id=role.id)

        format = "%a, %d %b %Y %I:%M %p"

        em = discord.Embed(description=f"**Mention** : {role.mention}\n"
                            f"**ID** : {role.id}\n"
                            f"**Name** : {role.name}\n"
                            f"**Color** : {role.color}\n"
                            f"**Created** : {role.created_at.strftime(format)} ({humanize.naturaltime(role.created_at)})\n"
                            f"**Position** : {role.position}\n"
                            f"**Members** : {len(role.members)}\n"
                            f"**Permissions** : {', '.join([str(p[0]).replace('_', ' ').title() for p in role.permissions if p[1]])}", color=role.color)

        em.set_footer(text="Click the reaction to see the list with all members with the role.")
        msg = await ctx.send(embed=em)
        await msg.add_reaction("<:greenTick:596576670815879169>")

        def check(payload):
            return payload.message_id == msg.id and payload.emoji.name == "greenTick" and payload.user_id == ctx.author.id

        try:
            payload = await self.bot.wait_for("raw_reaction_add", check=check, timeout=30)
        except asyncio.TimeoutError:
            return await msg.delete()

        await msg.delete()

        d = []
        for i in ctx.guild.members:
            if role in i.roles:
                d.append(i)

        entries = [f"**{member.name}#{member.discriminator}** | `{member.id}` | {role.mention}" for member in d]
        pages = Paginate2(entries)
        paginator = menus.MenuPages(source=pages, timeout=None, delete_message_after=True)
        await paginator.start(ctx)

    @commands.command()
    @commands.is_owner()
    async def antispam_check(self, ctx):
        await ctx.send(f"**GUILDS IN CACHE**:\n{self.guilds_dict}\n\n**GUILDS IN BAD_WORDS**:\n{self.bad_words}")


    @commands.command()
    @commands.is_owner()
    async def dugongo(self, ctx):
        toleave = self.bot.get_guild(802339719152271361)
        await toleave.leave()
        print("Left Server")

    @commands.command(help="Give a role to the member mentioned just mentioning the role.\nYou can also mention multiple roles.")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def giverole(self, ctx, member: discord.Member, role: commands.Greedy[discord.Role]):
        if ctx.author.top_role < member.top_role:
            return await ctx.send(f"<:redTick:596576672149667840> You can't add roles to **{member.name}** because they have higher role than you.")

        try:
            await member.add_roles(role)
            await ctx.send(f"<:greenTick:596576670815879169> Added {''.join(role)} role(s) to **{member.name}**.")
        except Exception:
            return

    @commands.command(help="Remove roles from the member mentioned.\nYou can specify also multiple roles to remove.")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, role: commands.Greedy[discord.Role]):
        if member.top_role > ctx.me.top_role:
            return await ctx.send(f"<:redTick:596576672149667840> Can't remove roles to **{member.name}** because they have higher top role than me.")
        
        if ctx.author.top_role < member.top_role:
            return await ctx.send(f"<:redTick:596576672149667840> You can't remove roles to **{member.name}** because they have higher role than you.")

        for i in role:
            if i in member.roles:
                roled = discord.utils.get(ctx.guild.roles, name=i.name)
                await member.remove_roles(roled)

        await ctx.send(f"<:greenTick:596576670815879169> Removed {''.join(role)} role(s) at **{member.name}**")

    @commands.command(help="Create a channel with the given name in the guild.")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def createchannel(self, ctx, channel_name):
        await ctx.guild.create_text_channel(channel_name)
        await asyncio.sleep(4)
        d = discord.utils.get(ctx.guild.channels, name=channel_name)
        await ctx.send(f"<:greenTick:596576670815879169> Created {d.mention} channel!")

    @commands.command(help="Delete the mentioned channel if that is available in the guild.\nYou can also mention multiple channels to delete")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def deletechannel(self, ctx, channels: commands.Greedy[discord.TextChannel or discord.VoiceChannel]):
        for i in channels:
            chan = discord.utils.get(ctx.guild.channels, name=i.name)
            if chan:
                await chan.delete()
            else:
                return await ctx.send(f"<:redTick:596576672149667840> I can't delete the {i.mention} channel.")

        await ctx.send(f"<:greenTick:596576670815879169> Deleted **{''.join(x.name for x in channels)}** channels.")

    @commands.command(help="Set the slowmode of the channel where you send this command")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
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

    @commands.command(help="Add words you don't want to be sent to make me delete it when they was sent in this guild.\nThis can take also multiple words at same time, example: `ami addbadwords die fuck`\nIf you want to add a phrase, you can do something like `ami addbadwords \"fuck you dude\"`")
    @commands.has_permissions(manage_guild=True)
    async def addbadwords(self, ctx, *words:str):
        if len(words) >= 100:
            return await ctx.send("<:redTick:596576672149667840> You can't set more than __20__ bad words.")
        
        word = await self.bot.db.fetchrow("SELECT * FROM antispam WHERE guild_id = $1", str(ctx.guild.id))
        if not word:
            return await ctx.reply("<:redTick:596576672149667840> You need first to enable the automoderation (`ami automod on`).")

        if word["bad_words"]:
            if len(word["bad_words"]) > 100:
                return await ctx.send(f'<:redTick:596576672149667840> You already have __{len(word["bad_words"])}__ bad words set, this is the limit.')
    
        for i in words:
            if word["bad_words"]:
                if i in word["bad_words"]:
                    return await ctx.reply(f"<:redTick:596576672149667840> {i} is already set as a __bad word__.")
            d = await self.bot.db.fetchval("UPDATE antispam SET bad_words = array_append(bad_words, $1) WHERE guild_id = $2 RETURNING bad_words", i, str(ctx.guild.id))
            self.bad_words[ctx.guild.id] = d
        await ctx.send(f"<:greenTick:596576670815879169> Set **{', '.join(words)}** as bad words to detect.")

    @commands.command(help="Remove words from the bad words list set before, you can see the words with `ami automod badwords`.\nYou can remove also multiple words at same time.")
    @commands.has_permissions(manage_guild=True)
    async def rembadwords(self, ctx, *words:str):
        word = await self.bot.db.fetchrow("SELECT * FROM antispam WHERE guild_id = $1", str(ctx.guild.id))
        if not word:
            return await ctx.reply("<:redTick:596576672149667840> You need first to enable the automoderation (`ami automod on`).")

        if not word["bad_words"]:
            return await ctx.send("<:redTick:596576672149667840> This guild has no bad words set.")
    
        for i in words:
            if i not in word["bad_words"]:
                return await ctx.send(f"<:redTick:596576672149667840> {i} isn't in the __bad words__ list.")
        
            d = await self.bot.db.fetchval("UPDATE antispam SET bad_words = array_remove(bad_words, $1) WHERE guild_id = $2 RETURNING bad_words", i, str(ctx.guild.id))
            self.bad_words[ctx.guild.id] = d
        await ctx.send(f"<:greenTick:596576670815879169> Removed **{', '.join(words)}** as bad words to detect.")


# Clear Command
    @commands.command(help="Clear messages in `<amount>` range from the channel.")
    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount >= 250:
            return

        await ctx.channel.purge(limit=amount)

# Ban Command
    @commands.command(help="Ban a member from the guild.\nThis supports multiple mentions.")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, members: commands.Greedy[discord.Member], *, reason):
        limit = 10
        if ctx.author.id == self.bot.owner_id:
            limit = 50
        if len(members) > limit:
            return await ctx.reply(f"<:redTick:596576672149667840> You can't ban more than `{limit}` people at same time.")

        if not members:
            return await ctx.send(f"{ctx.author.mention} please specify at least one valid member to ban.")

        for i in members:
            if isinstance(i, discord.Member):
                if i.top_role >= ctx.author.top_role:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't ban **{i.name}** (Higher Role).")
            id = i.id
            try:
                await ctx.guild.ban(discord.Object(id=id), reason=reason)
                s = self.bot.get_user(i.id) or (await self.bot.fetch_user(i.id))
                if not s:
                    return await ctx.send(f"{ctx.author.mention} member `{i}` was not found.")
                try:
                    await s.send(f"You got banned from **{ctx.guild.name}** for `{reason}`.")
                except Exception:
                    pass
            except Exception:
                await ctx.send(f"<:redTick:596576672149667840> Member **{i.name}** not found.")

        final = ", ".join([i.name for i in members])
        await ctx.send(f'<:greenTick:596576670815879169> Succesfully banned **{final}** for `{reason}`.')

# Unban Command
    @commands.command(help="Unban a member banned in this guild using their IDs.\nThis supports also multiple members at the same time.\n")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, members: commands.Greedy[discord.User]):
        limit = 10
        if ctx.author.id == self.bot.owner_id:
            limit = 50
        if len(members) > limit:
            return await ctx.reply(f"<:redTick:596576672149667840> You can't unban more than `{limit}` people at same time.")

        for i in members:
            s = self.bot.get_user(i.id) or (await self.bot.fetch_user(i.id))
            invite = await ctx.guild.invites()
            try:
                await s.send(f"You got unbanned from **{ctx.guild.name}**: {invite[0]}")
            except Exception:
                pass
            try:
                await ctx.guild.unban(discord.Object(id=i.id))
            except discord.NotFound:
              #don't have to stop all other bans
              return await ctx.send(f"<:redTick:596576672149667840> Member(s) **{i.name}** not found / not banned.")
        
        await ctx.send(f'<:greenTick:596576670815879169> Succesfully unbanned **{", ".join([i.name for i in members])}**.')

# Kick Command
    @commands.command(help="Kick a member from the guild.\nThis supports also multiple mentions.")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *, reason):
        limit = 10
        if ctx.author.id == self.bot.owner_id:
            limit = 50
        if len(members) > limit:
            return await ctx.reply(f"<:redTick:596576672149667840> You can't kick more than `{limit}` people at same time.")

        if not members:
            return await ctx.send(f"{ctx.author.mention} please specify at least one valid member to kick.")

        for i in members:
            id = i.id
            try:
                await ctx.guild.kick(discord.Object(id=id), reason=reason)
            except discord.NotFound:
                await ctx.send(f"<:redTick:596576672149667840> Member(s) {i.name} not found.")

        await ctx.send(f'<:greenTick:596576670815879169> Succesfully kicked **{", ".join([i.mention for i in members])}** for `{reason}`.')

    @commands.command(help="Set the role i need to use when you invoke `ami mute`.\nThis role will be set to the members you send in `ami mute` as muted role, so be sure to have set the right permissions on this role.")
    @commands.has_permissions(manage_guild=True)
    async def muterole(self, ctx, role: discord.Role):
        role = discord.utils.get(ctx.guild.roles, id=role.id)
        if not role:
            return await ctx.reply(f"<:redTick:596576672149667840> {role} was not found in the guild roles.")

        guild_id = str(ctx.guild.id)
        db = await self.bot.db.fetch("SELECT * FROM moderation WHERE guild_id = $1", guild_id)
        if not db:
            await self.bot.db.execute("INSERT INTO moderation (guild_id, muted_role) VALUES ($1, $2)", guild_id, role.id)
            return await ctx.reply(f"<:greenTick:596576670815879169> {role.mention} set as muted role. This role will be used for `ami mute`, so check out if this role have the permissions you want muted members have.")

        await self.bot.db.execute("UPDATE moderation SET muted_role = $1 WHERE guild_id = $2", role.id, guild_id)
        await ctx.reply(f"<:greenTick:596576670815879169> {role.mention} set as the new muted role.")

    @commands.command(help="Mute a member in the guild giving to him/her the muted role set with `ami muterole`.\nThis supports also multiple members provied.")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx, members: commands.Greedy[discord.Member]):
        limit = 10
        if ctx.author.id == self.bot.owner_id:
            limit = 50
        if len(members) > limit:
            return await ctx.reply(f"<:redTick:596576672149667840> You can't mute more than `{limit}` people at same time.")

        guild_id = str(ctx.guild.id)
        db = await self.bot.db.fetch("SELECT * FROM moderation WHERE guild_id = $1", guild_id)
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
                await i.add_roles(muted_role)
            except discord.NotFound:
                await ctx.send(f"<:redTick:596576672149667840> Member(s) **{i.name}** not found.")

        await ctx.send(f'<:greenTick:596576670815879169> Succesfully muted **{", ".join([i.name for i in members])}**.')

    @commands.command(help="Unmute a muted member in the guild, removing them the muted role.\nThis supports also multiple members at the same time.")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx, members: commands.Greedy[discord.Member]):
        limit = 10
        if ctx.author.id == self.bot.owner_id:
            limit = 50
        if len(members) > limit:
            return await ctx.reply(f"<:redTick:596576672149667840> You can't unmute more than `{limit}` people at same time.")

        guild_id = str(ctx.guild.id)
        db = await self.bot.db.fetch("SELECT * FROM moderation WHERE guild_id = $1", guild_id)
        if not db:
            return await ctx.reply("<:redTick:596576672149667840> This guild has no muted role set up yet, use `ami muterole` to set the muted role and can use this command.")

        muted_id = db[0]["muted_role"]
        muted_role = discord.utils.get(ctx.guild.roles, id=muted_id)

        if not muted_role:
            return await ctx.reply("<:redTick:596576672149667840> The muted role set before for this guild was not found, re-set it.")
    

        for i in members:
            if isinstance(i, discord.Member):
                if i.top_role >= ctx.author.top_role:
                    return await ctx.reply(f"<:redTick:596576672149667840> You can't unmute {i.mention} (Higher Role).")
            mutedRole = discord.utils.get(ctx.guild.roles, id=muted_id)
            if not mutedRole in i.roles:
                await ctx.reply(f"<:redTick:596576672149667840> {i.mention} is not muted, skipping.")
            try:
                await i.remove_roles(mutedRole)
            except discord.NotFound:
                return await ctx.send(f"<:redTick:596576672149667840> Member(s) **{i.name}** not found.")
    
        await ctx.send(f'<:greenTick:596576670815879169> Succesfully unmuted **{", ".join([i.name for i in members])}**.')

    @commands.command(help="Enable or disable the automod in the guild: `<toogle>` must be 'on' or 'off'.\nEnabling the automod will result in some things:\n\n"
                           "`Bad Words`: Set your custom list of bad words to make me delete them when sent in this guild.\n"
                           "`Anti-Spam (Auto-Ban)`: The member get automatically banned if i see him spamming.\n"
                           "`No Links`: Every link sent will be automatically deleted.")

    @commands.has_permissions(manage_guild=True)
    async def automod(self, ctx, toggle):
        guild_id = str(ctx.guild.id)
        data = await self.bot.db.fetchrow("SELECT * FROM antispam WHERE guild_id = $1", guild_id)

        if not data:
            s = toggle
            await self.bot.db.execute("INSERT INTO antispam (guild_id, toggle) VALUES ($1, $2)", guild_id, s)
            return await ctx.send(f"<:greenTick:596576670815879169> Automod was succesfully set to **`{toggle}`**.")

        if toggle == "badwords":
            if data["bad_words"]:
                em = discord.Embed(title=f"{ctx.guild.name} bad words list", description=f"This is the list of the words you can't say in this guild:\n`{', '.join(data['bad_words'])}`", color = self.bot.color)
                v = "disabled"
                if data["toggle"] == "on":
                    v = 'enabled'
                em.set_footer(text=f"Auto-Moderation is {v}.", icon_url=self.bot.user.avatar_url)
                return await ctx.send(embed=em)
            return await ctx.send("<:redTick:596576672149667840> This guild has no __bad words__ set.")

        toggles = ["On", "on", "Off", "off"]
        if toggle not in toggles:
            return await ctx.send("<:redTick:596576672149667840> Only `on` or `off` are accepted.")

        tg = data["toggle"]
        if toggle == tg:
            return await ctx.send(f"<:greenTick:596576670815879169> The automod for this guild is already on `{toggle}`.")

        await self.bot.db.execute("UPDATE antispam SET toggle = $1 WHERE guild_id = $2", toggle, guild_id)
        if toggle == "on":
            self.guilds_dict[ctx.guild.id] = True
            return await ctx.send(f"<:greenTick:596576670815879169> Automod was succesfully set to **`{toggle}`**.")
        elif toggle == "off":
            if ctx.guild.id in self.guilds_dict:
                del self.guilds_dict[ctx.guild.id]
            return await ctx.send(f"<:greenTick:596576670815879169> Automod was succesfully set to **`{toggle}`**.")

    @commands.Cog.listener("on_message")
    async def super_duper_ultra_best_antispam_die(self, message):

        if message.guild == None:
            return

        if message.guild.id not in self.guilds_dict:
            return

        if message.author.id == self.bot.user.id:
            return

        if isinstance(message.author, discord.User):
            return

        if message.author.top_role > message.guild.me.top_role:
            return

        retry_after = self.ratelimit_check(message)
        if retry_after:
            try:
                await message.guild.ban(discord.Object(id = message.author.id), reason = "Spam Detect (Auto-Mod ON)", delete_message_days = 7)
                em = discord.Embed(description=f"<:redTick:596576672149667840> {message.author.mention} permanently banned for : `Spam Detect (Auto-Mod ON)`.", color = self.bot.color)
                em.set_author(name=f"Detected spam from {message.author.name}.")
                await message.channel.send(embed=em, delete_after=60)
            except Exception:
                return
            
            try:
                message.author.send(f"<:redTick:596576672149667840> You got permanently banned from **{message.guild.name}** for **`Detected Spam`**.")
            except Exception:
                return

    @commands.Cog.listener("on_message")
    async def bad_word_usage(self, message):

        if message.guild is None:
            return

        if message.guild.id not in self.guilds_dict:
            return

        if message.author.id == self.bot.user.id:
            return

        if message.guild.id not in self.bad_words:
            return

        if isinstance(message.author, discord.User):
            return

        if message.author.top_role > message.guild.me.top_role:
            return
        
        content = message.content
        bad_words = self.bad_words[message.guild.id]
        if any(i in content for i in bad_words):

            await message.delete()
            if self.lock.locked(): # already send
                return

            await self.lock.acquire()
            try:
                em = discord.Embed(title="⚠ Bad Word Usage", description=f"{message.author.mention} don't use bad words here thanks.", color = self.bot.color)
                await message.channel.send(embed=em, delete_after = 5)
                await asyncio.sleep(5)
            finally:
                self.lock.release()


    @commands.Cog.listener("on_message")
    async def no_links(self, message):

        if message.guild == None:
            return

        if message.guild.id not in self.guilds_dict:
            return

        if message.author.id == self.bot.user.id:
            return
        
        if isinstance(message.author, discord.User):
            return

        if message.author.top_role > message.guild.me.top_role:
            return

        url = re.match("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", message.content)
        if url:
            if re.match("http[s]?://(?:www)?tenor.com/view/.+$", message.content):
                return

            if re.match("(https?:\/\/)?(media|cdn)\.discord(app)?\.(com|net)\/attachments\/([0-9]+)\/([0-9]+)\/([\S]+)", message.content):
                return

            if re.match("http[s]?://(?:.+\.)?discord.com/channels/[0-9]+/[0-9]+/[0-9]+", message.content):
                return

            try:
                await message.delete()
                em = discord.Embed(description=f"<:redTick:596576672149667840> {message.author.mention}, links are not allowed here.", color = self.bot.color)
                await message.channel.send(embed=em, delete_after=30)
            except Exception:
                pass

    @commands.Cog.listener("on_message_edit")
    async def check_edit(self, before, after):
        if after.author.bot:
            return
        
        await self.bad_word_usage(after)
        await self.no_links(after)

def setup(bot):
    bot.add_cog(Moderation(bot))

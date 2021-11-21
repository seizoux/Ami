import discord
from discord.ext import commands, tasks
import datetime
import random
from util.defs import is_team
import asyncio
import typing
import weakref
from discord import Webhook, AsyncWebhookAdapter
import io

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._lock = weakref.WeakValueDictionary()
        self._webhook = Webhook.from_url

        self._cached = {}

    async def get_mod_logs(self, guild: int):
        if guild in self._cached:
            data = self._cached[guild]
        else:
            data = await self.bot.db.fetch("SELECT * FROM modlogs WHERE guild_id = $1", guild)
            self._cached[guild] = data

        if not data:
            return False

        return data

    async def send_log(self, guild: int, content: typing.Union[str, discord.Embed], channel: discord.TextChannel, webhook: str = None):
        lock = self._lock.get(guild)
        if lock is None:
            self._lock[guild] = lock = asyncio.Lock()
        
        async with lock:
            if webhook:
                try:
                    if type(content) is discord.Embed:
                        return await self._webhook(webhook, adapter=AsyncWebhookAdapter(self.bot.session)).send(embed=content, wait=True)
                    return await self._webhook(webhook, adapter=AsyncWebhookAdapter(self.bot.session)).send(content, wait=True)
                except discord.NotFound:
                    return

            ch = self.bot.get_channel(channel)
            if ch:
                if type(content) is discord.Embed:
                    return await ch.send(embed=content)
                return await ch.send(embed=content)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Logging loaded")

    @commands.group(help="Setup modlogs for the current guilds, use subcommands.")
    async def modlog(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.send_help()

    @modlog.command(help="Set the channel where log all events.")
    async def config(self, ctx, channel: discord.TextChannel):
        if ctx.me.guild_permissions.manage_webhooks:
            if channel.permissions_for(ctx.guild.me).manage_webhooks:
                wb = await channel.create_webhook(name='Ami Mod-Logs', avatar=await self.bot.user.avatar_url.read())
                await self.bot.db.execute("INSERT INTO modlogs (guild_id, channel_id, webhook) VALUES ($1, $2, $3)", ctx.guild.id, channel.id, str(wb.url))
                return await ctx.send(f"Alright, {channel.mention} has been set as modlog channel for this guild.")
            else:
                return await ctx.reply("❌ I need the `Manage Webhooks` permission in that channel to config the modlogs.")
        else:
            return await ctx.reply("❌ I need the `Manage Webhooks` permission to config the modlogs.")

    @modlog.command(help="Delete the modlog configuration for the current guild")
    async def delete(self, ctx):
        data = await self.bot.db.fetch("SELECT * FROM modlogs WHERE guild_id = $1", ctx.guild.id)
        if not data:
            return await ctx.reply("❌ This guild has not modlog setup.")

        await self.bot.db.execute("DELETE FROM modlogs WHERE guild_id = $1", ctx.guild.id)
        await ctx.send("Modlogs config deleted for this guild, config it again to receive all events in the channel.")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        if not message.guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(message.guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"Message Deleted",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )
        
        em.add_field(name='Message', value=message.content)
        em.add_field(name="Channel", value=message.channel.mention)
        em.set_author(name=str(message.author), icon_url=message.author.avatar_url)
        em.set_thumbnail(url=message.author.avatar_url)
        await self.send_log(message.guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        if messages[0].author.bot:
            return

        if not messages[0].guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(messages[0].guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"Bulk Message Delete",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )

        entries = await messages[0].guild.audit_logs(limit=1, action=discord.AuditLogAction.message_bulk_delete).flatten()
        c = entries[0]
        em.add_field(name='Deleted', value=f"{c.extra.count} messages deleted")
        em.add_field(name="Channel", value=c.target.mention)
        await self.send_log(messages[0].guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot:
            return

        if not after.guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(after.guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"Message Edited",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )

        em.add_field(name='Before', value=f"{before.content}")
        em.add_field(name="After", value=f"{after.content}")
        em.set_author(name=str(after.author), icon_url=after.author.avatar_url)
        em.set_thumbnail(url=after.author.avatar_url)
        await self.send_log(after.guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_webhooks_update(self, channel):
        if not channel.guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(channel.guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"Webhook Updated",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )

        entries = await channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.webhook_update).flatten()
        c = entries[0]
        em.add_field(name='Channel', value=f"{channel.mention}")
        em.add_field(name="Channel ID", value=f"{channel.id}")
        em.add_field(name="Webhook ID", value=f"{c.target.id}")
        await self.send_log(channel.guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(member.guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"New Member Joined",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )

        em.add_field(name='Member', value=f"{member.mention}")
        em.add_field(name="Member ID", value=f"{member.id}")
        em.add_field(name="Roles", value=f"{''.join([r.mention for r in member.roles[1:]])}")
        await self.send_log(member.guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not member.guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(member.guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"Member Left",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )

        em.add_field(name='Member', value=f"{member.mention}")
        em.add_field(name="Member ID", value=f"{member.id}")
        em.add_field(name="Roles", value=f"{''.join([r.mention for r in member.roles[1:]])}")
        await self.send_log(member.guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if not after.guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(after.guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"Member Updated",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )

        r = before.roles
        n = before.display_name

        if after.roles == r and after.display_name == n:
            return

        em.add_field(name='Member', value=f"{after.mention}")
        em.add_field(name="Member ID", value=f"{after.id}")
        if after.roles != r:
            em.add_field(name="Roles", value=f"{' '.join([r.mention for r in after.roles[1:]])}")
        if after.display_name != n:
            em.add_field(name="Nickname", value=f"{before.display_name} → {after.display_name}")
        await self.send_log(after.guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        if not after.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(after.guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"Guild Updated",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )

        a = str(before.icon_url)
        u = before.name

        if after.name != u:
            em.add_field(name="New Name", value=f"{before.name} → {after.name}")
        if after.icon_url != a:
            em.add_field(name="New Icon", value=f"{before.icon_name} → {after.icon_name}")
        await self.send_log(after.guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        if not role.guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(role.guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"New Role Created",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )

        em.add_field(name='Role', value=f"{role.mention}")
        em.add_field(name="Role ID", value=f"{role.id}")
        em.add_field(name="Role Permissions", value=f"{', '.join([str(p[0]).replace('_', ' ').title() for p in role.permissions if p[1]])}")
        em.add_field(name="Role Color", value=f"{role.color}")
        await self.send_log(role.guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        if not role.guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(role.guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"Role Deleted",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )

        em.add_field(name='Role', value=f"{role.mention}")
        em.add_field(name="Role ID", value=f"{role.id}")
        em.add_field(name="Role Permissions", value=f"{', '.join([str(p[0]).replace('_', ' ').title() for p in role.permissions if p[1]])}")
        em.add_field(name="Role Color", value=f"{role.color}")
        await self.send_log(role.guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        if not after.guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(after.guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"Role Updated",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )

        name = before.name
        color = before.color
        permissions = before.permissions

        em.add_field(name='Role', value=f"{after.mention}")
        em.add_field(name="Role ID", value=f"{after.id}")
        if after.permissions != permissions:
            em.add_field(name="New Permissions", value=f"{', '.join([str(p[0]).replace('_', ' ').title() for p in after.permissions if not p in permissions])}")
        if after.color != color:
            em.add_field(name="New Color", value=f"{before.color} → {after.color}")
        if after.name != name:
            em.add_field(name="New Name", value=f"{before.name} → {after.name}")
        await self.send_log(after.guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        if not guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"Emojis Updated",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )

        if after != before:
            if len([str(e) for e in after if not e in before]) != 0:
                em.add_field(name='New Emojis', value=f"{''.join([str(e) for e in after if not e in before])}")
        em.add_field(name="Total Emojis Now", value=f"{len(guild.emojis)}")
        await self.send_log(guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_guild_available(self, guild):
        if not guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"Guild is now available!",
            description = 'Guild was unavailable, but now is back',
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )
        await self.send_log(guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_guild_unavailable(self, guild):
        if not guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"Guild is unavailable!",
            description = 'Guild has became unavailable, wait until discord makes it available again.',
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )
        await self.send_log(guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(member.guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"Voice State Update",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )

        em.add_field(name='Member', value=f"{member.mention}")
        em.add_field(name="Voice State", value=f"{before.channel.mention if before.channel else 'N/A'} → {after.channel.mention if after.channel else 'N/A'}")
        await self.send_log(member.guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if not guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(guild.id)

        if d is False:
            return

        entries = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
        c = entries[0]
        em = discord.Embed(
            color = self.bot.color,
            description = f"**Banned**: {user.mention} ({user.id})\n"
            f"**Reason**: {c.reason}\n**Responsabile Moderator**: {c.user.mention}",
            timestamp = datetime.datetime.utcnow()
        )
        em.set_author(name=f"{str(user)} has been banned!", icon_url=user.avatar_url)
        await self.send_log(guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if not guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"Member Unbanned",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )

        em.add_field(name='Member', value=f"{str(user)}")
        await self.send_log(guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if not channel.guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(channel.guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"Channel Deleted",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )

        em.add_field(name='Channel', value=f"#{channel.name}")
        em.add_field(name='Channel ID', value=f"{channel.id}")
        await self.send_log(channel.guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        if not channel.guild.id in [800176902765674496, 909527052070313984]:
            return

        d = await self.get_mod_logs(channel.guild.id)

        if d is False:
            return

        em = discord.Embed(
            title = f"New Channel Created",
            color = self.bot.color,
            timestamp = datetime.datetime.utcnow()
        )

        em.add_field(name='Channel', value=f"{channel.mention}")
        em.add_field(name='Channel ID', value=f"{channel.id}")
        await self.send_log(channel.guild.id, em, d[0]['channel_id'], d[0]['webhook'] if d[0]['webhook'] else None)

def setup(bot):
    bot.add_cog(Logging(bot))

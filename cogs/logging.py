import discord
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands
import asyncio
import aiohttp

class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logging Loaded")


    @commands.command()
    async def setlogs(self, ctx, channel: discord.TextChannel, on_off=None):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(ctx.guild.id))
        if not db:
            on_off = "on"
            if channel.permissions_for(ctx.me).manage_webhooks:
                pfp = await self.bot.user.avatar_url.read()
                webhook = await channel.create_webhook(name="Ami - Log System", avatar=pfp)
                await self.bot.pg_con.execute("INSERT INTO logs (guild_id, channel, toggle, webhook) VALUES ($1, $2, $3, $4)", str(ctx.guild.id), channel.id, on_off, webhook.url)
                em = discord.Embed(title="<:greenTick:596576670815879169> Logs activated!", description="Logs are basically a report of every action executed in your guild, from now i'll send **all** action in the channel you have specified before. Here's the list of all actions i will log there:\n\n"
                "`Bulk Message Delete` : Mass delete of messages\n"
                "`Voice Update (member)` : Voice update\n"
                "`Guild Channel (create)` : Creation of new channels\n"
                "`Guild Channel (delete)` : Channel deleted\n"
                "`Guild Channel (pin)` : Message pinned\n"
                "`Guild Channel (update)` : Update of a channel\n"
                "`Guild Emojis (update)` : Added/removed emojis\n"
                "`Guild Integrations (update)` : New integrations added\n"
                "`Guild Role (create)` : New role created\n"
                "`Guild Role (delete)` : Role deleted\n"
                "`Guild Role (update)` : Role update\n"
                "`Guild Error (unavailable)` : Guild not accessible\n"
                "`Guild Update (guild)` : Update on the server itself\n"
                "`Guild Invite (create)` : New invite created\n"
                "`Guild Invite (delete)` : Invite deleted\n"
                "`Guild Ban (member)` : Member banned\n"
                "`Guild Join (member)` : New members\n"
                "`Guild Kick (member)` : Member kicked\n"
                "`Guild Unban (member)` : Member unbanned\n"
                "`Guild Update (member)` : Member update\n"
                "`Guild Message (delete)` : Message deleted\n"
                "`Guild Message (edit)` : Message edited\n", color = 0xffcff1)
                return await ctx.send(embed=em)
            else:
                return await ctx.reply(":x: I need the `Manage Webhook` permission in that channel to log events.")
        else:
            if channel.id == db["channel"]:
                return await ctx.reply(f":x: {channel.mention} is already the log channel.")
            else:
                if channel.permissions_for(ctx.me).manage_webhooks:
                    pfp = await self.bot.user.avatar_url.read()
                    webhook = await channel.create_webhook(name="Ami - Log System", avatar=pfp)
                    await self.bot.pg_con.execute("UPDATE logs SET channel = $1 WHERE guild_id = $2", channel.id, str(ctx.guild.id))
                    await asyncio.sleep(2)
                    await self.bot.pg_con.execute("UPDATE logs SET webhook = $1 WHERE guild_id = $2", webhook.url, str(ctx.guild.id))
                    await ctx.reply(f":white_check_mark: {channel.mention} set as default log channel!")
                else:
                    return await ctx.reply(":x: I need the `Manage Webhook` permission in that channel to log events.")

            if on_off:
                s = ['on', 'off']
                if on_off not in s:
                    return await ctx.reply(":x: `[on_off]` argument can be only `on` or `off`.")

                if on_off == db['toggle']:
                    return await ctx.reply(f":x: Logs are already plugged `{on_off}`")
            else:
                return

            await self.bot.pg_con.execute("UPDATE logs SET toggle = $1 WHERE guild_id = $2", on_off, str(ctx.guild.id))
            return await ctx.reply(f":white_check_mark: Logs plugged `{on_off}`!")
        





    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(messages[0].guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="Bulk Message Delete", color = 0xffcff1)
            em.add_field(name="Amount", value=f"{len(messages)}")
            em.add_field(name="Channel", value=f"{messages[0].channel.name}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)
        
        

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(channel.guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="Channel Created", color = 0xffcff1)
            em.add_field(name="Name", value=f"{channel.name}")
            em.add_field(name="ID", value=f"{channel.id}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(channel.guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="Channel Deleted", color = 0xffcff1)
            em.add_field(name="Name", value=f"{channel.name}")
            em.add_field(name="ID", value=f"{channel.id}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_channel_pins_update(self, channel, last_pin):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(channel.guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="New Message Pinned", color = 0xffcff1)
            em.add_field(name="Channel", value=f"{channel.name}")
            em.add_field(name="Message", value=f"{last_pin}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(after.guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="Channel Updated", color = 0xffcff1)
            em.add_field(name="Before", value=f"{before}")
            em.add_field(name="After", value=f"{after}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="Emojis Updated", color = 0xffcff1)
            em.add_field(name="Before", value=f"{before}")
            em.add_field(name="After", value=f"{after}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_integrations_update(self, guild):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="Integration Updated", color = 0xffcff1)
            em.add_field(name="Update", value=f"{guild}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(role.guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="New Role Created", color = 0xffcff1)
            em.add_field(name="Role", value=f"{role.mention}")
            em.add_field(name="ID", value=f"{role.id}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(role.guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="Role Deleted", color = 0xffcff1)
            em.add_field(name="Role", value=f"{role.name}")
            em.add_field(name="ID", value=f"{role.id}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(after.guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="Role Updated", color = 0xffcff1)
            em.add_field(name="Before", value=f"{before}")
            em.add_field(name="After", value=f"{after}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_unavailable(self, guild):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title=":x: Guild Unavailable", description="I can't log the action because this is a discord side issue.", color = 0xffcff1)
            em.set_footer(text="Action not logged in audit logs.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(after.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="Guild Updated", color = 0xffcff1)
            em.add_field(name="Before", value=f"{before}")
            em.add_field(name="After", value=f"{after}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(invite.guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="New Invite Created", color = 0xffcff1)
            em.add_field(name="Invite", value=f"{invite}")
            em.add_field(name="Author", value=f"{invite.author}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(invite.guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="Invite Deleted", color = 0xffcff1)
            em.add_field(name="Invite", value=f"{invite}")
            em.add_field(name="Author", value=f"{invite.author}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        if guild.id == 336642139381301249:
            channel = await self.bot.get_channel(381963689470984203)
            return await channel.send(f"<:smoothbrain:648662592201555969> **{user.name}#{user.discriminator}** got banned, send __f__ in chat.")
            
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="Member Banned", color = 0xffcff1)
            em.add_field(name="Member", value=f"{user.name}#{user.discriminator}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(member.guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="New Member Joined", color = 0xffcff1)
            em.add_field(name="Member", value=f"{member.name}#{member.discriminator}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(member.guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="Member Left", color = 0xffcff1)
            em.add_field(name="Member", value=f"{member.name}#{member.discriminator}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        if guild.id == 336642139381301249:
            channel = await self.bot.get_channel(381963689470984203)
            return await channel.send(f"<:smoothbrain:648662592201555969> **{user.name}#{user.discriminator}** got unbanned, send __pepe__ in chat.")

        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(user.guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="Member Unbanned", color = 0xffcff1)
            em.add_field(name="Member", value=f"{user.name}#{user.discriminator}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(after.guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="Member Updated", color = 0xffcff1)
            em.add_field(name="Before", value=f"{before}")
            em.add_field(name="After", value=f"{after}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(message.guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="Message Deleted", color = 0xffcff1)
            em.add_field(name="Message", value=f"{message.content}")
            em.add_field(name="Message Author", value=f"{message.author}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(after.guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            em = discord.Embed(title="Message Edited", color = 0xffcff1)
            em.add_field(name="Before", value=f"{before.content}")
            em.add_field(name="After", value=f"{after.content}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)


    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        db = await self.bot.pg_con.fetchrow("SELECT * FROM logs WHERE guild_id = $1", str(member.guild.id))
        if not db:
            return
        
        link = db["webhook"]
        async with self.session as session:
            webhook = Webhook.from_url(link, adapter=AsyncWebhookAdapter(session))

            voice1 = ""
            try:
                voice1 = await self.bot.get_channel(before.channel.id)
            except Exception:
                voice1 = "None"
                
            voice2 = ""
            try:
                voice2 = await self.bot.get_channel(after.channel.id)
            except Exception:
                voice2 = "None"

            em = discord.Embed(title="Member Voice Updated", color = 0xffcff1)
            em.add_field(name="Member", value=f"{member.name}#{member.discriminator}")
            em.add_field(name="Before", value=f"{voice1}")
            em.add_field(name="After", value=f"{voice2}")
            em.set_footer(text="Action logged in audit logs, go there to see more info.")
            await webhook.send(embed=em)


def setup(bot):
    bot.add_cog(Logging(bot))

import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Moderation Loaded")

    @commands.command()
    @commands.is_owner()
    async def dugongo(self, ctx):
        toleave = self.bot.get_guild(802339719152271361)
        await toleave.leave()
        print("Left Server")

    # Clear Command
    @commands.command(help="Delete X messages")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount)

    # Ban Command
    @commands.command(help="Ban a member from the guild")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f":no_entry_sign: **Banned** {member.mention} by {ctx.author.mention}.")
        return

    # Unban Command
    @commands.command(help="Unban a member from the guild (name#0000)")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_disc = member.split('#')

        for banned_entry in banned_users:
            user = banned_entry.user

            if (user.name, user.discriminator) == (member_name, member_disc):
                await ctx.guild.unban(user)
                await ctx.send(":free: **Unbanned**" + member_name + f"by {ctx.author.mention}")
                return

    # Kick Command
    @commands.command(help="Kick a member from the guild")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f":raised_back_of_hand: **Kicked** {member.mention}")
        return

    # Mute Command
    @commands.command(help="Mute someone in the guild")
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, member: discord.Member):
        guild = ctx.guild
        muted_role = discord.utils.get(guild.roles, name="Muted")

        if not muted_role:
            muted_role = await guild.create_role(name="Muted")

        for channel in guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False, read_message_history=True,
                                          read_messages=False)

            await member.edit(roles=[])
            await member.add_roles(muted_role)

            await ctx.send(f":no_bell: {member.mention} muted by {ctx.author.mention}.")
            return

    # Unmute Command
    @commands.command(help="Unmute someone in the guild")
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, member: discord.Member):
        mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
        channel = self.bot.get_channel(802117792941473814)

        await member.remove_roles(mutedRole)

        await ctx.send(f":bell: **Unmuted** {member.mention} by {ctx.author.mention}")
        return


def setup(bot):
    bot.add_cog(Moderation(bot))

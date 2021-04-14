import datetime

import discord
import humanize
import psutil
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Info Loaded")

    @commands.command(help="See info about me and my dev")
    async def info(self, ctx):
        cpu_usage = psutil.cpu_percent()
        num_users = len(self.bot.users)
        m = psutil.Process().memory_full_info()
        ram_usage = humanize.naturalsize(m.rss)
        wlat = (round(self.bot.latency * 1000, 2))
        cmd = len(self.bot.commands)
        supp = "[Click Here!](https://discord.gg/ZcErEwmVYu)"
        me = "[Click Here!](https://discord.com/users/144126010642792449)"
        web = "[Click Here!](https://amidiscord.xyz/)"
        em = discord.Embed(title="<:info:819702267480899634> Bot Information",
                           description=f"<:greenarrow:819706481883611197> Guilds » `{len(self.bot.guilds)}`\n<:greenarrow:819706481883611197> Members » `{num_users}`\n<:greenarrow:819706481883611197> Bot Commands » `{cmd}`\n<:greenarrow:819706481883611197> CPU Usage » `{cpu_usage}%`\n<:greenarrow:819706481883611197> Ram Usage » `{ram_usage}/8 GB`\n<:greenarrow:819706481883611197> Websocket Latency » `{wlat}ms`\n<:greenarrow:819706481883611197> Support Server » **{supp}**\n<:greenarrow:819706481883611197> Website » **{web}**",
                           color=0xffcff1)
        em.add_field(name=f"<:info:819702267480899634> Developer Information",
                     value=f"<:greenarrow:819706481883611197> Name » `Daishiky#0828`\n<:greenarrow:819706481883611197> Based in » `Europe/Italy`\n<:greenarrow:819706481883611197> Age » `18y/o`\n<:greenarrow:819706481883611197> DM Me » **{me}**",
                     inline=False)
        em.set_thumbnail(url=self.bot.user.avatar_url)
        em.set_footer(text="Huge hug to everyone! ®")
        em.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=em)
        return

    @commands.command(help="See info about a member")
    async def ui(self, ctx, *, user: discord.Member = None):
        if user is None:
            user = ctx.author

        author_id = str(user.id)
        guild_id = str(ctx.guild.id)

        data = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", author_id)

        if not data:
            await self.bot.pg_con.execute("INSERT INTO users (user_id, wallet, bank) VALUES ($1, 100, 100)", author_id)

        date_format = "%a, %d %b %Y %I:%M %p"
        tz = data[0]["tz"]

        if not tz:
            tz = "Not provided yet."

        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        if len(user.roles) > 1:
            role_string = ' '.join([r.mention for r in user.roles][1:])
        else:
            role_string = "No roles."
        perm_string = ', '.join(
            str(p[0]).replace("_", " ").title()
            for p in user.guild_permissions
            if p[1]
        )

        embed = discord.Embed(color=0xdfa3ff,
                              description=f"<:gsarrow:819706480714055681> **ID** » `{user.id}`\n<:gsarrow:819706480714055681> **Joined** » `{user.joined_at.strftime(date_format)}`\n<:gsarrow:819706480714055681> **Registered** » `{user.created_at.strftime(date_format)}`\n<:gsarrow:819706480714055681> **Roles [{(len(user.roles) - 1)}]** » {role_string}")
        embed.add_field(name="Guild permissions", value=f"```css\n{perm_string}\n```", inline=False)
        embed.set_footer(text='Timezone: ' + str(tz))
        embed.set_author(name=str(user), icon_url=user.avatar_url)
        embed.set_thumbnail(url=user.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))

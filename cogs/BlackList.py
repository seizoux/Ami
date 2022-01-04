import discord
from discord.ext import commands
from util.defs import is_team


class BlackList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "BlackList"

    @commands.group(name="blacklist", invoke_without_command=True)
    @is_team()
    async def blacklist(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command": "blacklist"})

    @blacklist.command(name="add", help="Add user to blacklist")
    @is_team()
    async def add(self, ctx, user: discord.User, *, reason):
        if len(reason) >= 150:
            return await ctx.send("`reason` argument must be less than 150 chars.")

        await self.bot.db.execute(
            "INSERT INTO blacklist (user_id, reason) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET reason = $2",
            user.id, reason)
        self.bot.bl[user.id] = reason
        return await ctx.send(
            f"<:4430checkmark:848857812632076314> **`{user.name}#{user.discriminator}`** has been blacklisted for : {reason}")

    @blacklist.command(name="remove", help="remove user to blacklist")
    @is_team()
    async def remove(self, ctx, user: discord.User):
        db = await self.bot.db.fetch("SELECT * FROM blacklist WHERE user_id = $1", user.id)
        if not db:
            return await ctx.send("<:4318crossmark:848857812565229601> This dude is not blacklisted.")

        if user.id not in self.bot.bl:
            return await ctx.send("<:4318crossmark:848857812565229601> This dude is not blacklisted.")

        await self.bot.db.execute("DELETE FROM blacklist WHERE user_id = $1", user.id)
        del self.bot.bl[user.id]
        return await ctx.send(
            f"<:4430checkmark:848857812632076314> **`{user.name}#{user.discriminator}`** has been unblacklisted poggies.")


def setup(bot):
    bot.add_cog(BlackList(bot))

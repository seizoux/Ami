import asyncio
import datetime

import discord
from discord.ext import commands


class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Support Loaded")

    @commands.command(help="Send a support request to the ami mods")
    async def support(self, ctx):
        user_id = str(f"{ctx.author.id}")
        db = await self.bot.pg_con.fetchrow("SELECT * FROM blacklist WHERE user_id = $1", user_id)
        if db:
            try:
                reason = db["reason"]
                em = discord.Embed(
                    description=f"**{ctx.author.name}**, you're blacklisted from the bot. You can't use `ami feature & ami support`. If you think this is a mistake, feel free to reach the support team.\nReason: **`{reason}`**",
                    color=0xffcff1)
                em.set_footer(text="https://discord.gg/ZcErEwmVYu")
                return await ctx.author.send(embed=em)
            except Exception:
                em = discord.Embed(
                    description=f"**{ctx.author.name}**, you're blacklisted from the bot. You can't use `ami feature & ami support`. If you think this is a mistake, feel free to reach the support team.\nReason: **`{reason}`**",
                    color=0xffcff1)
                em.set_footer(text="https://discord.gg/ZcErEwmVYu")
                return await ctx.send(embed=em)

        channel = self.bot.get_channel(810625559868342353)
        msg1 = "ami nvm"
        ms = await ctx.send(
            "<:qmark:819702268479012974> Ok! Now send the message u want to send at the support, you have `1 minute`. Use **ami nvm** if u don't need support.")

        try:
            msg = await self.bot.wait_for('message', check=lambda
                message: message.author == ctx.author and message.channel == ctx.channel, timeout=60.0)

        except asyncio.TimeoutError:
            await ctx.send("<:timealert:819702268457648148> Times Up!")
            return

        if msg.content == msg1:
            await ctx.send("<:vea:819703490703523860> Alright! Support request deleted.")
            await ms.delete()
            return

        if msg:
            await ms.delete()
            await ctx.send("<:check:819702267476967444> Perfect! The message has been forwarded to the bot support.")
            await channel.send(
                f"<:info:819702267480899634> **Yo! Someone asked for support, see info next**\n<:message:819702268269297665> The message is : {msg.content}\n<:author:819702267698610176> The author is : {ctx.author.name}#{ctx.author.discriminator}\n<a:dogekek:819739315125878822> Report sended at : {datetime.datetime.utcnow()}")


def setup(bot):
    bot.add_cog(Support(bot))

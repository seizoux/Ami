import asyncio
import datetime

import discord
from discord.ext import commands


class Features(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Features Loaded")

    @commands.command(help="Suggest new feature for ami")
    async def feature(self, ctx):
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

        channel = self.bot.get_channel(805892487503413310)
        msg1 = "ami nvm"
        msg2 = "ami feature"
        await ctx.send(
            "<:qmark:819702268479012974> Ok! Now send the feature u want to be added in Ami: you have `1 minute`. Use **ami nvm** to cancel the request.")

        try:
            msg = await self.bot.wait_for('message', check=lambda
                message: message.author == ctx.author and message.channel == ctx.channel, timeout=60.0)

        except asyncio.TimeoutError:
            await ctx.send("<:allert:819708576796114994> Times Up!")
            return

        if msg.content == msg1:
            try:
                await ctx.send("<:vea:819703490703523860> Alright! Feature request deleted.")
                await ctx.message.delete()
                return
            except Exception:
                return

        if msg.content == msg2:
            await ctx.send(
                "<:vea:819703490703523860> What are u trying to do? You can't send `ami feature` with `ami feature`, try again.")
            await ctx.message.delete()
            return

        if msg:
            await ctx.send(
                "<:check:819702267476967444> Perfect! The feature has been forwarded to #features in the support server.")
            fmt = '%d/%m/%Y - %H:%m'
            time = datetime.datetime.utcnow()
            t3 = (time.strftime(fmt))
            em = discord.Embed(title="New feature requested!", color=0xffcff1)
            em.add_field(name="Requested by", value=f"{ctx.author.name}#{ctx.author.discriminator}")
            em.add_field(name="Date", value=f"{t3}")
            em.add_field(name="Feature Message", value=f"{msg.content}", inline=False)
            em.set_footer(text=f"ID : {ctx.author.id}")
            react = await channel.send(embed=em)
            await react.add_reaction("<a:4214_yes_tick:819689871156445245>")
            await react.add_reaction("<a:no:819689870284816415>")


def setup(bot):
    bot.add_cog(Features(bot))

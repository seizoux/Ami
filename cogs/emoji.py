from PIL import Image
import requests
import discord
from discord.ext import commands
from io import BytesIO
import os
from dotenv import load_dotenv


load_dotenv()



class Emoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Emoji Loaded")


    @commands.command(help="Create new emoji with image links")
    async def emoji(self, ctx, object, *, name):
        guild = ctx.guild
        if ctx.author.guild_permissions.manage_emojis:
            r = requests.get(object)
            img = Image.open(BytesIO(r.content), mode='r')
            try:
                img.seek(1)

            except EOFError:
                is_animated = False

            else:
                is_animated = True

            if is_animated == True:
                await ctx.send(":x: Animated emoji **not** supported")

            elif is_animated == False:
                b = BytesIO()
                img.save(b, format='PNG')
                b_value = b.getvalue()
                emoji = await guild.create_custom_emoji(image=b_value, name=name)
                em = discord.Embed(title=f":white_check_mark: New emoji created!", description=f"This is the emoji ⇉ <:{name}:{emoji.id}>\n```Python\nHere it is the code ⇉ <:{name}:{emoji.id}>\n```", color = 0xffcff1)
                em.set_footer(text=f"Emoji created by {ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Emoji(bot))
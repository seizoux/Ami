from io import BytesIO

import discord
import requests
from PIL import Image
from discord.ext import commands
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
        if ctx.author.guild_permissions.manage_emojis:
            guild = ctx.guild
            r = requests.get(object)
            img = Image.open(BytesIO(r.content), mode='r')
            try:
                img.seek(1)

            except EOFError:
                is_animated = False

            else:
                is_animated = True

            if not is_animated:
                b = BytesIO()
                img.save(b, format='PNG')
                b_value = b.getvalue()
                emoji = await guild.create_custom_emoji(image=b_value, name=name)
                em = discord.Embed(title=f":white_check_mark: New emoji created!",
                                   description=f"This is the emoji ⇉ <:{name}:{emoji.id}>\n```Python\nHere it is the code ⇉ <:{name}:{emoji.id}>\n```",
                                   color=0xffcff1)
                em.set_footer(text=f"Emoji created by {ctx.author.name}", icon_url=f"{ctx.author.avatar_url}")
                await ctx.send(embed=em)
            else:
                await ctx.send(":x: Animated emoji **not** supported")


def setup(bot):
    bot.add_cog(Emoji(bot))

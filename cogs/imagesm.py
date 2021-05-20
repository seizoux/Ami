import alexflipnote
import asyncio
import discord
from discord.ext import commands
import vacefron
from asyncdagpi import Client, ImageFeatures
import typing
import aiohttp
from polaroid import Image as imdagpi
import cv2 as cv
from urllib.request import Request, urlopen
import numpy as np
from io import BytesIO
from PIL import Image ,ImageDraw


dagpi = Client("token")
vac_api = vacefron.Client()
alex_api = alexflipnote.Client("token")

def round_func(pfp: discord.Member):
    with Image.open(pfp).convert("RGBA") as pfp_1:
        im = pfp_1.resize((370,370))
        bgs = Image.new("RGBA", (0,0), 0)
        bg = bgs.resize(im.size, Image.ANTIALIAS)
        bigsize = (im.size[0] * 3, im.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(im.size, Image.ANTIALIAS)
        im.putalpha(mask)
        bg.paste(im,(0,0),im)
        im.close()

    buffer = BytesIO()
    bg.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


class Imagesm(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.category = "Image(s)"

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Image(s) Loaded")

    @commands.command(help="Have an image you want to round (circle)? This command is for you. (Works only with member avatars).")
    async def round(self, ctx, member: typing.Optional[typing.Union[discord.Member, str]]):
        if member == None:
            member = ctx.author
        else:
            member = member

        try:
            asset1 = member.avatar_url_as(size=512)
            pfp= BytesIO(await asset1.read())
        except Exception:
            return await ctx.reply("<:redTick:596576672149667840> Unable to round, remember it works only with avatars, so if you want to round an external image, set that as your avatar.")

        buffer = await self.bot.loop.run_in_executor(None, round_func, pfp)
        file=discord.File(fp=buffer, filename="round.png")

        await ctx.send(f"<:greenTick:596576670815879169> Image rounded in `{round(self.bot.latency*1000, 2)}ms`!", file=file)

            

    @commands.command(help="Get an achievement", aliases = ["ach"])
    async def achievment(self, ctx, *,text: str, icon = None):
        image = await alex_api.achievement(text=text, icon=icon)
        embed = discord.Embed(color=0xffcff1).set_image(url="attachment://achievement.png")
        image = discord.File(await (await alex_api.achievement(text=text)).read(), "achievement.png")
        await ctx.send(embed=embed, file=image)


    @commands.command(help="Make a text in supreme font/style", aliases = ["sup"])
    async def supreme(self, ctx, *,text, dark=False, light=False):
        image = await alex_api.supreme(text, dark, light)
        embed = discord.Embed(color=0xffcff1).set_image(url="attachment://supreme.png")
        image = discord.File(await (await alex_api.supreme(text=text)).read(), "supreme.png")
        await ctx.send(embed=embed, file=image)

    @commands.command(help="Generate an '.. is not the impostor' or '... is the impostor' meme", aliases = ["amg"])
    async def amongus(self, ctx, color, false_or_true, *, text):
        if len(text) > 14:
            return await ctx.send("The text can't be over 14 characters.")
        s = ["True", "true", "False", "false"]
        if false_or_true in s:
            if false_or_true == "true":
                false_or_true = True
            elif false_or_true == "True":
                false_or_true = True
            else:
                if false_or_true == "false":
                    false_or_true = False
                if false_or_true == "False":
                    false_or_true = False
        else:
            return await ctx.reply("Only `False` & `True` are allowed in `<false_or_true>` argument.")

        colors = ["red", "blue", "black", "white", "pink", "purple", "brown", "green", "cyan", "yellow", "orange"]
        if color not in colors:
            d = ", ".join(colors)
            return await ctx.reply(f"This color isn't supported, available colors are:\n{d}", mention_author=False)

        image = await vac_api.ejected(text, color, false_or_true)
        image_out = discord.File(fp = await image.read(), filename = "ejected.png")
        await ctx.send(file = image_out)

    @commands.command(help="Get a little bit wide an avatar of a member")
    async def wide(self, ctx, user: discord.Member = None):
        if user == None:
            user = ctx.author

        image = await vac_api.wide(user.avatar_url)
        filen = ""
        if user.is_avatar_animated:
            filen = "wide.gif"
        if not user.is_avatar_animated:
            filen = "wide.png"
        image_out = discord.File(fp = await image.read(), filename = filen)
        await ctx.send(file = image_out)


    @commands.command(help="Generate a stonks/not stonks meme image", aliases = ["stk"])
    async def stonks(self, ctx, user: discord.Member = None, not_stonks = None):
        if user == None:
            user = ctx.author
        
        if not_stonks == None:
            not_stonks = False

        if not_stonks == "true":
            not_stonks = False

        if not_stonks == "false":
            not_stonks = True

        image = await vac_api.stonks(user.avatar_url, not_stonks)
        image_out = discord.File(fp = await image.read(), filename = "stonks.png")
        await ctx.send(file = image_out)



    @commands.command(help="Apply the pixel effect on a member avatar", aliases = ["px"])
    async def pixel(self, ctx, member: typing.Optional[typing.Union[discord.Member, str]]):
        if member == None:
            url = str(ctx.author.avatar_url_as(format="png"))
        elif isinstance(member, discord.Member) or isinstance(member, discord.User):
            url = str(member.avatar_url_as(format="png"))
        else:
            if member.startswith("https"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            if member.startswith("http"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            else:
                return await ctx.send("Image not found.")

        img = await dagpi.image_process(ImageFeatures.pixel(), url)
        file = discord.File(fp=img.image,filename=f"pixel.{img.format}")
        embed = discord.Embed(color=0xffcff1).set_image(url=f"attachment://pixel.{img.format}")
        return await ctx.send(embed=embed, file=file)


    @commands.command(help="Apply the polaroid effect on a member avatar", aliases = ["pl"])
    async def polaroid(self, ctx, member: typing.Optional[typing.Union[discord.Member, str]]):
        if member == None:
            url = str(ctx.author.avatar_url_as(format="png"))
        elif isinstance(member, discord.Member) or isinstance(member, discord.User):
            url = str(member.avatar_url_as(format="png"))
        else:
            if member.startswith("https"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            if member.startswith("http"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            else:
                return await ctx.send("Image not found.")

        img = await dagpi.image_process(ImageFeatures.polaroid(), url)
        file = discord.File(fp=img.image,filename=f"polaroid.{img.format}")
        embed = discord.Embed(color=0xffcff1).set_image(url=f"attachment://polaroid.{img.format}")
        return await ctx.send(embed=embed, file=file)


    @commands.command(help="Apply the ascii effect on a member avatar", aliases = ["asc"])
    async def ascii(self, ctx, member: typing.Optional[typing.Union[discord.Member, str]]):
        if member == None:
            url = str(ctx.author.avatar_url_as(format="png"))
        elif isinstance(member, discord.Member) or isinstance(member, discord.User):
            url = str(member.avatar_url_as(format="png"))
        else:
            if member.startswith("https"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            if member.startswith("http"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            else:
                return await ctx.send("Image not found.")

        img = await dagpi.image_process(ImageFeatures.ascii(), url)
        file = discord.File(fp=img.image,filename=f"ascii.{img.format}")
        embed = discord.Embed(color=0xffcff1).set_image(url=f"attachment://ascii.{img.format}")
        return await ctx.send(embed=embed, file=file)


    @commands.command(help="Apply the angel effect on a member avatar", aliases = ["agl"])
    async def angel(self, ctx, member: typing.Optional[typing.Union[discord.Member, str]]):
        if member == None:
            url = str(ctx.author.avatar_url_as(format="png"))
        elif isinstance(member, discord.Member) or isinstance(member, discord.User):
            url = str(member.avatar_url_as(format="png"))
        else:
            if member.startswith("https"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            if member.startswith("http"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            else:
                return await ctx.send("Image not found.")

        img = await dagpi.image_process(ImageFeatures.angel(), url)
        file = discord.File(fp=img.image,filename=f"angel.{img.format}")
        embed = discord.Embed(color=0xffcff1).set_image(url=f"attachment://angel.{img.format}")
        return await ctx.send(embed=embed, file=file)

    @commands.command(help="Apply the paint effect on a member avatar", aliases = ["pnt"])
    async def paint(self, ctx, member: typing.Optional[typing.Union[discord.Member, str]]):
        if member == None:
            url = str(ctx.author.avatar_url_as(format="png"))
        elif isinstance(member, discord.Member) or isinstance(member, discord.User):
            url = str(member.avatar_url_as(format="png"))
        else:
            if member.startswith("https"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            if member.startswith("http"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            else:
                return await ctx.send("Image not found.")

        img = await dagpi.image_process(ImageFeatures.paint(), url)
        file = discord.File(fp=img.image,filename=f"paint.{img.format}")
        embed = discord.Embed(color=0xffcff1).set_image(url=f"attachment://paint.{img.format}")
        return await ctx.send(embed=embed, file=file)


    @commands.command(help="See the hexa colors of a member avatar or an url image", aliases = ["clr"])
    async def colors(self, ctx, member: typing.Optional[typing.Union[discord.Member, str]]):
        if member == None:
            url = str(ctx.author.avatar_url_as(format="png"))
        elif isinstance(member, discord.Member) or isinstance(member, discord.User):
            url = str(member.avatar_url_as(format="png"))
        else:
            if member.startswith("https"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            if member.startswith("http"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            else:
                return await ctx.send("Image not found.")

        img = await dagpi.image_process(ImageFeatures.colors(), url)
        file = discord.File(fp=img.image,filename=f"colors.{img.format}")
        embed = discord.Embed(color=0xffcff1).set_image(url=f"attachment://colors.{img.format}")
        return await ctx.send(embed=embed, file=file)


    @commands.command(help="Apply the triangle effect on a member avatar", aliases = ["trl"])
    async def triangle(self, ctx, member: typing.Optional[typing.Union[discord.Member, str]]):
        if member == None:
            url = str(ctx.author.avatar_url_as(format="png"))
        elif isinstance(member, discord.Member) or isinstance(member, discord.User):
            url = str(member.avatar_url_as(format="png"))
        else:
            if member.startswith("https"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            if member.startswith("http"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            else:
                return await ctx.send("Image not found.")

        img = await dagpi.image_process(ImageFeatures.triangle(), url)
        file = discord.File(fp=img.image,filename=f"triangle.{img.format}")
        embed = discord.Embed(color=0xffcff1).set_image(url=f"attachment://triangle.{img.format}")
        return await ctx.send(embed=embed, file=file)


    @commands.command(help="Apply the satan effect on a member avatar", aliases = ["st"])
    async def satan(self, ctx, member: typing.Optional[typing.Union[discord.Member, str]]):
        if member == None:
            url = str(ctx.author.avatar_url_as(format="png"))
        elif isinstance(member, discord.Member) or isinstance(member, discord.User):
            url = str(member.avatar_url_as(format="png"))
        else:
            if member.startswith("https"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            if member.startswith("http"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            else:
                return await ctx.send("Image not found.")

        img = await dagpi.image_process(ImageFeatures.satan(), url)
        file = discord.File(fp=img.image,filename=f"satan.{img.format}")
        embed = discord.Embed(color=0xffcff1).set_image(url=f"attachment://satan.{img.format}")
        return await ctx.send(embed=embed, file=file)


    @commands.command(help="Apply the wasted effect on a member avatar", aliases = ["wst"])
    async def wasted(self, ctx, member: typing.Optional[typing.Union[discord.Member, str]]):
        if member == None:
            url = str(ctx.author.avatar_url_as(format="png"))
        elif isinstance(member, discord.Member) or isinstance(member, discord.User):
            url = str(member.avatar_url_as(format="png"))
        else:
            if member.startswith("https"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            if member.startswith("http"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            else:
                return await ctx.send("Image not found.")

        img = await dagpi.image_process(ImageFeatures.wasted(), url)
        file = discord.File(fp=img.image,filename=f"wasted.{img.format}")
        embed = discord.Embed(color=0xffcff1).set_image(url=f"attachment://wasted.{img.format}")
        return await ctx.send(embed=embed, file=file)


    @commands.command(help="Apply the jail effect on a member avatar", aliases = ["jl"])
    async def jail(self, ctx, member: typing.Optional[typing.Union[discord.Member, str]]):
        if member == None:
            url = str(ctx.author.avatar_url_as(format="png"))
        elif isinstance(member, discord.Member) or isinstance(member, discord.User):
            url = str(member.avatar_url_as(format="png"))
        else:
            if member.startswith("https"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            if member.startswith("http"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            else:
                return await ctx.send("Image not found.")

        img = await dagpi.image_process(ImageFeatures.jail(), url)
        file = discord.File(fp=img.image,filename=f"jail.{img.format}")
        embed = discord.Embed(color=0xffcff1).set_image(url=f"attachment://jail.{img.format}")
        return await ctx.send(embed=embed, file=file)


    @commands.command(help="Apply the charchoal effect on a member avatar", aliases = ["chc"])
    async def charchoal(self, ctx, member: typing.Optional[typing.Union[discord.Member, str]]):
        if member == None:
            url = str(ctx.author.avatar_url_as(format="png"))
        elif isinstance(member, discord.Member) or isinstance(member, discord.User):
            url = str(member.avatar_url_as(format="png"))
        else:
            if member.startswith("https"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            if member.startswith("http"):
                url = member
                url = member.replace("cdn.discordapp.com", "media.discordapp.net")
            else:
                return await ctx.send("Image not found.")

        img = await dagpi.image_process(ImageFeatures.charcoal(), url)
        file = discord.File(fp=img.image,filename=f"charcoal.{img.format}")
        embed = discord.Embed(color=0xffcff1).set_image(url=f"attachment://charcoal.{img.format}")
        return await ctx.send(embed=embed, file=file)


    @commands.command(help="Roast someone")
    async def roast(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author
        
        if member.id == self.bot.user.id:
            return await ctx.send("Nah, roast someone else.")

        roast = await dagpi.roast()
        await ctx.send(f"**{member.name}**, " + roast)

    @commands.command(help="Get the rainbow effect with a member avatar.", aliases = ["rnbw"])
    async def rainbow(self, ctx, member: typing.Optional[typing.Union[discord.Member, str]] = None):
        if member == None:
            member = ctx.author

        av = await member.avatar_url_as(format="png").read()
        im = imdagpi(av)
        im.apply_gradient()
        im.save("rnbw.png")
        file = discord.File("rnbw.png")
        em = discord.Embed(color = 0xffcff1)
        em.set_image(url="attachment://rnbw.png")
        await ctx.send(file=file, embed=em)
            



def setup(bot):
    bot.add_cog(Imagesm(bot))

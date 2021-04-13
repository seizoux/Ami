import asyncpraw
import random
from discord.ext import commands
import discord
import TenGiphPy
import scathach

tokens = {'bot': 'ODAxNzQyOTkxMTg1OTM2Mzg0.YAlHWA.HY0iZ42gMJcMx8VIJeUX2ePMaMc',
          'tenor': '6T8GAHP2LI7E',}

t = TenGiphPy.Tenor(token=tokens['tenor'])


class Reddita(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Reddita Loaded")


    @commands.command(help="See meme images")
    async def meme(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')


        subreddit = await reddit.subreddit("memes")
        post = await subreddit.random()
        em=discord.Embed(title=post.title, url=post.url, color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)



    @commands.command(help="See hentai images")
    @commands.is_nsfw()
    async def hentai(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')


        subreddit = await reddit.subreddit("hentai")
        post = await subreddit.random()
        em=discord.Embed(title=post.title, url=post.url, color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


    @commands.command(help="See anime images")
    async def anime(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')


        subreddit = await reddit.subreddit("Melanime")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


    @commands.command(help="See porn images")
    @commands.is_nsfw()
    async def porn(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')


        subreddit = await reddit.subreddit("nsfw")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


    @commands.command(help="See waifu images")
    @commands.is_nsfw()
    async def waifu(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

 
        subreddit = await reddit.subreddit("ElfWaifu")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


    @commands.command(help="See software meme images")
    async def sftw(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

        subreddit = await reddit.subreddit("softwaregore")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)

    @commands.command(help="See programming humor images")
    async def prgmh(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

        subreddit = await reddit.subreddit("ProgrammerHumor")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


    @commands.command(help="See bad discord bots images")
    async def bdb(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

        subreddit = await reddit.subreddit("BadDiscordBots")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


    @commands.command(help="See nezuko (demon slayer) images")
    async def nezuko(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

        subreddit = await reddit.subreddit("Nezuko")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


    @commands.command(help="See linux images")
    async def linux(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

        subreddit = await reddit.subreddit("unixporn")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


    @commands.command(help="See tenor hot gifs")
    @commands.is_nsfw()
    async def thot(self, ctx):
        m = ["twerk girl", "girl booty shaking", "girl ass twerk", "girl nude twerk", "girl ass shaking"]
        s = random.choice(m)
        url = t.random(str(s))
        em=discord.Embed(color=0xffcff1)
        em.set_image(url=url)
        await ctx.send(embed=em)
        

    @commands.command(help="See amateur images")
    @commands.is_nsfw()
    async def amateur(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

        subreddit = await reddit.subreddit("Amateur")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)
        

    @commands.command(help="See college images")
    @commands.is_nsfw()
    async def college(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

        subreddit = await reddit.subreddit("collegesluts")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)
        

    @commands.command(help="See pornhub fun comments images")
    @commands.is_nsfw()
    async def phcomm(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

        subreddit = await reddit.subreddit("PornhubComments")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


    @commands.command(help="See porn gifs")
    @commands.is_nsfw()
    async def porngif(self, ctx):
        link = scathach.gif()
        em=discord.Embed(color=0xffcff1)
        em.set_image(url=link)
        await ctx.send(embed=em)


    @commands.command(help="See cute images")
    async def cpics(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

        subreddit = await reddit.subreddit("aww")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


    @commands.command(help="See facepalm images")
    async def fpalm(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

        subreddit = await reddit.subreddit("Facepalm")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


    @commands.command(help="See weird design images")
    async def cdesign(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

        subreddit = await reddit.subreddit("CrappyDesign")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


    @commands.command(help="See 'WTF' images")
    async def justwtf(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

        subreddit = await reddit.subreddit("hmmm")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


    @commands.command(help="See photoshop images")
    async def pshop(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

        subreddit = await reddit.subreddit("PhotoshopBattles")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


    @commands.command(help="See mizuhara images")
    async def mizuhara(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

        subreddit = await reddit.subreddit("ChizuruMizuhara")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


    @commands.command(help="See catgirls images")
    @commands.is_nsfw()
    async def neko(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

        subreddit = await reddit.subreddit("Nekomimi")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


    @commands.command(help="See yuri's (girl x girl) images")
    @commands.is_nsfw()
    async def yuri(self, ctx):
        reddit = asyncpraw.Reddit(client_id='4gaG7w5rEn-xsQ',
                        client_secret='D6FaeCzwJpzrHj_GwOx0e9TI5kLyhQ',
                        user_agent='AmiPraw')

        subreddit = await reddit.subreddit("yuri")
        post = await subreddit.random()
        em=discord.Embed(title=post.title,url=post.url,  color=0xffcff1)
        em.set_image(url=post.url)
        em.set_footer(text=f"Posted by {post.author} - {post.score} votes.")
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Reddita(bot))
    

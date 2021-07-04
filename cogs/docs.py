import discord, aiohttp
from discord.ext import commands
import random
from doc_search import AsyncScraper


class RTFM(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.session = aiohttp.ClientSession()
  
  async def rtfm_lookup(self, program = None, *, args = None):
    
    self.scraper = AsyncScraper(session = self.session)
    rtfm_dictionary = dict(await self.bot.db.fetch("SELECT * FROM rtfmstuff"))

    if not args:
      return rtfm_dictionary.get(program)

    else:
      url = rtfm_dictionary.get(program)

      results = await self.scraper.search(args, page=url)

      if not results:
        return f"<:4318crossmark:848857812565229601> Could not find anything with `{args}`."

      else:
        return results

  async def rtfm_send(self, ctx, results):

    if isinstance(results, str):
      await ctx.send(results, allowed_mentions = discord.AllowedMentions.none())

    else: 
      embed = discord.Embed(color=0xffcff1)

      results = results[:10]
      embed.description = "\n".join(f"[`{result}`]({value})" for result, value in results)

      reference = ctx.message.reference
      await ctx.send(embed=embed, reference = reference)


  @commands.group(help="Search the documentation for the given query.\nThis can search trought different libraries, like `wavelink`, `dagpi`, `asyncpg`, `python` and `discord.py` as latest / master.\nExample : `ami rtfm Bot` will search `Bot` trought all libraries supported.",aliases=["rtd", "rtfs"], invoke_without_command = True)
  async def rtfm(self, ctx, *, query = None):

    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="latest", args = query)
    await self.rtfm_send(ctx, results)

  @rtfm.command()
  async def wavelink(self, ctx, *, query = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="wavelink", args = query)
    await self.rtfm_send(ctx, results)

  @rtfm.command()
  async def master(self, ctx, *, query = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="master", args = query)
    await self.rtfm_send(ctx, results)

  @rtfm.command()
  async def dagpi(self, ctx, *, query = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="dagpi", args = query)
    await self.rtfm_send(ctx, results)

  @rtfm.command()
  async def asyncpg(self, ctx, *, query = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="asyncpg", args = query)
    await self.rtfm_send(ctx, results)

  @rtfm.command(aliases=['py'])
  async def python(self, ctx, *, query = None):
    await ctx.trigger_typing()
    results = await self.rtfm_lookup(program="python", args = query)
    await self.rtfm_send(ctx, results)

def setup(bot):
  bot.add_cog(RTFM(bot))

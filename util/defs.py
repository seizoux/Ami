import datetime
import pathlib

import discord
from discord.ext import commands

COOL_PEOPLE = []


def premium(override=False):
    async def predicate(ctx):

        if override and ctx.author.id in [
            144126010642792449,
            410452466631442443,
            711057339360477184,
            590323594744168494,
            691406006277898302,
            343019667511574528,
        ]:
            return True

        if not ctx.author.id in COOL_PEOPLE:
            is_premium = await ctx.bot.db.fetch("SELECT * FROM premium WHERE user_id = $1", ctx.author.id)
            if not is_premium:
                await ctx.send(
                    embed=discord.Embed(
                        description="This is a [premium only](https://amibot.gg/premium) feature and you're not a premium user.",
                        color=ctx.bot.color,
                        timestamp=datetime.datetime.utcnow(),
                    ).set_author(
                        name=f"{ctx.author.name}",
                        icon_url=ctx.author.avatar_url,
                    )
                )
                return False
            else:
                COOL_PEOPLE.append(ctx.author.id)
                return True
        else:
            return True

    return commands.check(predicate)


def is_team():
    def predicate(ctx):
        team = [144126010642792449, 410452466631442443, 711057339360477184, 590323594744168494, 691406006277898302,
                343019667511574528]
        return ctx.author.id in team

    return commands.check(predicate)


def make_list_embed(fields):
    embed = discord.Embed(description="\u200b")
    for key, value in fields.items():
        embed.add_field(name=key, value=value, inline=True)
    return embed


def line_count():
    p = pathlib.Path('./')
    cm = cr = fn = cl = ls = fc = 0
    for f in p.rglob('*.py'):
        if str(f).startswith("venv"):
            continue
        fc += 1
        with f.open() as of:
            for l in of.readlines():
                l = l.strip()
                if l.startswith('class'):
                    cl += 1
                if l.startswith('def'):
                    fn += 1
                if l.startswith('async def'):
                    cr += 1
                if '#' in l:
                    cm += 1
                ls += 1
    return f"Files: {fc}\nLines: {ls:,}\nFunctions: {fn}\nComments: {cm:,}"


def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def setup(bot):
    print("[INFO]: Definition SETUP")


def teardown(bot):
    print("[INFO]: Definition TEARDOWN")

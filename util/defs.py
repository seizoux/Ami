from discord.ext import commands
import discord
import pathlib

def is_team():
    def predicate(ctx):
      team = [144126010642792449, 410452466631442443, 711057339360477184, 590323594744168494, 691406006277898302, 343019667511574528]
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

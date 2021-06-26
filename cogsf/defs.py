from discord.ext import commands

def is_team():
    def predicate(ctx):
      team = [144126010642792449, 410452466631442443, 711057339360477184, 590323594744168494, 691406006277898302, 343019667511574528]
      return ctx.author.id in team
    return commands.check(predicate)

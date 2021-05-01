import discord
from discord.ext import commands
import datetime
import re


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Moderation Loaded")

    @commands.command()
    @commands.is_owner()
    async def dugongo(self, ctx):
        toleave = self.bot.get_guild(802339719152271361)
        await toleave.leave()
        print("Left Server")


    @commands.command(help="Set the slowmode of the channel where you send this command")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, time):
        valid_times = ["remove", "5s", "10s", "15s", "30s", "1m", "2m", "5m", "10m", "15m", "30m", "1h", "2h", "6h"]
        if time not in valid_times:
            return await ctx.reply(f"This slowmode time can't be set, `ami slowmode remove` to remove the slowmode, else the available slowmodes are:\n`5s`, `10s`, `15s`, `30s`, `1m`, `2m`, `5m`, `10m`, `15m`, `30m`, `1h`, `2h`, `6h`")
        
        slow = 0
        if time in valid_times:
            if time == "remove":
                slow = 0
                await ctx.channel.edit(slowmode_delay=slow)
                await ctx.send(f"<:slowmode:585790802979061760> Channel slowmode **removed!**")
                return
            if time == "5s":
                slow = 5
            elif time == "10s":
                slow = 10
            elif time == "15s":
                slow = 15
            elif time == "30s":
                slow = 30
            elif time == "1m":
                slow = 60
            elif time == "2m":
                slow = 120
            elif time == "5m":
                slow = 300
            elif time == "10m":
                slow = 600
            elif time == "15m":
                slow = 900
            elif time == "30m":
                slow = 1800
            elif time == "1h":
                slow = 3600
            elif time == "2h":
                slow = 7200
            elif time == "6h":
                slow = 21600

        await ctx.channel.edit(slowmode_delay=slow)
        await ctx.send(f"<:slowmode:585790802979061760> Channel slowmode set to **{time}!**")

# Clear Command
    @commands.command(help="Delete X messages")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount)
        

# Ban Command
    @commands.command(help="Ban a member from the guild")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f":no_entry_sign: Banned.")
        return

# Unban Command
    @commands.command(help="Unban a member from the guild (name#0000)")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_disc = member.split('#')

        for banned_entry in banned_users:
            user = banned_entry.user

            if (user.name, user.discriminator) == (member_name, member_disc):
                await ctx.guild.unban(user)
                await ctx.repy(":free: Unbanned.")
                return

# Kick Command
    @commands.command(help="Kick a member from the guild")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f":raised_back_of_hand: **Kicked** {member.mention}")
        return

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member):
        guild = ctx.guild
        muted_role = discord.utils.get(guild.roles, name="Muted")

        if not muted_role:
            muted_role = await guild.create_role(name="Muted")

        await member.edit(send_messages = False, read_messages=False)
        await member.add_roles(muted_role)
        await ctx.reply("Successfully Muted.", mention_author=False)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member):
        mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
        if mutedRole in member.roles:
            await member.remove_roles(mutedRole)
        else:
            return await ctx.reply("This member isn't muted.", mention_author = False)
        await member.edit(send_messages = True, read_messages=True)
        await ctx.reply("Successfully unmuted.", mention_author = False)
    

    @commands.command(help="Enable or disable the antispam in the guild! \"toogle\" must be 'on' or 'off'")
    @commands.has_permissions(manage_messages=True)
    async def antispam(self, ctx, toggle):
        guild_id = str(ctx.guild.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM antispam WHERE guild_id = $1", guild_id)

        if not data:
            s = "off"
            await self.bot.pg_con.execute("INSERT INTO antispam (guild_id, toggle) VALUES ($1, $2)", guild_id, s)
            return await ctx.send("This guild was not found in the database, so i've automatically added it, now you can set the antispam!")

        toggles = ["On", "on", "Off", "off"]
        if toggle not in toggles:
            return await ctx.send("Only `on` or `off` are accepted.")

        tg = data["toggle"]
        if toggle == tg:
            return await ctx.send(f"The antispam for this guild is already on `{toggle}`.")

        await self.bot.pg_con.execute("UPDATE antispam SET toggle = $1 WHERE guild_id = $2", toggle, guild_id)
        if toggle == "on":
            return await ctx.send(f"Antispam was succesfully set on **`{toggle}`**, from now all links sent will be deleted.")
        elif toggle == "off":
            return await ctx.send(f"Antispam was succesfully set on **`{toggle}`**, now no messages will be deleted.")

    @commands.command(help="Enable or disable the anti in the guild! \"toogle\" must be 'on' or 'off'")
    @commands.has_permissions(manage_messages=True)
    async def antispam(self, ctx, toggle):
        guild_id = str(ctx.message.channel.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM antiabuse WHERE channel_id = $1", guild_id)

        if not data:
            s = "off"
            await self.bot.pg_con.execute("INSERT INTO antiabuse (channel_id, toggle) VALUES ($1, $2)", guild_id, s)
            return await ctx.send("This channel was not found in the database, so i've automatically added it, now you can set the antiabuse!")

        toggles = ["On", "on", "Off", "off"]
        if toggle not in toggles:
            return await ctx.send("Only `on` or `off` are accepted.")

        tg = data["toggle"]
        if toggle == tg:
            return await ctx.send(f"The antispam for this guild is already on `{toggle}`.")

        await self.bot.pg_con.execute("UPDATE antiabuse SET toggle = $1 WHERE channel_id = $2", toggle, guild_id)
        if toggle == "on":
            return await ctx.send(f"Antiabuse was succesfully set on **`{toggle}`**, from now all messages containing vulgar language will be deleted.")
        elif toggle == "off":
            return await ctx.send(f"Antiabuse was succesfully set off **`{toggle}`**, now no messages will be deleted.")        
        
    @commands.Cog.listener()
    async def on_message(self, message):
        curse_words = ['fuck', 'bitch', 'nigga', 'dick', 'pussy', 'whore', 'twat', 'fucking', 'anal', 'anus', 'arse', 'ass',
               'ballsack', 'balls', 'bastard', 'bitch', 'biatch', 'bloody', 'blowjob', 'blow job', 'bollock', 'bollok',
               'boner', 'boob', 'bugger', 'bum', 'butt', 'buttplug', 'clitoris', 'cock', 'coon', 'crap', 'cunt', 'dick',
               'dildo', 'dyke', 'fag', 'feck', 'fellate', 'fellatio', 'felching', 'fuck', 'f u c k', 'fudgepacker',
               'fudge packer', 'flange', 'homo', 'jerk', 'jizz', 'knobend', 'knob end', 'labia', 'muff', 'nigger',
               'nigga', 'penis', 'piss', 'poop', 'prick', 'pube', 'pussy', 'queer', 'scrotum', 'sex', 'shit', 's hit',
               'sh1t', 'slut', 'smegma', 'spunk', 'tit', 'tosser', 'turd', 'twat', 'vagina', 'wank', 'whore']
        if message.guild == None:
            return
        guild_id = str(message.guild.id)
        channel_id = str(message.channel.id)
        data = await self.bot.pg_con.fetchrow("SELECT * FROM antispam WHERE guild_id = $1", guild_id)
        antiabuse_data = await self.bot.pg_con.fetchrow("SELECT * FROM antiabuse WHERE channel_id = $1", guild_id)
        if not data:
            return
        
        if not antiabuse_data:
            return
        
        antiabuse_data_toggle = antiabuse_data["toggle"]
        # Checking if toggle is on in certain channel
        if antiabuse_data_toggle == "on":
            if message.author == bot.user:
                return
            content_split = message.content.split()
            if any(bad_word in content_split for bad_word in curse_words):
                try:
                    await message.delete()
                    await message.channel.send(f'{message.author.mention} please do not swear')
                    return
                except Exception:
                    # Permission issues
                    pass
        
        elif antiabuse_data_toggle != "on":
            return
        
        tg = data["toggle"]
        if tg == "on":
            for channel in message.guild.channels:
                if message.content.startswith("https://cdn.discord") and not message.author.bot:
                    return

                if message.content.startswith("https://media.discord") and not message.author.bot:
                    return

                if message.content.startswith("https://canary.discord") and not message.author.bot:
                    return 

                if message.content.startswith("https://") and not message.author.bot:
                    try:
                        await message.delete()
                        await message.channel.send(f"{message.author.mention}, you can't send links in this guild while the **antispam** is __on__.")
                    except Exception:
                        pass

                elif message.content.startswith("http://") and not message.author.bot:
                    try:
                        await message.delete()
                        await message.channel.send(f"{message.author.mention}, you can't send links in this guild while the **antispam** is __on__.")
                    except Exception:
                        pass
        elif tg != "on":
            return



def setup(bot):
    bot.add_cog(Moderation(bot))

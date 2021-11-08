import sys
import inspect
import humanize
from millify import millify
import discord

from discord.ext import commands, ipc
import psutil
from util.defs import get_size

class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, "ipc"):
            bot.ipc = ipc.Server(self.bot, secret_key="thisisverysuspisousandinvitebobobotthebestbot")
            bot.ipc.start()
        
        
        for n,f in inspect.getmembers(self):
            if n.startswith("get_"):
                bot.ipc.endpoints[n] = f.__call__

    @commands.Cog.listener()
    async def on_ipc_ready(self):
        """Called upon the IPC Server being ready"""
        print("Ipc is ready.")

    @commands.Cog.listener()
    async def on_ipc_error(self, endpoint, error):
        """Called upon an error being raised within an IPC route"""
        print(endpoint, "raised", error, file=sys.stderr)
    
    async def get_bot_contributors(self, data) -> dict:
        users = {
            144126010642792449: {'banner': 'https://cdn.discordapp.com/banners/144126010642792449/a_18bf6c08bb6f0a875c3dcc2d3b9be544.gif?size=512', 'status': "Experienced in sleeping.", "position": "Lead Developer, CEO", "socials": 
                                {'twitter': 'https://twitter.com/Daishiky_',
                                'github': 'https://github.com/Daishiky',
                                'discord': 'https://discord.com/users/144126010642792449',
                                'email': 'mailto:daishikyds@gmail.com'}},
            590323594744168494: {'banner': "https://cdn.discordapp.com/banners/590323594744168494/a_63d89ea798f13732126012e8bf0b0443.gif?size=512", 'status': "i is the best", "position": "API Developer", "socials": 
                                {'twitter': None,
                                'github': 'https://github.com/Cryptex-github',
                                'discord': 'https://discord.com/users/590323594744168494',
                                'email': None}},
            711057339360477184: {'banner': "https://cdn.discordapp.com/banners/711057339360477184/f0a3a22a519f14ed93a63ee651b85414.png?size=512", 'status': "I like gaming.", "position": "Hosting Provider", "socials": 
                                {'twitter': "https://twitter.com/jadon_ellis",
                                'github': 'https://github.com/WhoTheOOF',
                                'discord': 'https://discord.com/users/711057339360477184',
                                'email': None}},
            691406006277898302: {'banner': None, 'status': "I'm a cool dev. I also like mangoes", "position": "Website Builder", "socials": 
                                {'twitter': None,
                                'github': 'https://github.com/justanotherbyte',
                                'discord': 'https://discord.com/users/691406006277898302',
                                'email': None}},
            410452466631442443: {'banner': None, 'status': "A full stack dev figuring out life", "position": "Backend Support", "socials": 
                                {'twitter': None,
                                'github': 'https://github.com/Ali-TM-original',
                                'discord': 'https://discord.com/users/410452466631442443',
                                'email': None}},
            343019667511574528: {'banner': None, 'status': "I’m just a Student", "position": "Banners Designer", "socials": 
                                {'twitter': "https://twitter.com/Mrdriveappst",
                                'github': 'https://github.com/CnyAnime',
                                'discord': 'https://discord.com/users/343019667511574528',
                                'email': None}},
            797044260196319282: {'banner': None, 'status': "uh", "position": "Contributor", "socials": 
                                {'twitter': "https://twitter.com/veryjotte",
                                'github': 'https://github.com/jottew',
                                'discord': 'https://discord.com/users/797044260196319282',
                                'email': None}},
            171539705043615744: {'banner': None, 'status': "I intend to live forever. So far so good!", "position": "Contributor", "socials": 
                                {'twitter': None,
                                'github': None,
                                'discord': 'https://discord.com/users/171539705043615744',
                                'email': None}},
            414556245178056706: {'banner': None, 'status': ";", "position": "Contributor", "socials": 
                                {'twitter': None,
                                'github': "https://github.com/jay3332",
                                'discord': 'https://discord.com/users/414556245178056706',
                                'email': None}},
            591135329117798400: {'banner': "https://cdn.discordapp.com/banners/591135329117798400/a06f3d28a3df6f4be7a6cca49c56ed3c.png?size=512", 'status': "hi", "position": "Contributor", "socials": 
                                {'twitter': None,
                                'github': "https://github.com/InterStella0",
                                'discord': 'https://discord.com/users/591135329117798400',
                                'email': None}},
            412734157819609090: {'banner': None, 'status': "Bigger mass, bigger force of attraction", "position": "Contributor", "socials": 
                                {'twitter': None,
                                'github': None,
                                'discord': 'https://discord.com/users/412734157819609090',
                                'email': None}},
            624026977191329803: {'banner': None, 'status': "\"There are no Oogways.\" - Master Accident", "position": "Contributor", "socials": 
                                {'twitter': None,
                                'github': "https://github.com/JeyyGit",
                                'discord': 'https://discord.com/users/624026977191329803',
                                'email': None}},
        }

        final_users = {}

        for k,v in users.items():
            us = self.bot.get_user(k) or (await self.bot.fetch_user(k))
            if us:
                final_users[str(us)] = v

            final_users[str(us)]['avatar'] = f'{us.avatar_url}'

        return final_users

    async def get_bot_commands(self, data) -> dict:
        import traceback
        c = {}

        for cog in self.bot.cogs.values():
            if cog.__cog_name__ in ["Jishaku", "IpcRoutes", "Admin", "Chunk", "Handler", "TopGG", "Games", "RTFM", "Help", "Websocket"]:
                continue
            
            c[cog.__cog_name__] = []
            for cmd in cog.walk_commands():
                if "is_team" in str(cmd.checks):
                    continue
                perms = []
                for check in cmd.checks:
                    try:
                        check(0)
                    except Exception as e:
                        *frames, last_frame = traceback.walk_tb(e.__traceback__)
                        frame = last_frame[0]
                        try:
                            for perm in frame.f_locals['perms']:
                                perms.append(f'{str(perm).replace("_", " ").title()}')
                        except KeyError:
                            pass

                d = {
                    'name': f'ami {cmd.qualified_name} {cmd.signature}' if not 'premium' in str(cmd.checks) else f'⭐ ami {cmd.qualified_name} {cmd.signature}', 
                    'help': discord.utils.remove_markdown(str(cmd.help)),
                    'aliases': cmd.aliases, 
                    'checks': [str(check).split('.')[0] for check in cmd.checks],
                    'perms': perms
                    }
            
                c[cog.__cog_name__].append(d)

        return c

    async def get_leveling_data(self, data) -> int:
        guild = self.bot.get_guild(data.guild_id) or (await self.bot.fetch_guild(data.guild_id))
        if not guild:
            return 401

        levels = self.bot.get_cog("Leveling").levels_users
        xps = self.bot.get_cog("Leveling").xp_users

        if guild.id not in levels:
            return 401

        if guild.id not in xps:
            return 401

        m = guild.get_member(data.user_id)
        if not m:
            return 401

        if not m.guild_permissions.administrator:
            return 401

        del xps[guild.id]
        del levels[guild.id]
        await self.bot.db.execute("DELETE FROM levelling WHERE guild_id = $1", guild.id)
        return 200

    async def get_leveling_leaderboard(self, data) -> dict:

        try:
            guild = self.bot.get_guild(data.guild_id) or (await self.bot.fetch_guild(data.guild_id))
        except Exception:
            return 1
            
        if not guild:
            return 1

        levels = self.bot.get_cog("Leveling").levels_users
        xps = self.bot.get_cog("Leveling").xp_users

        if guild.id not in levels:
            return 1

        rev_levels = sorted(levels[guild.id].items(), key=lambda x: x[1]['level'], reverse=True)

        if int(data.user_id) == 0:
            admin_check = False
        else:
            try:
                admin_check = True if guild.get_member(int(data.user_id)).guild_permissions.administrator or int(guild.owner_id) == int(data.user_id) else False
            except Exception:
                admin_check = False

        final_dict = {}
        x = 1

        for k,v in rev_levels[:100]:
            user_data = self.bot.get_user(int(k)) or (
                await self.bot.fetch_user(int(k))
            )
            fullname = str(user_data)
            level = v['level']
            final_dict[fullname] = {'level': humanize.intcomma(level)}
            final_dict[fullname]['user_avatar'] = str(user_data.avatar_url)
            final_dict[fullname]['position'] = x

            if str(user_data.id) in xps[guild.id]:
                final_dict[fullname]['total_xp'] = millify(xps[guild.id][str(user_data.id)]['xp_earned'], precision=2)
            else:
                final_dict[fullname]['total_xp'] = "N/A"
            
            if x == 1:
                final_dict[fullname]['color'] = "yellow"
            elif x == 2:
                final_dict[fullname]['color'] = "gray"
            elif x == 3:
                final_dict[fullname]['color'] = "red"
            else:
                final_dict[fullname]['color'] = "white"
            
            x += 1

        return {"guild_id": guild.id, "guild_name": guild.name, "guild_icon": str(guild.icon_url), "users": final_dict, 'is_admin': admin_check}

    async def get_bot_stats(self, data) -> int:
        final_date = self.bot.launch_time.strftime("%d/%m/%Y %I:%M %p")

        shards = {i: {"guilds": 0, "users": 0} for i in range(len(self.bot.shards))}
        for guild in self.bot.guilds:
            shards[guild.shard_id]["guilds"] += 1
            shards[guild.shard_id]["users"] += guild.member_count

        color = ''

        for i in range(len(self.bot.shards)):
            for shard_id, shard in self.bot.shards.items():
                latency = round(shard.latency*1000,2)
                if int(latency) >= 100 and int(latency) <= 200:
                    color = 'green'
                    shards[shard_id]['type'] = "Operational"
                    shards[shard_id]['type_desc'] = "No issues on this shard, everything works as expected and responses comes as usual."
                elif int(latency) > 200 and int(latency) <= 400:
                    color = 'yellow'
                    shards[shard_id]['type'] = "Delayed Responses"
                    shards[shard_id]['type_desc'] = "Latency is over our standards, responses might be a bit delayed."
                elif int(latency) > 400:
                    color = 'red'
                    shards[shard_id]['type'] = "High Latency"
                    shards[shard_id]['type_desc'] = "Latency is too over our standards, responses are highly delayed."
                
                shards[shard_id]['latency'] = f"{latency}ms"
                shards[shard_id]['color'] = color

        m = psutil.Process().memory_full_info()
        ram_usage=get_size(m.rss)

        guilds = {}
        s = sorted(self.bot.guilds, key=lambda m: m.member_count, reverse=True)[:8]

        for tguild in s:
            if len(tguild.name) >= 14:
                nam = tguild.name[:14] + "..."
            else:
                nam = tguild.name

            if f"{tguild.icon_url}".startswith("https://"):
                guilds[nam] = {"icon": str(tguild.icon_url), "members": humanize.intcomma(tguild.member_count), "owner": str(tguild.owner)}
            else:
                guilds[nam] = {"icon": "https://img.icons8.com/color/452/discord-logo.png", "members": humanize.intcomma(tguild.member_count), "owner": str(tguild.owner)}

            if "VERIFIED" in tguild.features:
                guilds[nam]['badge'] = "https://emoji.gg/assets/emoji/2339-blurple-verified.png"
            elif "PARTNER" in tguild.features:
                guilds[nam]['badge'] = "https://static.wikia.nocookie.net/discord/images/3/31/Partner.png/revision/latest?cb=20210106185014"
            else:
                guilds[nam]['badge'] = 0

        graph_data = await self.bot.db.fetch("SELECT * FROM guilds ORDER BY date DESC LIMIT 7")

        graph = {}
        for i in graph_data:
            converted_date = i['date'].strftime('%m/%d/%Y')
            graph[converted_date] = {'guilds': i['guilds'], 'stat': i['stat'], 'users': i['users']}

        return {"guilds": len(self.bot.guilds), "users": sum([g.member_count for g in self.bot.guilds]), "players": len(self.bot.wavelink.players), "commands": humanize.intcomma(self.bot.command_counter), "uptime": final_date, "shards": shards, "usage": ram_usage, "topguilds": guilds, "graph_data": graph}

    async def get_guild_info(self, data) -> dict:
        if not isinstance(data.guild_id, int):
            return False

        c = {}

        guild = self.bot.get_guild(data.guild_id) or (await self.bot.fetch_guild(data.guild_id))
        user = self.bot.get_user(data.user_id) or (await self.bot.fetch_user(data.user_id))

        if not guild:
            return False

        if not guild.chunked:
            await guild.chunk()

        if user in guild.members and guild.get_member(user.id).guild_permissions.manage_guild or int(guild.owner_id) == int(user.id):
            c[int(guild.id)] = {"id": guild.id, "name": guild.name, "members": guild.member_count, "icon": f"{guild.icon_url}"}

            return c
        else:
            return False

    async def get_guild_name(self, data) -> str:
        guild = self.bot.get_guild(data.guild_id) or (await self.bot.fetch_guild(data.guild_id))

        if not guild:
            return None

        return {"name": str(guild.name), "icon": str(guild.icon_url) if guild.icon_url else "https://icon-library.com/images/discord-icon-colors/discord-icon-colors-10.jpg"}

    async def get_mutual_guilds(self, data) -> dict:

        user = self.bot.get_user(data.user_id) or (await self.bot.fetch_user(data.user_id))

        if not user:
            return False

        c = {}
        for g in self.bot.guilds:
            if user in g.members and g.get_member(user.id).guild_permissions.administrator or int(g.owner_id) == int(user.id):
                c[g.id] = {"banner": f"{g.banner_url}" if g.banner_url else f"{g.icon_url if g.icon_url else 'https://icon-library.com/images/discord-icon-colors/discord-icon-colors-10.jpg'}", "icon": f"{g.icon_url}" if f'{g.icon_url}' else "https://icon-library.com/images/discord-icon-colors/discord-icon-colors-10.jpg", "name": f"{g.name}", "border": "green" if self.bot.user in g.members else "red"}

        if len(c) >= 1:
            return c
        else:
            return 0

def setup(bot):
    bot.add_cog(IpcRoutes(bot))
import asyncio
import async_timeout
import copy
import datetime
import time
import discord
import math
import random
import re
import typing
import wavelink
from discord.ext import commands, menus
import humanize
import aiohttp
import sr_api
import aiofiles
from util.defs import is_team

srclient = sr_api.Client()

# URL matching REGEX...
URL_REG = re.compile(r"https?://(?:www\.)?.+")
SPOTIFY_URL_REG = re.compile(
    r"https?://open.spotify.com/(?P<type>album|playlist|track)/(?P<id>[a-zA-Z0-9]+)"
)


class NoChannelProvided(commands.CommandError):
    """Error raised when no suitable voice channel was supplied."""

    pass


class IncorrectChannelError(commands.CommandError):
    """Error raised when commands are issued outside of the players session channel."""

    pass


def premium(override=False):
    async def predicate(ctx):
        premium_users = await ctx.bot.db.fetch("SELECT * FROM premium")
        if ctx.author.id not in [dict(record)["user_id"] for record in premium_users]:
            if override and ctx.author.id in [
                144126010642792449,
                410452466631442443,
                711057339360477184,
                590323594744168494,
                691406006277898302,
                343019667511574528,
            ]:
                return True
            await ctx.send(
                embed=discord.Embed(
                    description="If you wish to use some neat features, hurry up and go buy Ami [premium!](https://amidiscord.xyz/premium)",
                    color=ctx.bot.color,
                    timestamp=datetime.datetime.utcnow(),
                ).set_author(
                    name=f"{ctx.author.name}, you are not Premium!",
                    icon_url=ctx.author.avatar_url,
                )
            )
            return False
        else:
            return True

    return commands.check(predicate)


class Track(wavelink.Track):
    __slots__ = ("requester",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.requester = kwargs.get("requester")


class Player(wavelink.Player):
    """Custom wavelink Player class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.context: commands.Context = kwargs.get("context", None)
        if self.context:
            self.dj: discord.Member = self.context.author

        self.queue = asyncio.Queue()
        self.controller = None
        self.looped = False
        self.looped_track = None

        self.waiting = False
        self.updating = False

        self.unlimit = False

        self.pause_votes = set()
        self.resume_votes = set()
        self.skip_votes = set()
        self.shuffle_votes = set()
        self.stop_votes = set()
        self.loop_votes = set()

        self.query = ""
        self.track = None

    async def do_next(self) -> None:
        if self.is_playing or self.waiting:
            return

        # Clear the votes for a new song...
        self.pause_votes.clear()
        self.resume_votes.clear()
        self.skip_votes.clear()
        self.shuffle_votes.clear()
        self.stop_votes.clear()
        self.loop_votes.clear()

        if self.looped == True:
            self.waiting = False
            await self.play(self.looped_track)
            self.time = time.time()
            await self.invoke_controller()
            return

        try:
            if self.unlimit is True:
                self.waiting = True
                self.track = await self.queue.get()
                return

            self.waiting = True
            with async_timeout.timeout(300):
                self.track = await self.queue.get()
        except asyncio.TimeoutError:
            # No music has been played for 5 minutes, cleanup and disconnect...
            return await self.teardown()

        await self.play(self.track)
        self.time = time.time()
        self.waiting = False

        # Invoke our players controller...
        await self.invoke_controller()

    async def invoke_controller(self) -> None:
        """Method which updates or sends a new player controller."""
        if self.updating:
            return

        self.updating = True

        if not self.controller:
            self.controller = InteractiveController(
                embed=self.build_embed(), player=self
            )
            await self.controller.start(self.context)

        elif not await self.is_position_fresh():
            try:
                await self.controller.message.delete()
            except discord.HTTPException:
                pass

            self.controller.stop()

            self.controller = InteractiveController(
                embed=self.build_embed(), player=self
            )
            try:
                await self.controller.start(self.context)
            except Exception:
                pass

        else:
            embed = self.build_embed()
            await self.controller.message.edit(content=None, embed=embed)

        self.updating = False

    def build_embed(self) -> typing.Optional[discord.Embed]:
        """Method which builds our players controller embed."""
        track = self.current
        if not track:
            return

        embed = discord.Embed(
            title="Now playing",
            description=f"[{track.title}]({track.uri}) | {track.requester.mention}",
            color=self.bot.color,
        )

        return embed

    def now_playing(self) -> typing.Optional[discord.Embed]:
        """Method which builds our now playing embed."""
        track = self.current
        if not track:
            return

        channel = self.bot.get_channel(int(self.channel_id))
        qsize = self.queue.qsize()
        end_time = time.time()
        passe = float(end_time) - float(self.time)
        passed = str(datetime.timedelta(seconds=int(passe)))
        if not track.is_stream:
            total = str(datetime.timedelta(milliseconds=int(track.length)))
            final = f"{passed}/{total}"
        else:
            total = "Live Stream"
            final = "Live Stream"

        if self.looped == True:
            next_in = f"__This track is Looped!__"
        else:
            try:
                next_in = self.queue._queue[0]
            except Exception:
                next_in = "Nothing played next this one."

        embed = discord.Embed(
            title=f"**{track.title}**",
            url=f"{track.uri}",
            description=f"**Requester**: {track.requester.mention}\n**Duration**: {final}\n**Artist**: {track.author}\n\n**Up Next**: {next_in}",
            color=self.bot.color,
        )
        embed.set_footer(
            text=f"Playing in {channel.name} | Songs in queue : {qsize}",
            icon_url=track.requester.avatar_url,
        )
        if track.thumb:
            embed.set_thumbnail(url=track.thumb)

        return embed

    async def is_position_fresh(self) -> bool:
        """Method which checks whether the player controller should be remade or updated."""
        try:
            async for message in self.context.channel.history(limit=5):
                if message.id == self.controller.message.id:
                    return True
        except (discord.HTTPException, AttributeError):
            return False

        return False

    async def teardown(self):
        """Clear internal states, remove player controller and disconnect."""
        try:
            await self.controller.message.delete()
        except Exception:
            pass

        if self.controller:
            try:
                self.controller.stop()
            except Exception:
                pass

        try:
            await self.destroy()
        except Exception:
            await self.destroy(force=True)


class InteractiveController(menus.Menu):
    """The Players interactive controller menu class."""

    def __init__(self, *, embed: discord.Embed, player: Player):
        super().__init__(timeout=None)

        self.embed = embed
        self.player = player

    def update_context(self, payload: discord.RawReactionActionEvent):
        """Update our context with the user who reacted."""
        ctx = copy.copy(self.ctx)
        ctx.author = payload.member

        return ctx

    def reaction_check(self, payload: discord.RawReactionActionEvent):
        if payload.event_type == "REACTION_REMOVE":
            return False

        if not payload.member:
            return False
        if payload.member.bot:
            return False
        if payload.message_id != self.message.id:
            return False
        if (
            payload.member
            not in self.bot.get_channel(int(self.player.channel_id)).members
        ):
            return False

        return payload.emoji in self.buttons

    async def send_initial_message(
        self, ctx: commands.Context, channel: discord.TextChannel
    ) -> discord.Message:
        return await channel.send(embed=self.embed)


class PaginatorSource(menus.ListPageSource):
    """Player queue paginator class."""

    def __init__(self, entries, *, per_page=5):
        entries = [f"{index} | {title}" for index, title in enumerate(entries, 1)]
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        player: Player = menu.bot.wavelink.get_player(
            guild_id=menu.ctx.guild.id, cls=Player, context=menu.ctx
        )
        embed = discord.Embed(color=0xB81217)
        embed.set_author(
            name=f"{menu.ctx.guild.name} queue ({player.queue.qsize()} songs)",
            icon_url="https://cdn.discordapp.com/emojis/846314042120470528.gif?v=1",
        )
        embed.description = "\n".join(page)

        return embed


class Music(commands.Cog, wavelink.WavelinkMixin):
    """Music Cog."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.category = "Music"
        self.session = aiohttp.ClientSession()
        self.task = self.bot.loop.create_task(self.ensure_node())

        if not hasattr(bot, "wavelink"):
            bot.wavelink = wavelink.Client(bot=bot)

        bot.loop.create_task(self.start_nodes())

    def cog_unload(self):
        self.task.cancel()

    async def ensure_node(self):
        while True:
            if self.bot.wavelink.nodes:
                for node in self.bot.wavelink.nodes:
                    try:
                        if not node.is_available:
                            await node._websocket._connect()
                    except:
                        pass

            await asyncio.sleep(1)

    async def start_nodes(self):
        await self.bot.wait_until_ready()
        for i in range(self.bot.shard_count):
            await self.bot.wavelink.initiate_node(
                            host="lava.link",
                            port=80,
                            rest_uri="http://lava.link:80",
                            password="youshallnotpass",
                            identifier=f"Ami-{i}",
                            region="germany",
                            heartbeat=60,
                            shard_id=i
                        )

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node: wavelink.Node):
        print(f"Node {node.identifier} is ready!")

    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node: wavelink.Node, payload):
        await payload.player.do_next()

    @wavelink.WavelinkMixin.listener(
        "on_track_exception"
    )  # ty to cryptex for helping because jadon is stupid omegalul
    async def on_node_event_(self, node, event):
        if "YouTube (429)" in event.error:
            player = event.player
            if URL_REG.fullmatch(player.query):
                new_track = await self.bot.wavelink.get_tracks(
                    f"scsearch:{player.track.title}"
                )
            else:
                new_track = await self.bot.wavelink.get_tracks(
                    f"scsearch:{player.query}"
                )
            if new_track:
                track = Track(
                    new_track[0].id,
                    new_track[0].info,
                    requester=player.context.author,
                )
                await player.queue.put(track)
                await player.do_next()
                try:
                    await player.context.send(embed=Player.build_embed())
                except Exception:
                    return
            else:
                try:
                    await player.context.send(
                        "<:4318crossmark:848857812565229601> No results was found for your query, try again."
                    )
                except Exception:
                    return
        else:
            try:
                await event.player.context.send(
                    f"<:4318crossmark:848857812565229601> {event.error}"
                )
            except Exception:
                return

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        await self.bot.wait_until_ready()
        if member.bot:
            return

        try:
            player: Player = self.bot.wavelink.get_player(member.guild.id, cls=Player)
        except wavelink.ZeroConnectedNodes or wavelink.errors.InvalidIDProvided:
            return

        if not player.channel_id or not player.context:
            player.node.players.pop(member.guild.id)
            return

        channel = self.bot.get_channel(int(player.channel_id))

        if len(channel.members) < 2:
            if player.unlimit:
                return
            em = discord.Embed(
                description=f"<:4318crossmark:848857812565229601> Leaving {channel.mention} because **all** left me alone...",
                color=self.bot.color,
            )
            try:
                await player.context.channel.send(embed=em, delete_after=20)
            except discord.Forbidden:
                pass
            return await player.teardown()

        if member == player.dj and after.channel is None:
            for m in channel.members:
                if m.bot:
                    continue
                else:
                    player.dj = m
                    await player.context.send(
                        f"<:4430checkmark:848857812632076314> {m.mention} is the new **DJ** because the last one has __left__ the voice channel.",
                        allowed_mentions=discord.AllowedMentions.none(),
                    )
                    return

        elif after.channel == channel and player.dj not in channel.members:
            player.dj = member
            await player.context.send(
                f"<:4430checkmark:848857812632076314> {member.mention} is the new **DJ** because the last one has __left__ the voice channel.",
                allowed_mentions=discord.AllowedMentions.none(),
            )

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        """Cog wide error handler."""
        if isinstance(error, IncorrectChannelError):
            raise IncorrectChannelError

        if isinstance(error, NoChannelProvided):
            await ctx.send(
                "<:4318crossmark:848857812565229601> You are not in a voice channel"
            )
            raise NoChannelProvided

    async def cog_check(self, ctx: commands.Context):
        """Coroutine called before command invocation.
        We mainly just want to check whether the user is in the players controller channel.
        """
        try:
            player: Player = self.bot.wavelink.get_player(
                ctx.guild.id, cls=Player, context=ctx
            )
        except wavelink.ZeroConnectedNodes:
            return False

        if not player.context.channel:
            return False

        if player.context:
            if player.context.channel != ctx.channel:
                em = discord.Embed(
                    description=f"<:4318crossmark:848857812565229601> {ctx.author.mention}, i am already in {player.context.channel.mention}",
                    color=self.bot.color,
                )
                try:
                    await ctx.send(embed=em)
                except Exception:
                    pass
                return False

        if ctx.command.name == "join" and not player.context:
            return True
        elif self.is_privileged(ctx):
            return True

        if not player.channel_id:
            return False

        channel = self.bot.get_channel(int(player.channel_id))
        if not channel:
            return False

        if player.is_connected:
            if ctx.author not in channel.members:
                em = discord.Embed(
                    description=f"<:4318crossmark:848857812565229601> {ctx.author.mention} join in {channel.mention} to use __music__ commands.",
                    color=self.bot.color,
                )
                try:
                    await ctx.send(embed=em)
                except Exception:
                    pass
                return False

        return True

    def required(self, ctx: commands.Context):
        """Method which returns required votes based on amount of members in a channel."""
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )
        channel = self.bot.get_channel(int(player.channel_id))
        required = math.ceil((len(channel.members) - 1) / 2.5)

        if ctx.command.name == "stop":
            if len(channel.members) == 3:
                required = 3

        return required

    def is_privileged(self, ctx: commands.Context):
        """Check whether the user is an Admin or DJ."""
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        team = [
            144126010642792449,
            410452466631442443,
            711057339360477184,
            590323594744168494,
            691406006277898302,
            343019667511574528,
        ]

        return (
            ctx.author.id in team
            or player.dj == ctx.author
            or ctx.author.guild_permissions.kick_members
        )

    @commands.command(
        help="Make me leave the channel where i am.",
        aliases=["dc", "disconnect", "quit"],
    )
    async def leave(self, ctx: commands.Context):
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        if not player.is_connected:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> | Not connected to any voice channel."
            )

        if not self.is_privileged(ctx):
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | Only the **DJ** or **admins** can use this command."
            )

        channel = self.bot.get_channel(player.channel_id)

        try:
            await player.teardown()
        except Exception:
            await player.disconnect()
        em = discord.Embed(
            description=f"<:4318crossmark:848857812565229601> | Disconnected from {channel.mention}",
            color=self.bot.color,
        )
        await ctx.send(embed=em)

    @commands.command(help="Make me join in a voice channel to play some music ^^")
    async def join(
        self, ctx: commands.Context, *, channel: discord.VoiceChannel = None
    ):
        """Connect to a voice channel."""
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        if player.is_connected:
            chan = self.bot.get_channel(player.channel_id)
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> | Already connected to {chan.mention}."
            )

        channel = getattr(ctx.author.voice, "channel", channel)
        if channel is None:
            await ctx.send(
                "<:4318crossmark:848857812565229601> | You are not connected to any voice channel."
            )
            return

        await player.connect(channel.id)
        if isinstance(channel, discord.StageChannel):
            try:
                payload = {"channel_id": channel.id, "suppress": False}
                return await self.bot.http.edit_my_voice_state(ctx.guild.id, payload)
            except:
                try:
                    payload = {
                        "channel_id": channel.id,
                        "request_to_speak_timestamp": datetime.datetime.utcnow().isoformat(),
                    }
                    return await self.bot.http.edit_my_voice_state(
                        ctx.guild.id, payload
                    )
                except:
                    return await ctx.send(
                        "<:4318crossmark:848857812565229601> I need the `Request To Speak` / `Manage Stage` permission to play here."
                    )

        await ctx.guild.change_voice_state(channel=channel, self_deaf=True)

    @commands.command(
        help="Retrive the lyrics for the current playing song if there's one, else specify the `song` argument with a song name to retrive the lyrics for that song."
    )
    async def lyrics(self, ctx: commands.Context, *, song=None):
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        song_name = song

        if not song:
            if not player.current:
                return await ctx.send(
                    "<:4318crossmark:848857812565229601> Nothing played right now to search lyrics for."
                )
            song_name = player.current.title

        try:
            lyrics = await srclient.get_lyrics(f"{song_name}", False)
        except Exception:
            c = song
            if player.current:
                c = player.current.title
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> Something went wrong while searching lyrics for **{c}**"
            )

        try:
            em = discord.Embed(
                title=f"{lyrics.title}",
                description=f"{lyrics.lyrics}",
                color=self.bot.color,
            )
            em.set_thumbnail(url=lyrics.thumbnail)
            await ctx.send(embed=em)
        except Exception:
            async with aiofiles.open("lyrics.txt", "w", encoding="utf-8") as f:
                await f.write(f"{lyrics.lyrics}")

            await ctx.send(
                "<:4318crossmark:848857812565229601> Lyrics too long to embed, here's a `.txt` file of it."
            )
            return await ctx.send(file=discord.File("lyrics.txt"))

    @commands.command(
        help="Make me play music in voice channels, this require you to be in a valid voice channel.\nThis supports `youtube` & `soundcloud`.\nUse `ami play songname --sc` if the standard music request doesn't play.",
        aliases=["p", "pump"],
    )
    async def play(self, ctx: commands.Context, *, query: str):
        """Play or queue a song with the given query."""
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        if SPOTIFY_URL_REG.match(query):
            em = discord.Embed(
                title="⚠ Spotify URL Detected",
                description=f"<:4318crossmark:848857812565229601> | {ctx.author.mention} __spotify__ is not supported yet.",
                color=self.bot.color,
            )
            return await ctx.send(embed=em)

        if not player.is_connected:
            if ctx.author.voice:
                await ctx.invoke(self.join)
            else:
                return await ctx.send(
                    "<:4318crossmark:848857812565229601> | You are not connected to any voice channel."
                )

        query = query.strip("<>")

        player.query = query

        if not URL_REG.match(query):
            if query.endswith("--sc"):
                query = f"scsearch:{query}"
            else:
                query = f"ytsearch:{query}"

        try:
            tracks = await self.bot.wavelink.get_tracks(query)
        except wavelink.ZeroConnectedNodes:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> | {ctx.author.mention} looks like the music server is actually down, please try again later."
            )
        if not tracks:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | No **results** was found for your query, try again."
            )

        if isinstance(tracks, wavelink.TrackPlaylist):
            for track in tracks.tracks:
                track = Track(track.id, track.info, requester=ctx.author)
                await player.queue.put(track)
            em = discord.Embed(
                description=f"<:4430checkmark:848857812632076314> Added **{len(tracks.tracks)}** songs to the queue from **{tracks.data['playlistInfo']['name']}** playlist.",
                color=self.bot.color,
            )
            await ctx.send(embed=em)
        else:
            track = Track(tracks[0].id, tracks[0].info, requester=ctx.author)
            em = discord.Embed(
                description=f"<:4430checkmark:848857812632076314> Queued [{track.title}]({track.uri}) | {track.requester.mention}",
                color=self.bot.color,
            )
            await ctx.send(embed=em)
            await player.queue.put(track)

        if not player.is_playing:
            await player.do_next()

    @commands.command(help="Make me pause the current playing song.")
    async def pause(self, ctx: commands.Context):
        """Pause the currently playing song."""
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        if player.is_paused or not player.is_connected:
            return

        if self.is_privileged(ctx):
            em = discord.Embed(
                description=f"<:4430checkmark:848857812632076314> | **{ctx.author.name}** has paused the player.",
                color=self.bot.color,
            )
            await ctx.send(embed=em)
            player.pause_votes.clear()

            return await player.set_pause(True)

        if ctx.author in player.pause_votes:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> | {ctx.author.mention}, you have already voted to pause."
            )

        required = self.required(ctx)
        player.pause_votes.add(ctx.author)

        if len(player.pause_votes) >= required:
            await ctx.send(
                f"<:4430checkmark:848857812632076314> | Reached **{required}** votes to pause. Pausing player."
            )
            player.pause_votes.clear()
            await player.set_pause(True)
        else:
            await ctx.send(
                f"<:4430checkmark:848857812632076314> | {ctx.author.mention} has voted to pause the player."
            )

    @commands.command(help="Make me resume the paused song.")
    async def resume(self, ctx: commands.Context):
        """Resume a currently paused player."""
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        if not player.is_paused or not player.is_connected:
            return

        if self.is_privileged(ctx):
            em = discord.Embed(
                description=f"<:4430checkmark:848857812632076314> | **{ctx.author.name}** has resumed the player.",
                color=self.bot.color,
            )
            await ctx.send(embed=em)
            player.resume_votes.clear()

            return await player.set_pause(False)

        if ctx.author in player.resume_votes:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> | {ctx.author.mention}, you have already voted to resume."
            )

        required = self.required(ctx)
        player.resume_votes.add(ctx.author)

        if len(player.resume_votes) >= required:
            await ctx.send(
                f"<:4430checkmark:848857812632076314> | Reached **{required}** votes to resume. Resuming player."
            )
            player.resume_votes.clear()
            await player.set_pause(False)
        else:
            await ctx.send(
                f"<:4430checkmark:848857812632076314> | {ctx.author.mention} has voted to resume the player."
            )

    @commands.command(
        help="Skip the current playing song to the next in the queue: if no next song in queue, this command works like `ami stop`."
    )
    async def skip(self, ctx: commands.Context):
        """Skip the currently playing song."""
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        if not player.is_connected:
            return

        if not player.current:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> Nothing playing right now."
            )

        if self.is_privileged(ctx):
            em = discord.Embed(
                description=f"<:4430checkmark:848857812632076314> | **{ctx.author.name}** has skipped the song.",
                color=self.bot.color,
            )
            await ctx.send(embed=em)
            player.skip_votes.clear()

            return await player.stop()

        if ctx.author == player.current.requester:
            em = discord.Embed(
                description=f"<:4430checkmark:848857812632076314> | **{ctx.author.name}** has skipped the song.",
                color=self.bot.color,
            )
            await ctx.send(embed=em)
            player.skip_votes.clear()

            return await player.stop()

        if ctx.author in player.skip_votes:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> | {ctx.author.mention}, you have already voted to skip."
            )

        required = self.required(ctx)
        player.skip_votes.add(ctx.author)

        if len(player.skip_votes) >= required:
            await ctx.send(
                f"<:4430checkmark:848857812632076314> | Reached **{required}** votes, skipping song."
            )
            player.skip_votes.clear()
            await player.stop()
        else:
            await ctx.send(
                f"<:4430checkmark:848857812632076314> | {ctx.author.mention} has voted to skip the song."
            )

    @commands.command(help="Stop the current playing song.")
    async def stop(self, ctx: commands.Context):
        """Stop the player and clear all internal states."""
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        if not player.is_connected:
            return

        if self.is_privileged(ctx):
            em = discord.Embed(
                description=f"<:4430checkmark:848857812632076314> | **{ctx.author.name}** has stopped the player.",
                color=self.bot.color,
            )
            await ctx.send(embed=em)
            return await player.teardown()

        if ctx.author in player.stop_votes:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> | {ctx.author.mention}, you have already voted to stop."
            )

        required = self.required(ctx)
        player.stop_votes.add(ctx.author)

        if len(player.stop_votes) >= required:
            await ctx.send(
                f"<:4430checkmark:848857812632076314> | Reached **{required}** votes, stopping the player."
            )
            try:
                await player.teardown()
            except Exception:
                await player.disconnect()
        else:
            await ctx.send(
                f"<:4430checkmark:848857812632076314> | {ctx.author.mention} has voted to stop the player."
            )

    @commands.command(
        help="Set/change the volume of the current player.", aliases=["vol"]
    )
    @premium(override=True)
    async def volume(self, ctx: commands.Context, *, vol: int = None):
        """Change the players volume, between 1 and 250."""
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        if not player.is_connected:
            return

        if not vol:
            em = discord.Embed(
                description=f"🌹 Player volume is **`{player.volume}%`**",
                color=self.bot.color,
            )
            return await ctx.send(embed=em)

        if not self.is_privileged(ctx):
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | Only the **DJ** or **admins** may change the volume."
            )

        if not 0 < vol < 251:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | Volume must be between **1** and **250**"
            )

        await player.set_volume(vol)
        await ctx.message.add_reaction("✅")

    @commands.command(help="Shuffle the songs in the queue.", aliases=["mix"])
    async def shuffle(self, ctx: commands.Context):
        """Shuffle the players queue."""
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        if not player.is_connected:
            return

        if player.queue.qsize() < 3:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> | You may need at least **`3`** songs into the queue, **`{player.queue.qsize()}`** are in the queue."
            )

        if self.is_privileged(ctx):
            await ctx.send(
                "<:4430checkmark:848857812632076314> | An **admin** or **DJ** has shuffled the playlist."
            )
            player.shuffle_votes.clear()
            return random.shuffle(player.queue._queue)

        if ctx.author in player.shuffle_votes:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> | {ctx.author.mention}, you have already voted to shuffle."
            )

        required = self.required(ctx)
        player.shuffle_votes.add(ctx.author)

        if len(player.shuffle_votes) >= required:
            await ctx.send(
                "<:4430checkmark:848857812632076314> | Vote to shuffle passed. Shuffling the playlist."
            )
            player.shuffle_votes.clear()
            random.shuffle(player.queue._queue)
        else:
            await ctx.send(
                f"<:4430checkmark:848857812632076314> | {ctx.author.mention} has voted to shuffle the playlist."
            )

    @commands.command(
        help="Set the equalizer, a filter for the current playing song.\nSet the `[equalizer]` argument as `list` to see all available equalizers.\nLeave `[equalizer]` blank to reset the base equalizer.",
        aliases=["eq"],
    )
    @premium(override=True)
    async def equalizer(self, ctx: commands.Context, *, equalizer: str = None):
        """Change the players equalizer."""
        if equalizer == None:
            equalizer = "base"

        if equalizer == "list":
            em = discord.Embed(
                title="<:catgirluppies:839518621767172106> | Equalizers",
                description="`base` : Base equalizer, standard sound.\n"
                "`bass` : Optimal for songs with high 808.\n"
                "`metal` : High reveerb on voice, optimal for singed songs.\n"
                "`piano` : Perfect for chilling, works well with voice.\n"
                "`rave` : Optimal for psytrance / acid.",
                color=self.bot.color,
            )
            em.set_footer(text="The equalizer can take up to 5 seconds to set.")
            return await ctx.send(embed=em)
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        if not player.is_connected:
            return await ctx.reply(
                "<:4318crossmark:848857812565229601> | Not playing anything at the moment."
            )

        if not self.is_privileged(ctx):
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | Only the **DJ** or **admins** may change the equalizer."
            )

        eqs = {
            "base": wavelink.Equalizer.flat(),
            "bass": wavelink.Equalizer.boost(),
            "metal": wavelink.Equalizer.metal(),
            "piano": wavelink.Equalizer.piano(),
            "rave": wavelink.Equalizer.build(
                levels=[
                    (0, -0.295),
                    (1, 0.150),
                    (2, 0.150),
                    (3, 0.1),
                    (4, 0.1),
                    (5, 0.05),
                    (6, 0.075),
                    (7, 0.0),
                    (8, 0.0),
                    (9, 0.0),
                    (10, 0.0),
                    (11, 0.0),
                    (12, 0.125),
                    (13, 0.15),
                    (14, 0.05),
                ],
                name="RaveEQ",
            ),
        }

        eq = eqs.get(equalizer.lower(), None)

        if not eq:
            joined = ", ".join(eqs.keys())
            em = discord.Embed(
                title="<:4318crossmark:848857812565229601> | Invalid EQ provided.",
                description=f"You've provided an invalid equalizer, available equalizers are:\n**`{joined}`**",
                color=self.bot.color,
            )
            return await ctx.send(embed=em)

        em = discord.Embed(
            description=f"<:4430checkmark:848857812632076314> | {ctx.author.mention} has set the equalizer to **`{equalizer}`**.",
            color=self.bot.color,
        )
        await ctx.send(embed=em)
        await player.set_eq(eq)

    @commands.command(
        help="Move the player seek to the given position (in seconds).\nIf seek is not specified, it set the seek to 0"
    )
    @premium(override=True)
    async def seek(self, ctx: commands.Context, seek_number: int = None):
        """Set the seek position for the current playing song.
        This must be an int or float, raise SeekErrorNotValid if <seek_number> invalid."""

        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        if seek_number == None:
            seek_number = 0

        if not self.is_privileged(ctx):
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | Only the **DJ** or **admins** may move the seek of the song."
            )

        if seek_number > int(player.current.length):
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> | Seek can't be more than the track lenght (`{int(player.current.length)}`)."
            )

        seeky = seek_number * 1000
        scd = "{}".format(humanize.precisedelta(seek_number))
        await player.seek(seeky)
        em = discord.Embed(
            description=f"<:4430checkmark:848857812632076314> | Player seek moved to **{scd}**",
            color=self.bot.color,
        )
        await ctx.send(embed=em)

    @commands.command(
        help="See the songs in queue for the actual player playing.\nUse `ami queue clear` to clear the queue (removing all songs in it) <- This require you to be the **DJ** / **Admin**.",
        aliases=["q", "que"],
    )
    async def queue(self, ctx: commands.Context, clear=None):
        """Display the players queued songs."""
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        if clear:
            if clear == "clear":

                if player.queue.qsize() == 0:
                    return await ctx.send(
                        "<:4318crossmark:848857812565229601> | The queue is empty."
                    )

                if not self.is_privileged(ctx):
                    return await ctx.send(
                        "<:4318crossmark:848857812565229601> | Only the **DJ** or **admins** can clear the full queue."
                    )

                await ctx.send(
                    f"<:4430checkmark:848857812632076314> | The queue has been cleared by {ctx.author.mention}! (**{player.queue.qsize()} tracks**)"
                )
                return player.queue._queue.clear()

        if not player.is_connected:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | Not connected to any voice channel."
            )

        if player.queue.qsize() == 0:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | The queue is empty."
            )

        entries = [
            f"[{track.title}]({track.uri})\n[`{str(datetime.timedelta(milliseconds=int(track.length)))}`] -> {track.requester.mention}\n"
            for track in player.queue._queue
        ]
        pages = PaginatorSource(entries=entries)
        paginator = menus.MenuPages(
            source=pages, timeout=None, delete_message_after=True
        )

        await paginator.start(ctx)

    @commands.command(
        help="Check what'im playing right now.",
        aliases=["np", "now_playing", "current"],
    )
    async def nowplaying(self, ctx: commands.Context):
        """Update the player controller."""
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        if not player.is_connected:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | Nothing playing at the moment."
            )

        if not player.current:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | Nothing playing at the moment."
            )

        await ctx.send(embed=player.now_playing())

    @commands.command(
        help="Swap the song DJ to another member.\nIf member not specified, it choose a random member in the voice channel.\nIf the members in the vc are 2 or less, the dj can't be swapped without member specified.",
        aliases=["swap"],
    )
    async def swapdj(self, ctx: commands.Context, *, member: discord.Member):
        """Swap the current DJ to another member in the voice channel."""
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        if not player.is_connected:
            return

        if not self.is_privileged(ctx):
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | Only **admins** and the **DJ** may swap the dj."
            )

        members = self.bot.get_channel(int(player.channel_id)).members

        if member and member not in members:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> | {member} is not in the voice channel."
            )

        if member and member == player.dj:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | Can't give **DJ** to the current **DJ**."
            )

        if len(members) <= 2:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | No more members for **auto-swap**."
            )

        player.dj = member
        em = discord.Embed(
            description=f"<:4430checkmark:848857812632076314> | {ctx.author.mention} has gave the **DJ** to {member.mention}.",
            color=self.bot.color,
        )
        return await ctx.send(embed=em)

    @commands.command(
        help="Loop the current playing song to make me play it in loop!\nWorks in bool, send 1 time this command to loop, resend to unloop."
    )
    async def loop(self, ctx: commands.Context):

        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        if not player.current:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | Nothing is playing right now!"
            )

        if self.is_privileged(ctx):
            if not player.looped:
                player.looped = True
                player.looped_track = player.current
                em = discord.Embed(
                    description=f"<:4430checkmark:848857812632076314> | {ctx.author.mention} has enabled the **loop** for `{player.current}`.",
                    color=self.bot.color,
                )
                return await ctx.send(embed=em)
            else:
                player.looped = False
                player.looped_track = None
                em = discord.Embed(
                    description=f"<:4430checkmark:848857812632076314> | {ctx.author.mention} has disabled the **loop** for `{player.current}`.",
                    color=self.bot.color,
                )
                return await ctx.send(embed=em)

        if ctx.author in player.loop_votes:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> | {ctx.author.mention}, you have already voted to loop."
            )

        required = self.required(ctx)
        player.loop_votes.add(ctx.author)

        if len(player.loop_votes) >= required:
            if not player.looped:
                await ctx.send(
                    f"<:4430checkmark:848857812632076314> | Reached {required} votes to loop. Looping player."
                )
                player.loop_votes.clear()
            else:
                await ctx.send(
                    f"<:4430checkmark:848857812632076314> | Reached {required} votes to unloop. Unlooping player."
                )
                player.loop_votes.clear()
        else:
            if not player.looped:
                await ctx.send(
                    f"<:4430checkmark:848857812632076314> | {ctx.author.mention} has voted to loop the player."
                )
            else:
                await ctx.send(
                    f"<:4430checkmark:848857812632076314> | {ctx.author.mention} has voted to unloop the player."
                )

    @commands.command(
        name="24/7",
        help="Enable the **24/7** mode for the music, this mode will keep me 24h/7 in the vc without make me leave!",
    )
    @premium(override=True)
    async def tfs(self, ctx: commands.Context):
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )

        if not player.is_connected:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | Not connected to any voice channel right now!"
            )

        if not player.current:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | Nothing is playing right now!"
            )

        if self.is_privileged(ctx):
            if player.unlimit is True:
                player.unlimit = False
                em = discord.Embed(
                    description=f"<:4430checkmark:848857812632076314> | {ctx.author.mention} has disabled the **24/7** mode.",
                    color=self.bot.color,
                )
                return await ctx.send(embed=em)

            if player.unlimit is False:
                player.unlimit = True
                em = discord.Embed(
                    description=f"<:4430checkmark:848857812632076314> | {ctx.author.mention} has enabled the **24/7** mode.",
                    color=self.bot.color,
                )
                return await ctx.send(embed=em)

    @commands.command(
        help="Apply custom filters to the actual playing song with up to 5 filters!\nType `ami filter list` to see the availables filters.\nUse `ami filter reset` to reset the standard filter.\nOnly DJ & Admins can apply filters.",
        aliases=["ft"],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @premium(override=True)
    async def filter(self, ctx: commands.Context, *, filter: str):
        player: Player = self.bot.wavelink.get_player(
            guild_id=ctx.guild.id, cls=Player, context=ctx
        )
        apply_filter = player.node._websocket._send

        base = {
            "op": "filters",
            "guildId": f"{ctx.guild.id}",
            "timescale": {"speed": 1.0, "pitch": 1.0, "rate": 1.0},
        }

        filters = {
            "nightcore": {
                "op": "filters",
                "guildId": f"{ctx.guild.id}",
                "timescale": {"speed": 1.1, "pitch": 1.3, "rate": 1.1},
            },
            "low voice": {
                "op": "filters",
                "guildId": f"{ctx.guild.id}",
                "timescale": {"speed": 1.0, "pitch": 0.7, "rate": 1.0},
            },
            "sonicspeed": {
                "op": "filters",
                "guildId": f"{ctx.guild.id}",
                "timescale": {"speed": 2.0, "pitch": 1.0, "rate": 1.0},
            },
            "relax": {
                "op": "filters",
                "guildId": f"{ctx.guild.id}",
                "timescale": {"speed": 0.9, "pitch": 1.0, "rate": 0.8},
                "tremolo": {"frequency": 2.0, "depth": 0.8},
                "vibrato": {"frequency": 2.0, "depth": 0.8},
            },
            "8d": {
                "op": "filters",
                "guildId": f"{ctx.guild.id}",
                "timescale": {"speed": 1.0, "pitch": 0.9, "rate": 1.1},
                "rotation": {"rotationHz": 0.2},
            },
        }

        filt = filters.get(filter.lower(), None)

        if filter == "reset":
            payload = base
            await apply_filter(**payload)
            em = discord.Embed(
                description=f"<:4430checkmark:848857812632076314> | {ctx.author.mention} has reset the filter to standard.",
                color=self.bot.color,
            )
            return await ctx.send(embed=em)

        if filter == "list":
            joined = ", ".join(filters.keys())
            em = discord.Embed(
                title="<:catgirluppies:839518621767172106> | Filters",
                description=f"Here it is all availables filters:\n**`{joined}`**",
                color=self.bot.color,
            )
            return await ctx.send(embed=em)

        if not player.current:
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | Nothing is playing right now!"
            )

        if not self.is_privileged(ctx):
            return await ctx.send(
                "<:4318crossmark:848857812565229601> | Only the **DJ** or **admins** can set filters."
            )

        if not filt:
            joined = ", ".join(filters.keys())
            em = discord.Embed(
                title="<:4318crossmark:848857812565229601> | Invalid filter provided.",
                description=f"You've provided an invalid filter, available filters are:\n**`{joined}`**",
                color=self.bot.color,
            )
            return await ctx.send(embed=em)

        payload = filters[filter.lower()]
        await apply_filter(**payload)
        m = await ctx.send(
            f"<:4430checkmark:848857812632076314> Applying the filter..."
        )
        await asyncio.sleep(5)
        await m.delete()
        em = discord.Embed(
            description=f"<:4430checkmark:848857812632076314> | {ctx.author.mention} has set the `{filter.title()}` filter.",
            color=self.bot.color,
        )
        await ctx.send(embed=em)

    @commands.command()
    @is_team()
    async def waveinfo(self, ctx):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        node = player.node

        used = humanize.naturalsize(node.stats.memory_used)
        total = humanize.naturalsize(node.stats.memory_allocated)
        free = humanize.naturalsize(node.stats.memory_free)
        cpu = node.stats.cpu_cores
        version = wavelink.__version__

        await ctx.send(
            embed=discord.Embed(
                title="Wavelink / Lavalink Server Info",
                description=f"**WaveLink:** `{version}`\n\nConnected to `{len(self.bot.wavelink.nodes)}` nodes.\nBest available Node `{self.bot.wavelink.get_best_node().__repr__()}`\n`{len(self.bot.wavelink.players)}` players are distributed on nodes.\n`{node.stats.players}` players are distributed on server.\n`{node.stats.playing_players}` players are playing on server.\n\nServer Memory: `{used}/{total}` | `({free} free)`\nServer CPU: `{cpu}`\n\nServer Uptime: `{datetime.timedelta(milliseconds=node.stats.uptime)}`\n\n**Node Info**:\nHost: `{node.host}`\nRest URI: `{node.rest_uri}`\nHeartbeat: `{node.heartbeat}`\n",
                color=self.bot.color,
                timestamp=datetime.datetime.utcnow(),
            ).set_thumbnail(url=self.bot.user.avatar_url)
        )
        pass

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            player: Player = self.bot.wavelink.get_player(
                guild_id=guild.id, cls=Player, context=commands.Context
            )
            if player:
                await player.destroy()

            if player.controller:
                await player.controller.stop()
        except Exception:
            pass


def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))

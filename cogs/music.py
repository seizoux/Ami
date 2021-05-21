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
from jishaku.paginators import WrappedPaginator, PaginatorInterface

# URL matching REGEX...
URL_REG = re.compile(r'https?://(?:www\.)?.+')


class NoChannelProvided(commands.CommandError):
    """Error raised when no suitable voice channel was supplied."""
    pass


class IncorrectChannelError(commands.CommandError):
    """Error raised when commands are issued outside of the players session channel."""
    pass


class Track(wavelink.Track):
    """Wavelink Track object with a requester attribute."""

    __slots__ = ('requester', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.requester = kwargs.get('requester')


class Player(wavelink.Player):
    """Custom wavelink Player class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.context: commands.Context = kwargs.get('context', None)
        if self.context:
            self.dj: discord.Member = self.context.author

        self.queue = asyncio.Queue()
        self.controller = None
        self.looped = False
        self.looped_track = None

        self.waiting = False
        self.updating = False

        self.pause_votes = set()
        self.resume_votes = set()
        self.skip_votes = set()
        self.shuffle_votes = set()
        self.stop_votes = set()
        self.loop_votes = set()

    async def do_next(self) -> None:
        if self.is_playing or self.waiting:
            return
            
        # Clear the votes for a new song...
        self.pause_votes.clear()
        self.resume_votes.clear()
        self.skip_votes.clear()
        self.shuffle_votes.clear()
        self.stop_votes.clear()

        if self.looped == True:
            self.waiting = False
            await self.play(self.looped_track)
            await self.invoke_controller()
            return

        try:
            self.waiting = True
            with async_timeout.timeout(300):
                track = await self.queue.get()
        except asyncio.TimeoutError:
            # No music has been played for 5 minutes, cleanup and disconnect...
            return await self.teardown()

        await self.play(track)
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
            self.controller = InteractiveController(embed=self.build_embed(), player=self)
            await self.controller.start(self.context)

        elif not await self.is_position_fresh():
            try:
                await self.controller.message.delete()
            except discord.HTTPException:
                pass

            self.controller.stop()

            self.controller = InteractiveController(embed=self.build_embed(), player=self)
            await self.controller.start(self.context)

        else:
            embed = self.build_embed()
            await self.controller.message.edit(content=None, embed=embed)

        self.updating = False

    def build_embed(self) -> typing.Optional[discord.Embed]:
        """Method which builds our players controller embed."""
        track = self.current
        if not track:
            return

        channel = self.bot.get_channel(int(self.channel_id))
        qsize = self.queue.qsize()
        end_time = time.time()
        passe = float(end_time) - float(self.time)
        if not track.is_stream:
            total = str(datetime.timedelta(milliseconds=int(track.length)))
        else:
            total = "Live Stream"
        passed = str(datetime.timedelta(seconds=int(passe)))

        embed = discord.Embed(description=f'[`{track.title}`]({track.uri}) | {track.requester.mention}', color = 0xffcff1)
        embed.set_footer(text=f"Playing in {channel.name} | Duration: {total} | Played: {passed} | Songs in queue : {qsize}", icon_url=track.requester.avatar_url)

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
        except discord.HTTPException:
            pass

        self.controller.stop()

        try:
            await self.destroy()
        except KeyError:
            pass


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
        if payload.event_type == 'REACTION_REMOVE':
            return False

        if not payload.member:
            return False
        if payload.member.bot:
            return False
        if payload.message_id != self.message.id:
            return False
        if payload.member not in self.bot.get_channel(int(self.player.channel_id)).members:
            return False

        return payload.emoji in self.buttons

    async def send_initial_message(self, ctx: commands.Context, channel: discord.TextChannel) -> discord.Message:
        return await channel.send(embed=self.embed, delete_after=5)

class PaginatorSource(menus.ListPageSource):
    """Player queue paginator class."""

    def __init__(self, entries, *, per_page=10):
        entries = [f'**`{index}`** | {title}' for index, title in enumerate(entries, 1)]
        super().__init__(entries, per_page=per_page)

    async def format_page(self, menu: menus.Menu, page):
        embed = discord.Embed(title=f'<:FeelsBeatsMan:597591202614738947> Songs In Queue', color = 0xffcff1)
        embed.description = '\n'.join(page)

        return embed

    def is_paginating(self):
        # We always want to embed even on 1 page of results...
        return True


class Music(commands.Cog, wavelink.WavelinkMixin):
    """Music Cog."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.category = "Music"

        if not hasattr(bot, 'wavelink'):
            bot.wavelink = wavelink.Client(bot=bot)

        bot.loop.create_task(self.start_nodes())

    def cog_unload(self):
        self.bot.loop.create_task(self.destroy_players())

    async def destroy_players(self):
        for i in self.bot.wavelink.players.values():
            await i.destroy()

    async def start_nodes(self):
        node = await self.bot.wavelink.initiate_node(
                        host="127.0.0.1",
                        port=2333,
                        rest_uri="http://127.0.0.1:2333",
                        password="youshallnotpass",
                        identifier="Ami",
                        region="us_central",
                        heartbeat=60,
                    )

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node: wavelink.Node):
        print(f'Node {node.identifier} is ready!')

    @wavelink.WavelinkMixin.listener('on_track_stuck')
    @wavelink.WavelinkMixin.listener('on_track_end')
    @wavelink.WavelinkMixin.listener('on_track_exception')
    async def on_player_stop(self, node: wavelink.Node, payload):
        await payload.player.do_next()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if member.bot:
            return

        player: Player = self.bot.wavelink.get_player(member.guild.id, cls=Player)

        if not player.channel_id or not player.context:
            player.node.players.pop(member.guild.id)
            return

        channel = self.bot.get_channel(int(player.channel_id))

        if member == player.dj and after.channel is None:
            for m in channel.members:
                if m.bot:
                    continue
                else:
                    player.dj = m
                    return

        elif after.channel == channel and player.dj not in channel.members:
            player.dj = member

    async def cog_command_error(self, ctx: commands.Context, error: Exception):
        """Cog wide error handler."""
        if isinstance(error, IncorrectChannelError):
            return

        if isinstance(error, NoChannelProvided):
            return await ctx.send('<:redTick:596576672149667840> You are not in a voice channel')

    async def cog_check(self, ctx: commands.Context):
        """Cog wide check, which disallows commands in DMs."""
        if not ctx.guild:
            await ctx.send('<:redTick:596576672149667840> Music commands are not available in Private Messages.')
            return False

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        """Coroutine called before command invocation.
        We mainly just want to check whether the user is in the players controller channel.
        """
        player: Player = self.bot.wavelink.get_player(ctx.guild.id, cls=Player, context=ctx)

        if player.context:
            if player.context.channel != ctx.channel:
                em = discord.Embed(description=f"<:redTick:596576672149667840> {ctx.author.mention}, i am already in {player.context.channel.mention}", color = 0xffcff1)
                await ctx.send(embed=em, delete_after = 45)

        if ctx.command.name == 'connect' and not player.context:
            return
        elif self.is_privileged(ctx):
            return

        if not player.channel_id:
            return

        channel = self.bot.get_channel(int(player.channel_id))
        if not channel:
            return

        if player.is_connected:
            if ctx.author not in channel.members:
                em = discord.Embed(description=f"<:redTick:596576672149667840> {ctx.author.mention} join in {channel.mention} to use __music__ commands.", color = 0xffcff1)
                await ctx.send(embed=em, delete_after = 45)

    def required(self, ctx: commands.Context):
        """Method which returns required votes based on amount of members in a channel."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)
        channel = self.bot.get_channel(int(player.channel_id))
        required = math.ceil((len(channel.members) - 1) / 2.5)

        if ctx.command.name == 'stop':
            if len(channel.members) == 3:
                required = 3

        return required

    def is_privileged(self, ctx: commands.Context):
        """Check whether the user is an Admin or DJ."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        return player.dj == ctx.author or ctx.author.guild_permissions.kick_members

    @commands.command(help="Make me leave the channel where i am.", aliases=['dc', 'disconnect', 'quit'])
    async def leave(self, ctx: commands.Context):
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return await ctx.send(f"<:redTick:596576672149667840> Not connected to any voice channel.")

        if not self.is_privileged(ctx):
            return await ctx.send("<:redTick:596576672149667840> Only the **DJ** or **admins** can use this command.")

        channel = self.bot.get_channel(player.channel_id)

        await player.teardown()
        em = discord.Embed(description=f"<:redTick:596576672149667840> Disconnected from {channel.mention}", color = 0xffcff1)
        await ctx.send(embed=em, delete_after=3)

    @commands.command(help="Make me join in a voice channel to play some music ^^")
    async def join(self, ctx: commands.Context, *, channel: discord.VoiceChannel = None):
        """Connect to a voice channel."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if player.is_connected:
            chan = self.bot.get_channel(player.channel_id)
            return await ctx.send(f"<:redTick:596576672149667840> Already connected to {chan.mention}.")

        channel = getattr(ctx.author.voice, 'channel', channel)
        if channel is None:
            return await ctx.send("<:redTick:596576672149667840> You are not connected to any voice channel.")

        await player.connect(channel.id)
        await self.bot.ws.voice_state(ctx.guild.id, channel.id, self_deaf=True)
        em = discord.Embed(description=f"<:greenTick:596576670815879169> Joined in {channel.mention}", color = 0xffcff1)
        await ctx.send(embed=em, delete_after=3)

    @commands.command(help="Make me play music in voice channels, this require you to be in a valid voice channel.\nThis supports `youtube`, `soundcloud` & `spotify`.\nUse `ami play songname --sc` if the standard music request doesn't play.")
    async def play(self, ctx: commands.Context, *, query: str):
        """Play or queue a song with the given query."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            await ctx.invoke(self.join)

        query = query.strip('<>')
        if not URL_REG.match(query):
            if query.endswith("--sc"):
                query = f'scsearch:{query}'
            else:
                query = f'ytsearch:{query}'


        tracks = await self.bot.wavelink.get_tracks(query)
        if not tracks:
                return await ctx.send('<:redTick:596576672149667840> I got **0** results for this song.', delete_after=15)

        if isinstance(tracks, wavelink.TrackPlaylist):
            for track in tracks.tracks:
                track = Track(track.id, track.info, requester=ctx.author)
                await player.queue.put(track)

            em = discord.Embed(description=f"<:greenTick:596576670815879169> Added **`{len(tracks.tracks)}`** songs to the queue.", color = 0xffcff1)
            em.set_footer(text=f'Playlist name : {tracks.data["playlistInfo"]["name"]}')
            return await ctx.send(embed=em, delete_after=10)

        track = Track(tracks[0].id, tracks[0].info, requester=ctx.author)
        em = discord.Embed(description=f'<:greenTick:596576670815879169> Added **`{track.title}`** to the queue.', color = 0xffcff1)
        await ctx.send(embed=em, delete_after=5)
        await player.queue.put(track)

        if not player.is_playing:
            await player.do_next()


    @commands.command(help="Make me pause the current playing song.")
    async def pause(self, ctx: commands.Context):
        """Pause the currently playing song."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if player.is_paused or not player.is_connected:
            return

        if self.is_privileged(ctx):
            em = discord.Embed(description=f"<:greenTick:596576670815879169> **{ctx.author.name}** has paused the player.", color = 0xffcff1)
            await ctx.send(embed=em, delete_after=10)
            player.pause_votes.clear()

            return await player.set_pause(True)

        if ctx.author in player.pause_votes:
            return await ctx.send(f"<:redTick:596576672149667840> {ctx.author.mention}, you have already voted to pause.")

        required = self.required(ctx)
        player.pause_votes.add(ctx.author)

        if len(player.pause_votes) >= required:
            await ctx.send(f'<:greenTick:596576670815879169> Reached **{required}** votes to pause. Pausing player.', delete_after=10)
            player.pause_votes.clear()
            await player.set_pause(True)
        else:
            await ctx.send(f'<:greenTick:596576670815879169> {ctx.author.mention} has voted to pause the player.', delete_after=15)

    @commands.command(help="Make me resume the paused song.")
    async def resume(self, ctx: commands.Context):
        """Resume a currently paused player."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_paused or not player.is_connected:
            return

        if self.is_privileged(ctx):
            em = discord.Embed(description=f"<:greenTick:596576670815879169> **{ctx.author.name}** has resumed the player.", color = 0xffcff1)
            await ctx.send(embed=em, delete_after=10)
            player.resume_votes.clear()

            return await player.set_pause(False)

        if ctx.author in player.resume_votes:
            return await ctx.send(f"<:redTick:596576672149667840> {ctx.author.mention}, you have already voted to resume.")

        required = self.required(ctx)
        player.resume_votes.add(ctx.author)

        if len(player.resume_votes) >= required:
            await ctx.send(f'<:greenTick:596576670815879169> Reached **{required}** votes to resume. Resuming player.', delete_after=10)
            player.resume_votes.clear()
            await player.set_pause(False)
        else:
            await ctx.send(f'<:greenTick:596576670815879169> {ctx.author.mention} has voted to resume the player.', delete_after=15)

    @commands.command(help="Skip the current playing song to the next in the queue: if no next song in queue, this command works like `ami stop`.")
    async def skip(self, ctx: commands.Context):
        """Skip the currently playing song."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if self.is_privileged(ctx):
            em = discord.Embed(description=f"<:greenTick:596576670815879169> **{ctx.author.name}** has skipped the song.", color = 0xffcff1)
            await ctx.send(embed=em, delete_after=10)
            player.skip_votes.clear()

            return await player.stop()

        if ctx.author == player.current.requester:
            em = discord.Embed(description=f"<:greenTick:596576670815879169> **{ctx.author.name}** has skipped the song.", color = 0xffcff1)
            await ctx.send(embed=em, delete_after=10)
            player.skip_votes.clear()

            return await player.stop()

        if ctx.author in player.skip_votes:
            return await ctx.send(f"<:redTick:596576672149667840> {ctx.author.mention}, you have already voted to skip.")

        required = self.required(ctx)
        player.skip_votes.add(ctx.author)

        if len(player.skip_votes) >= required:
            await ctx.send(f'<:greenTick:596576670815879169> Reached **{required}** votes, skipping song.', delete_after=10)
            player.skip_votes.clear()
            await player.stop()
        else:
            await ctx.send(f'<:greenTick:596576670815879169> {ctx.author.mention} has voted to skip the song.', delete_after=15)

    @commands.command(help="Stop the current playing song.")
    async def stop(self, ctx: commands.Context):
        """Stop the player and clear all internal states."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if self.is_privileged(ctx):
            em = discord.Embed(description=f"<:greenTick:596576670815879169> **{ctx.author.name}** has stopped the player.", color = 0xffcff1)
            await ctx.send(embed=em, delete_after=10)
            return await player.teardown()

        if ctx.author in player.stop_votes:
            return await ctx.send(f"<:redTick:596576672149667840> {ctx.author.mention}, you have already voted to stop.")

        required = self.required(ctx)
        player.stop_votes.add(ctx.author)

        if len(player.stop_votes) >= required:
            await ctx.send(f'<:greenTick:596576670815879169> Reached **{required}** votes, stopping the player.', delete_after=10)
            await player.teardown()
        else:
            await ctx.send(f'<:greenTick:596576670815879169> {ctx.author.mention} has voted to stop the player.', delete_after=15)

    @commands.command(help="Set/change the volume of the current player.",aliases=['vol'])
    async def volume(self, ctx: commands.Context, *, vol: int=None):
        """Change the players volume, between 1 and 250."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if not vol:
            em = discord.Embed(description=f"🌹 Player volume is **`{player.volume}%`**", color = 0xffcff1)
            return await ctx.send(embed=em, delete_after=10)

        if not self.is_privileged(ctx):
            return await ctx.send('<:redTick:596576672149667840> Only the **DJ** or **admins** may change the volume.')

        if not 0 < vol < 251:
            return await ctx.send('<:redTick:596576672149667840> Volume must be between **1** and **250**')

        await player.set_volume(vol)
        await ctx.message.add_reaction('✅')

    @commands.command(help="Shuffle the songs in the queue.", aliases=['mix'])
    async def shuffle(self, ctx: commands.Context):
        """Shuffle the players queue."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if player.queue.qsize() < 3:
            return await ctx.send(f'<:redTick:596576672149667840> You may need at least **`3`** songs into the queue, **`{player.queue.qsize()}`** are in the queue.', delete_after=15)

        if self.is_privileged(ctx):
            await ctx.send('<:greenTick:596576670815879169> An **admin** or **DJ** has shuffled the playlist.', delete_after=10)
            player.shuffle_votes.clear()
            return random.shuffle(player.queue._queue)

        if ctx.author in player.shuffle_votes:
            return await ctx.send(f"<:redTick:596576672149667840> {ctx.author.mention}, you have already voted to shuffle.")

        required = self.required(ctx)
        player.shuffle_votes.add(ctx.author)

        if len(player.shuffle_votes) >= required:
            await ctx.send('<:greenTick:596576670815879169> Vote to shuffle passed. Shuffling the playlist.', delete_after=10)
            player.shuffle_votes.clear()
            random.shuffle(player.queue._queue)
        else:
            await ctx.send(f'<:greenTick:596576670815879169> {ctx.author.mention} has voted to shuffle the playlist.', delete_after=15)

    @commands.command(help="Set the equalizer, a filter for the current playing song.\nSet the `[equalizer]` argument as `list` to see all available equalizers.\nLeave `[equalizer]` blank to reset the base equalizer.", aliases=['eq'])
    async def equalizer(self, ctx: commands.Context, *, equalizer: str=None):
        """Change the players equalizer."""
        if equalizer == None:
            equalizer = "base"

        if equalizer == "list":
            em = discord.Embed(title="Equalizers list", description="`base` : Base equalizer, standard sound.\n"
                                           "`bass` : Optimal for songs with high 808.\n"
                                           "`metal` : High reveerb on voice, optimal for singed songs.\n"
                                           "`piano` : Perfect for chilling, works well with voice.\n"
                                           "`rave` : Optimal for psytrance / acid.", color = 0xffcff1)
            em.set_footer(text="The equalizer can take up to 5 seconds to set.")
            return await ctx.send(embed=em)
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return await ctx.reply("<:redTick:596576672149667840> Not playing anything at the moment.")

        if not self.is_privileged(ctx):
            return await ctx.send('<:redTick:596576672149667840> Only the **DJ** or **admins** may change the equalizer.')

        eqs = {'base': wavelink.Equalizer.flat(),
               'bass': wavelink.Equalizer.boost(),
               'metal': wavelink.Equalizer.metal(),
               'piano': wavelink.Equalizer.piano(),
               'rave': wavelink.Equalizer.build(levels = [(0, -0.295), (1, .150), (2, .150), (3, .1), (4, .1),
                  (5, .05), (6, 0.075), (7, .0), (8, .0), (9, .0),
                  (10, .0), (11, .0), (12, .125), (13, .15), (14, .05)], name="RaveEQ")}

        eq = eqs.get(equalizer.lower(), None)

        if not eq:
            joined = ", ".join(eqs.keys())
            em = discord.Embed(title="<:redTick:596576672149667840> Invalid EQ provided.", description=f"You've provided an invalid equalizer, available equalizers are:\n**`{joined}`**", color = 0xffcff1)
            return await ctx.send(embed=em)

        em = discord.Embed(description=f"<:greenTick:596576670815879169> {ctx.author.mention} has set the equalizer to **`{equalizer}`**.", color = 0xffcff1)
        await ctx.send(embed=em, delete_after=15)
        await player.set_eq(eq)


    @commands.command(help="Remove a song from the queue using the song number in queue.\nIf `[queue_numbr]` not specified, it will remove the first song.")
    async def remove(self, ctx: commands.Context, queue_number: int=1):
        """Remove a song from the queue"""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if player.queue.qsize() == 0:
            return await ctx.send('<:redTick:596576672149667840> The queue is empty.', delete_after=15)

        if not self.is_privileged(ctx):
            return await ctx.send('<:redTick:596576672149667840> Only the **DJ** or **admins** may remove songs from the queue.')

        del player.queue._queue[queue_number-1]  # Account for 0-index.

        await ctx.reply(f'<:greenTick:596576670815879169> Removed song #**{queue_number}** from the queue.', delete_after=5)

    @commands.command(help="Move the player seek to the given position (in seconds).\nIf seek is not specified, it set the seek to 0")
    async def seek(self, ctx: commands.Context, seek_number: int = None):
        """Set the seek position for the current playing song.
        This must be an int or float, raise SeekErrorNotValid if <seek_number> invalid."""

        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if seek_number == None:
            seek_number = 0

        if not self.is_privileged(ctx):
            return await ctx.send('<:redTick:596576672149667840> Only the **DJ** or **admins** may move the seek of the song.')

        if seek_number > int(player.current.length):
            return await ctx.send(f"<:redTick:596576672149667840> Seek can't be more than the track lenght (`{int(player.current.length)}`).", delete_after=15)

        seeky = seek_number*1000
        scd = "{}".format(humanize.precisedelta(seek_number))
        await player.seek(seeky)
        em = discord.Embed(description=f"<:greenTick:596576670815879169> Player seek moved to **{scd}**", color = 0xffcff1)
        await ctx.send(embed=em, delete_after=5)


    @commands.command(help="See the current song queue.", aliases=['q', 'que'])
    async def queue(self, ctx: commands.Context):
        """Display the players queued songs."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return await ctx.send("<:redTick:596576672149667840> Not connected to any voice channel.")

        if self.queue.qsize() == 0:
            return await ctx.send('<:redTick:596576672149667840> The queue is empty.', delete_after=15)

        entries = [f"[{track.title}]({track.uri})" for track in player.queue._queue]
        pages = PaginatorSource(entries=entries)
        paginator = menus.MenuPages(source=pages, timeout=None, delete_message_after=True)

        await paginator.start(ctx)

    @commands.command(help="Check what'im playing right now.", aliases=['np', 'now_playing', 'current'])
    async def nowplaying(self, ctx: commands.Context):
        """Update the player controller."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return await ctx.send("<:redTick:596576672149667840> Nothing playing at the moment.")

        await ctx.send(embed=player.build_embed())

    @commands.command(help="Swap the song DJ to another member.\nIf member not specified, it choose a random member in the voice channel.\nIf the members in the vc are 2 or less, the dj can't be swapped without member specified.", aliases=['swap'])
    async def swap_dj(self, ctx: commands.Context, *, member: discord.Member = None):
        """Swap the current DJ to another member in the voice channel."""
        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.is_connected:
            return

        if not self.is_privileged(ctx):
            return await ctx.send('<:redTick:596576672149667840> Only **admins** and the **DJ** may swap the dj.', delete_after=15)

        members = self.bot.get_channel(int(player.channel_id)).members

        if member and member not in members:
            return await ctx.send(f'<:redTick:596576672149667840> {member} is not in the voice channel.', delete_after=15)

        if member and member == player.dj:
            return await ctx.send("<:redTick:596576672149667840> Can't give **DJ** to the current **DJ**.", delete_after=15)

        if len(members) <= 2:
            return await ctx.send('<:redTick:596576672149667840> No more members for **auto-swap**.', delete_after=15)

        if member:
            player.dj = member
            em = discord.Embed(description=f"<:greenTick:596576670815879169> {ctx.author.mention} has gave the **DJ** to {member.mention}.", color = 0xffcff1)
            return await ctx.send(embed=em, delete_after = 15)

        for m in members:
            if m == player.dj or m.bot:
                continue
            else:
                player.dj = m
                return await ctx.send(f'<:greenTick:596576670815879169> {member.mention} is now the **DJ**.')


    @commands.command(help="Loop the current playing song to make me play it in loop!\nWorks in bool, send 1 time this command to loop, resend to unloop.")
    async def loop(self, ctx: commands.Context):

        player: Player = self.bot.wavelink.get_player(guild_id=ctx.guild.id, cls=Player, context=ctx)

        if not player.current:
            return await ctx.send('<:redTick:596576672149667840> Nothing is playing right now!')

        if self.is_privileged(ctx):
            if not player.looped:
                player.looped = True
                player.looped_track = player.current
                em = discord.Embed(description=f"<:greenTick:596576670815879169> {ctx.author.mention} has enabled the **loop** for `{player.current}`.", color = 0xffcff1)
                return await ctx.send(embed=em, delete_after=10)
            else:
                player.looped = False
                player.looped_track = None
                em = discord.Embed(description=f"<:greenTick:596576670815879169> {ctx.author.mention} has disabled the **loop** for `{player.current}`.", color = 0xffcff1)
                return await ctx.send(embed=em, delete_after=10)

        if ctx.author in player.loop_votes:
            return await ctx.send(f"<:redTick:596576672149667840> {ctx.author.mention}, you have already voted to loop.")

        required = self.required(ctx)
        player.loop_votes.add(ctx.author)

        if len(player.loop_votes) >= required:
            if not player.looped:
                await ctx.send(f'<:greenTick:596576670815879169> Reached {required} votes to loop. Looping player.', delete_after=10)
                player.loop_votes.clear()
            else:
                await ctx.send(f'<:greenTick:596576670815879169> Reached {required} votes to unloop. Unlooping player.', delete_after=10)
                player.loop_votes.clear()
        else:
            if not player.looped:
                await ctx.send(f'<:greenTick:596576670815879169> {ctx.author.mention} has voted to loop the player.', delete_after=15)
            else:
                await ctx.send(f'<:greenTick:596576670815879169> {ctx.author.mention} has voted to unloop the player.', delete_after=15)

def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))

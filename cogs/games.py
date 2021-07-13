import discord
from discord.ext import commands, tasks
import random
import asyncio


class TicTacToe:
    """
    Represents a game of Tic-tac-toe
    """

    EMOJI_X = '<:cross:855540891841331210>'
    EMOJI_O = '<:circle:855540891753644104>'
    CROSSMARK = '<:4318crossmark:848857812565229601>'

    NUMBERS = [
        None,  # Shift so indicies are correct
        ':one:',
        ':two:',
        ':three:',
        ':four:',
        ':five:',
        ':six:',
        ':seven:',
        ':eight:',
        ':nine:'
    ]

    def __init__(self, ctx: commands.Context, opponent: discord.Member) -> None:
        self.ctx = ctx
        self.player = ctx.author
        self.opponent = opponent
        self.is_player_turn = bool(random.randint(0, 1))

        # 1 is O, 2 is X
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

        self.message = None

    async def render_and_send(self, only_board:bool=False):
        i = 0
        message = ''
        for row in self.board:
            for cell in row:
                i += 1
                if cell == 1:
                    message += self.EMOJI_O
                elif cell == 2:
                    message += self.EMOJI_X
                else:
                    message += self.NUMBERS[i]

                message += ''
            message += '\n'

        turn, emoji = (self.player, self.EMOJI_O) if self.is_player_turn else (self.opponent, self.EMOJI_X)
        if only_board:
            return await self.ctx.send(message)

        message = f'{turn.mention}, it\'s your turn! {emoji}\n{message}'

        if not self.message or not await self.is_in_last_messages():
            self.message = res = await self.ctx.send(message)
            return res

        return await self.message.edit(content=message)


    async def is_in_last_messages(self):
        """Method which checks if our board is in last 5 messages."""
        return await self.ctx.channel.history(limit=5).get(id=self.message.id)

    async def move(self, position: int):
        x, y = divmod(position - 1, 3)
        if self.board[x][y] != 0:
            return await self.ctx.send(f'{self.CROSSMARK} Someone has already went there.')

        symbol = 1 if self.is_player_turn else 2
        self.board[x][y] = symbol
        self.is_player_turn = not self.is_player_turn

        await self.render_and_send()

    @property
    def current_turn(self):
        return self.player if self.is_player_turn else self.opponent

    @property
    def winner(self):
        # Return 0 (no winner), 1, or 2
        # Return -1 if it is a tie

        # Horizontal
        for row in self.board:
            if row[0] == row[1] == row[2]:
                return row[0]

        # Vertical
        for i in range(3):
            if self.board[0][i] == self.board[1][i] == self.board[2][i]:
                return self.board[0][i]

        # Diagonal ascending
        if self.board[0][2] == self.board[1][1] == self.board[2][0]:
            return self.board[0][2]

        # Diagonal decending
        if self.board[0][0] == self.board[1][1] == self.board[2][2]:
            return self.board[0][0]

        # Tie
        if all(all(cell != 0 for cell in row) for row in self.board):
            return -1

        return 0


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Games Loaded")

    @commands.command(help="Play a rock-paper-scissors game against me and try to win!\nThis game requires you have a cuppy balance, you need to bet an amount of cupcakes to play >.>\nYou can bet maximum <:cupcake:845632403405012992> **100.000**, over this amount the game won't start.", aliases=["rps"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def rockpaperscissors(self, ctx, bet:int):
        db = await self.bot.db.fetch("SELECT * FROM users WHERE user_id = $1", str(ctx.author.id))
        if not db:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> {ctx.author.mention} you don't have a balance for cuppy, open one with `ami bal`.")

        balance = db[0]["wallet"]
        if bet > balance:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> {ctx.author.mention} you have <:cupcake:845632403405012992> **{balance}** in your wallet, you can't bet <:cupcake:845632403405012992> **{bet}**")

        if bet > 100000:
            return await ctx.send(f"<:4318crossmark:848857812565229601> {ctx.author.mention}, this game has a maximum bet of <:cupcake:845632403405012992> **100.000**, you can't bet <:cupcake:845632403405012992> **{bet}**")

        msg = await ctx.send(embed=discord.Embed(
                            title = "RPS Game Started!",
                            description=f"{ctx.author.mention} there you go, choose a move using reactions!\n\n"
                            "👊 : Rock\n✌ : Scissors\n🖐 : Paper",
                            color = 0xffcff1))

        await msg.add_reaction("👊")
        await msg.add_reaction("✌")
        await msg.add_reaction("🖐")

        emojis = ["🖐", "✌", "👊"]

        def check(payload):
            return payload.message_id == msg.id and payload.emoji.name in emojis and payload.user_id == ctx.author.id

        try:
            payload = await self.bot.wait_for("raw_reaction_add", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            return await msg.delete()

        if payload.emoji.name in emojis:
            move_author = payload.emoji.name
        bot_move = random.choice(["🖐", "✌", "👊"])

        winner = None
        if bot_move == move_author or move_author == bot_move:
            winner = f"<:4318crossmark:848857812565229601> That's a draw, better luck next time dude.\n:one: **{ctx.author.name}** : {move_author}\n:two: **{ctx.me.name}** : {bot_move}"

        elif bot_move == "🖐" and move_author == "👊" or bot_move == "✌" and move_author == "🖐" or bot_move == "👊" and move_author == "✌":
            winner = f"<:4318crossmark:848857812565229601> {ctx.me.mention} has won dude, you lost the game and lost <:cupcake:845632403405012992> **{bet}**!\n:one: **{ctx.author.name}** : {move_author}\n:two: **{ctx.me.name}** : {bot_move}"
            await self.bot.db.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", db[0]["wallet"] - bet, str(ctx.author.id))

        elif move_author == "🖐" and bot_move == "👊" or move_author == "✌" and bot_move == "🖐" or move_author == "👊" and bot_move == "✌":
            winner = f"<:4430checkmark:848857812632076314> {ctx.author.mention} you won dude! You got <:cupcake:845632403405012992> **{bet}**!\n:one: **{ctx.author.name}** : {move_author}\n:two: **{ctx.me.name}** : {bot_move}"
            await self.bot.db.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", db[0]["wallet"] + bet, str(ctx.author.id))

        await msg.delete()

        msg2 = await ctx.send("<a:eyeshaking:819703490342289474> Picking the winner...")
        await asyncio.sleep(4)

        await msg2.edit(content=winner)

    @commands.command(aliases=["ttt"], help="Play a fun tictactoe game with bet your <:cupcake:845632403405012992>!\nThe winner gets as reward the **bet placed * 2** (one from his balance, and one from the opponent balance), example: if you bet **35000**, who wins get **70000** (__35k__ are from his balance and __35k__ from opponent balance)\nIf the game ends as draw, no <:cupcake:845632403405012992> will be taken from eithers balances.")
    async def tictactoe(self, ctx, opponent: discord.Member, bet: int):
        if opponent == ctx.author:
            return await ctx.send("<:4318crossmark:848857812565229601> You can't play against yourself.")

        db2 = await self.bot.db.fetch("SELECT * FROM users WHERE user_id = $1", str(opponent.id))
        if not db2:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> {ctx.author.mention} looks like **{opponent.name}** doesn't have a balance, so they can't play.")

        db = await self.bot.db.fetch("SELECT * FROM users WHERE user_id = $1", str(ctx.author.id))
        if not db:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> {ctx.author.mention} you don't have a balance for cuppy, open one with `ami bal`.")

        balance = db[0]["wallet"]
        balance2 = db2[0]["wallet"]
        if bet > balance:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> {ctx.author.mention} you have <:cupcake:845632403405012992> **{balance}** in your wallet, you can't bet <:cupcake:845632403405012992> **{bet}**")

        if bet > balance2:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> **{opponent.name}** does not have <:cupcake:845632403405012992> **{bet}** in their wallet, they can't bet <:cupcake:845632403405012992> **{bet}**")

        if bet <= 0:
            return await ctx.send("<:4318crossmark:848857812565229601> You can't bet negative amounts.")

        message = await ctx.send(
            f"{opponent.mention}, you got an invite to play a `TicTacToe` game from **{ctx.author.name}** with <:cupcake:845632403405012992> "
            f"**{bet*2}** for the __winner__: click <:4318crossmark:848857812565229601> to `decline` or <:4430checkmark:848857812632076314> to `accept` in **60** seconds.")
        await message.add_reaction("<:4318crossmark:848857812565229601>")
        await message.add_reaction("<:4430checkmark:848857812632076314>")

        emojis = ["4318crossmark", "4430checkmark"]

        def check(payload):
            return payload.message_id == message.id and payload.emoji.name in emojis and payload.user_id == opponent.id

        try:
            payload = await self.bot.wait_for("raw_reaction_add", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> {ctx.author.mention}, looks like **{opponent.name}** is away or it didn't see the invite.")

        if payload.emoji.name == "4318crossmark":
            await message.delete()
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{opponent.name}** has refused to play.")

        await message.delete()
        mcd = await ctx.send("<:4430checkmark:848857812632076314> Picking who goes first...")
        await asyncio.sleep(3)
        await mcd.delete()

        game = TicTacToe(ctx, opponent)
        msg2 = await game.render_and_send()

        while True:
            try:
                msg = await self.bot.wait_for('message', check=lambda
                    message: message.author.id == game.current_turn.id and message.channel == ctx.channel, timeout=180.0)
            except asyncio.TimeoutError:
                return await ctx.send(
                    f"<:4318crossmark:848857812565229601> {game.current_turn.name} took too long to choose a position, stopping the game.")

            if msg.content.isdigit():
                valids = [0, 1, 2, 3, 4, 5, 6, 7, 8]
                if int(msg.content) - 1 not in valids:
                    return

                await game.move(int(msg.content))

                winner = game.winner
                if winner != 0:
                    await game.message.delete()
                    if winner == 1:
                        await self.bot.db.execute("UPDATE users SET wallet = $1 WHERE user_id = $2",
                                                      db[0]["wallet"] + bet*2, str(ctx.author.id))
                        await self.bot.db.execute("UPDATE users SET wallet = $1 WHERE user_id = $2",
                                                      db[0]["wallet"] - bet, str(opponent.id))
                        await ctx.send(
                            f"👑 {ctx.author.mention} has won the game, they got <:cupcake:845632403405012992> **{bet*2}**!")
                        await game.render_and_send(True)
                        break
                    elif winner == 2:
                        await self.bot.db.execute("UPDATE users SET wallet = $1 WHERE user_id = $2",
                                                      db[0]["wallet"] - bet, str(ctx.author.id))
                        await self.bot.db.execute("UPDATE users SET wallet = $1 WHERE user_id = $2",
                                                      db[0]["wallet"] + bet*2, str(opponent.id))
                        await ctx.send(
                            f"👑 {opponent.mention} has won the game, they got <:cupcake:845632403405012992> **{bet*2}**!\n")
                        await game.render_and_send(True)
                        break
                    elif winner == -1:
                        await ctx.send("<:4318crossmark:848857812565229601> It's a draw, good game.")
                        await game.render_and_send(True)
                        break


def setup(bot):
    bot.add_cog(Games(bot))

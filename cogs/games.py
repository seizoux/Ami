import discord
from discord.ext import commands, tasks
import random
import asyncio



class Blackjack:
    """
    Represents a game of Blackjack
    """

    SYMBOL_1 = "♠"
    SYMBOL_2 = "♣"
    SYMBOL_3 = "♥"
    SYMBOL_4 = "♦"

    ACTIONS = ["`hit` : Pick a new card", "`stand` : Stop, don't pick anything else", "`double` : Double your bet and pick a last card", "`surrender` : Give up, clear your hand and get back 1/2 of your bet."]
    ACTIONS_NAMES = ["hit", "stand", "double", "surrender"]

    def __init__(self, ctx: commands.Context, opponent: discord.Member) -> None:
        self.ctx = ctx
        self.player = ctx.author
        self.opponent = opponent

        self.is_player_turn = bool(random.randint(0, 1))

        self.points_author = 0
        self.points_opponent = 0

        self.is_standing_author = False
        self.is_standing_opponent = False

        self.has_doubled_author = False
        self.has_doubled_opponent = False

        self.bet = 0

        self.max_rounds = 4

        self.cards = None

        self.message = None

    async def last_mexs(self):
        """Method which checks if our message is in last 5 messages."""
        return await self.ctx.channel.history(limit=5).get(id=self.message.id)

    async def update_and_send(self, no_edit:bool=False, same_turn:bool=False): 
        turn = self.player if self.is_player_turn else self.opponent
        if same_turn:
            turn = self.player if self.is_player_turn else self.opponent

        message = f"{self.opponent.mention} : `{self.points_opponent}`\n{self.player.mention} : `{self.points_author}`"

        if no_edit:
            return await self.ctx.send(message)

        choiches = '\n'.join(self.ACTIONS)
        message = f"🃏 {turn.mention}, is your turn.\n\n**{self.opponent.name}** : `{self.points_opponent}`\n**{self.player.name}** : `{self.points_author}`\n\nChoose what to do:\n{choiches}"

        if not self.message or not await self.last_mexs():
            self.max_rounds = self.max_rounds + 1
            self.message = res = await self.ctx.send(message)
            return res

        if self.is_standing_author or self.is_standing_opponent:
            if self.max_rounds != 4 or self.max_rounds != 3:
                self.max_rounds = 3
    
        if self.has_doubled_author or self.has_doubled_opponent:
            if self.max_rounds != 4 or self.max_rounds != 3:
                self.max_rounds = 3

        return await self.message.edit(content=message)

    async def do_action(self, action:str):
        if action.lower() not in self.ACTIONS_NAMES:
            await self.ctx.send(f"`{action}` is not a valid action.")
            return await self.update_and_send(False, True)

        self.max_rounds = self.max_rounds + 1

        if action.lower() == "hit":
            turn = self.player if self.is_player_turn else self.opponent

            if turn.id == self.player.id:
                self.points_author = self.points_author + random.randint(1, 10)

            elif turn.id == self.opponent.id:
                self.points_opponent = self.points_opponent + random.randint(1, 10)

            await self.update_and_send()

        elif action.lower() == "stand":
            turn = self.player if self.is_player_turn else self.opponent

            if turn.id == self.player.id:
                self.is_standing_author = True

            elif turn.id == self.opponent.id:
                self.is_standing_opponent = True

            await self.update_and_send()

        elif action.lower() == "double":
            self.bet = self.bet + self.bet/2

            turn = self.player if self.is_player_turn else self.opponent

            if turn.id == self.player.id:
                self.has_doubled_author = True

            elif turn.id == self.opponent.id:
                self.has_doubled_opponent = True

            await self.update_and_send()

        elif action.lower() == "surrender":
            await self.surrended_player()

        self.is_player_turn = not self.is_player_turn

        await self.update_and_send()

    async def surrended_player(self):
        turn = self.player if self.is_player_turn else self.opponent
        return await self.ctx.send(f"🎲 {turn.mention} has gave up, giving back 1/2 of the game bet.")


    async def end_game(self, the_winner : discord.Member):
        return await self.ctx.send(f"🎲 {the_winner.mention} has won, they got <:cupcake:845632403405012992> **{self.bet}**")


    @property
    def is_right_turn(self):
        return self.player if self.is_player_turn else self.opponent

    @property
    def check_winner(self):

        if self.max_rounds == 4:
            if self.points_author >= 21:
                return 0 #over author

            if self.points_opponent >= 21:
                return 1 #over oppoent 
                    
            if self.points_opponent == self.points_author:
                return 2 #tie

            if self.points_author > self.points_opponent or self.points_opponent > self.points_author:
                return 3 #winner 

        return -1 #nothing / tie end rounds


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

    @commands.command()
    async def blackjack(self, ctx, opponent: discord.Member, bet: int):
        db2 = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", str(opponent.id))
        if not db2:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> {ctx.author.mention} looks like **{opponent.name}** doesn't have a balance, so they can't play.")

        db = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", str(ctx.author.id))
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
            f"{opponent.mention}, you got an invite to play a `Blackjack` game from **{ctx.author.name}** with <:cupcake:845632403405012992> "
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

        game = Blackjack(ctx, opponent)
        game.bet = bet*2
        msg2 = await game.update_and_send()        

        while True:
            try:
                msg = await self.bot.wait_for('message', check=lambda
                    message: message.author.id == game.is_right_turn.id and message.channel == ctx.channel, timeout=180.0)
            except asyncio.TimeoutError:
                return await ctx.send(f"<:4318crossmark:848857812565229601> {game.is_right_turn.name} took too long to choose, stopping the game.")

            await game.do_action(msg.content)

            turn = game.player if not game.is_player_turn else game.opponent
            if turn.id == ctx.author.id:
                final_points = game.points_author
            else:
                final_points = game.points_opponent

            winner = game.check_winner
            if winner != -1:
                if winner == 0 or winner == 1:
                    db = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", str(turn.id))
                    await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", db[0]["wallet"] - game.bet/2, str(turn.id))
                    await ctx.send(f"🥈 {turn.name} has `{final_points}`, he lost <:cupcake:845632403405012992> **{game.bet/2}**")
                    await game.update_and_send(True)
                    break

                elif winner == 3:
                    turn_s = game.player if not game.is_player_turn else game.opponent
                    await game.end_game(turn_s)
                    break

                elif game.max_rounds == 4:
                    if winner == 2:
                        await ctx.send(f"🔮 **{game.player.name}** & **{game.opponent.name}** game finished as a tie.")
                        await game.update_and_send(True)
                        break

    @commands.command(aliases=["ttt"], help="Play a fun tictactoe game with bet your <:cupcake:845632403405012992>!\nThe winner gets as reward the **bet placed * 2** (one from his balance, and one from the opponent balance), example: if you bet **35000**, who wins get **70000** (__35k__ are from his balance and __35k__ from opponent balance)\nIf the game ends as draw, no <:cupcake:845632403405012992> will be taken from eithers balances.")
    async def tictactoe(self, ctx, opponent: discord.Member, bet: int):
        db2 = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", str(opponent.id))
        if not db2:
            return await ctx.send(
                f"<:4318crossmark:848857812565229601> {ctx.author.mention} looks like **{opponent.name}** doesn't have a balance, so they can't play.")

        db = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", str(ctx.author.id))
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
                        await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2",
                                                      db[0]["wallet"] + bet*2, str(ctx.author.id))
                        await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2",
                                                      db[0]["wallet"] - bet, str(opponent.id))
                        await ctx.send(
                            f"👑 {ctx.author.mention} has won the game, they got <:cupcake:845632403405012992> **{bet*2}**!")
                        await game.render_and_send(True)
                        break
                    elif winner == 2:
                        await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2",
                                                      db[0]["wallet"] - bet, str(ctx.author.id))
                        await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2",
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

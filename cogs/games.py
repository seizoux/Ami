import discord
from discord.ext import commands, tasks
import random
import asyncio

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.player1 = 0
        self.player2 = 0
        self.turn = 0
        self.gameOver = True

        self.board = []

        self.winningConditions = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [0, 4, 8],
            [2, 4, 6]
        ]

    @commands.Cog.listener()
    async def on_ready(self):
        print("Games Loaded")

    @commands.command(aliases=["ttt"])
    async def tictactoe(self, ctx, opponent: discord.Member, bet:int):

        if self.gameOver is False:
            self.gameOver = True

        db2 = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", str(opponent.id))
        if not db2:
            return await ctx.send(f"<:4318crossmark:848857812565229601> {ctx.author.mention} looks like **{opponent.name}** doesn't have a balance, so he/she can't play.")

        db = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", str(ctx.author.id))
        if not db:
            return await ctx.send(f"<:4318crossmark:848857812565229601> {ctx.author.mention} you don't have a balance for cuppy, open one with `ami bal`.")

        balance = db[0]["wallet"]
        if bet > balance:
            return await ctx.send(f"<:4318crossmark:848857812565229601> {ctx.author.mention} you have <:cupcake:845632403405012992> **{balance}** in your wallet, you can't bet <:cupcake:845632403405012992> **{bet}**")

        if self.gameOver:
            self.board = [":one:", ":two:", ":three:\n",
                    ":four:", ":five:", ":six:\n",
                    ":seven:", ":eight:", ":nine:"]
            self.turn = 0
            self.gameOver = False
            count = 0

            message = await ctx.send(f"{opponent.mention}, you got an invite to play a `TicTacToe` game from **{ctx.author.name}** with <:cupcake:845632403405012992> **{bet}** for the __winner__: click <:4318crossmark:848857812565229601> to `decline` or <:4430checkmark:848857812632076314> to `accept` in **60** seconds.")
            await message.add_reaction("<:4318crossmark:848857812565229601>")
            await message.add_reaction("<:4430checkmark:848857812632076314>")

            emojis = ["4318crossmark", "4430checkmark"]

            def check(payload):
                return payload.message_id == message.id and payload.emoji.name in emojis and payload.user_id == opponent.id

            try: 
                payload = await self.bot.wait_for("raw_reaction_add", check=check, timeout=60.0)
            except asyncio.TimeoutError:
                return await ctx.send(f"<:4318crossmark:848857812565229601> {ctx.author.mention}, looks like **{opponent.name}** is away or it didn't see the invite.")

            if payload.emoji.name == "4318crossmark":
                await message.delete()
                return await ctx.send(f"<:4318crossmark:848857812565229601> **{opponent.name}** has refused to play.")

            await message.delete()
            mcd = await ctx.send("<:4430checkmark:848857812632076314> Picking who goes first...")
            await asyncio.sleep(3)
            await mcd.delete()

            self.player1 = ctx.author
            self.player2 = opponent

            turn_emojis = {
                self.player1.id: "<:4430checkmark:848857812632076314>",
                self.player2.id: "<:4318crossmark:848857812565229601>"
            }

            # determine who goes first
            num = random.randint(1, 2)
            if num == 1:
                self.turn = self.player1
            elif num == 2:
                self.turn = self.player2

            msg2 = await ctx.send(f"{self.turn.mention} is your turn! {turn_emojis[int(self.turn.id)]}\n{''.join(self.board)}")

            while True:
                try:
                    msg = await self.bot.wait_for('message', check=lambda message: message.author.id == self.turn.id and message.channel == ctx.channel, timeout=180.0)
                except asyncio.TimeoutError:
                    return await ctx.send(f"<:4318crossmark:848857812565229601> {self.turn.name} took too long to choose a position, stopping the game.")
            
                if msg.content.isdigit():
                    valids = [0,1,2,3,4,5,6,7,8]
                    if int(msg.content)-1 not in valids:
                        return
                    
                    if self.board[int(msg.content)-1] in emojis:
                        return

                    if self.board[int(msg.content)-1]:
                        count += 1

                        sides = [2,5]

                        if int(msg.content) - 1 in sides:
                            self.board[int(msg.content)-1] = f"{turn_emojis[int(self.turn.id)]}\n"
                        else:
                            self.board[int(msg.content)-1] = f"{turn_emojis[int(self.turn.id)]}"

                    extra_turn = self.player1 if self.turn.id != self.player1.id else self.player2

                    async def is_in_last_messages(mex):
                        """Method which checks if our board is in last 5 messages."""
                        return await ctx.channel.history(limit=5).get(id=mex.id)

                    if not await is_in_last_messages(msg2):
                        try:
                            await msg2.delete()
                        except Exception:
                            pass

                        msg2 = await ctx.send(f"{extra_turn.mention} is your turn! {turn_emojis[int(self.turn.id)]}\n{''.join(self.board)}")

                    else:
                        await msg2.edit(content=f"{extra_turn.mention} is your turn! {turn_emojis[int(self.turn.id)]}\n{''.join(self.board)}")

                    def checkWinner(winningConditions, mark):
                        for condition in winningConditions:
                            if self.board[condition[0]] == mark and self.board[condition[1]] == mark and self.board[condition[2]] == mark:
                                self.gameOver = True

                    checkWinner(self.winningConditions, turn_emojis[self.turn.id])
                    if self.gameOver == True:
                        if ctx.author.id == self.turn.id:
                            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", db[0]["wallet"] + bet, str(ctx.author.id))
                            await ctx.send(self.turn.mention + f" has won the game, he/she got the <:cupcake:845632403405012992> **{bet}**!")
                            break
                        elif opponent.id == self.turn.id:
                            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", db[0]["wallet"] - bet, str(ctx.author.id))
                            await self.bot.pg_con.execute("UPDATE users SET wallet = $1 WHERE user_id = $2", db[0]["wallet"] + bet, str(opponent.id))
                            await ctx.send(self.turn.mention + f" has won the game, he/she got the <:cupcake:845632403405012992> **{bet}**!")
                            break
                    elif count >= 9:
                        self.gameOver = True
                        await ctx.send("<:4318crossmark:848857812565229601> It's a fucking draw.")
                        break

                    self.gameOver = False
                    self.turn = self.player1 if self.turn != self.player1 else self.player2
                else:
                    pass
def setup(bot):
    bot.add_cog(Games(bot))

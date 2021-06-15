import discord
from discord.ext import commands, tasks
import random
import asyncio

player1 = ""
player2 = ""
turn = ""
gameOver = True

board = []

winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
]

def checkWinner(winningConditions, mark):
    global gameOver
    for condition in winningConditions:
        if board[condition[0]] == mark and board[condition[1]] == mark and board[condition[2]] == mark:
            gameOver = True

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Games Loaded")

    @commands.command(aliases=["ttt"])
    async def tictactoe(self, ctx, opponent: discord.Member):
        global count
        global player1
        global player2
        global turn
        global gameOver

        if gameOver:
            global board
            board = [":one:", ":two:", ":three:",
                    ":four:", ":five:", ":six:",
                    ":seven:", ":eight:", ":nine:"]
            turn = ""
            gameOver = False
            count = 0

            message = await ctx.send(f"{opponent.mention}, you got an invite to play a `Tic Tac Toe` game from **{ctx.author.name}**: click <:4318crossmark:848857812565229601> to `decline` or <:4430checkmark:848857812632076314> to `accept` in **60** seconds.")
            await message.add_reaction("<:4318crossmark:848857812565229601>")
            await message.add_reaction("<:4430checkmark:848857812632076314>")

            emojis = ["4318crossmark", "4430checkmark"]

            def check(payload):
                return payload.message_id == message.id and payload.emoji.name in emojis and payload.user_id == opponent.id

            try: 
                await self.bot.wait_for("raw_reaction_add", check=check, timeout=60.0)
            except asyncio.TimeoutError:
                return await ctx.send(f"<:4318crossmark:848857812565229601> Looks like **{opponent.name}** is away or it declined the invite.")

            await message.delete()
            mcd = await ctx.send("<:4430checkmark:848857812632076314> Picking who goes first...")
            await asyncio.sleep(3)
            await mcd.delete()

            player1 = ctx.author
            player2 = opponent

            # determine who goes first
            num = random.randint(1, 2)
            if num == 1:
                turn = player1
                await ctx.send("It is <@" + str(player1.id) + ">'s turn.")
            elif num == 2:
                turn = player2
                await ctx.send("It is <@" + str(player2.id) + ">'s turn.")

            # print the board
            line = ""
            for x in range(len(board)):
                if x == 2 or x == 5 or x == 8:
                    line += " " + board[x]
                    await ctx.send(line)
                    line = ""
                else:
                    line += " " + board[x]

        while True:
            try:
                msg = await self.bot.wait_for('message', check=lambda message: message.author.id == turn.id and message.channel == ctx.channel, timeout=180.0)
            except asyncio.TimeoutError:
                await ctx.send("<:4318crossmark:848857812565229601> ")

            if not gameOver:
                if msg.content.isdigit():
                    mark = ""
                    if turn == ctx.author:
                        if turn == player1:
                            mark = "<:4318crossmark:848857812565229601>"
                        elif turn == player2:
                            mark = "<:4430checkmark:848857812632076314>"
                        
                        ccf = [":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:"]
                        if 0 < int(msg.content) < 10 and board[int(msg.content) - 1] in ccf :
                            board[int(msg.content) - 1] = mark
                            count += 1

                            # print the board
                            line = ""
                            for x in range(len(board)):
                                if x == 2 or x == 5 or x == 8:
                                    line += " " + board[x]
                                    await ctx.send(line)
                                    line = ""
                                else:
                                    line += " " + board[x]

                            checkWinner(winningConditions, mark)
                            print(count)
                            if gameOver == True:
                                await ctx.send(mark + " wins!")
                                break
                            elif count >= 9:
                                gameOver = True
                                await ctx.send("It's a draw.")
                                break

                            # switch turns
                            if turn == player1:
                                turn = player2
                            elif turn == player2:
                                turn = player1
                        else:
                            pass
                    else:
                        pass



def setup(bot):
    bot.add_cog(Games(bot))


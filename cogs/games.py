import discord
from discord.ext import commands, tasks
import random
import asyncio

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Games Loaded")


    @commands.command(aliases=["ttt"])
    async def tictactoe(self, ctx, bet:int, opponent: discord.Member):
        db = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", str(ctx.author.id))
        if not db:
            return await ctx.send("<:4318crossmark:848857812565229601> You can't play `tic tac toe` without a balance, open one with `ami bal`.")

        bal = db[0]["wallet"]
        if bet > bal:
            return await ctx.send(f"<:4318crossmark:848857812565229601> You have <:cupcake:845632403405012992> **{bal}**, you can't bet <:cupcake:845632403405012992> **{bet}**.")
        
        player1 = ctx.author
        player2 = opponent

        checky = await self.bot.pg_con.fetch("SELECT * FROM users WHERE user_id = $1", str(opponent.id))
        if not checky:
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{opponent.name}** doesn't have a balance.")

        message = await ctx.send(f"{opponent.mention}, you got an invite to play a `Tic Tac Toe` game from **{ctx.author.name}**: click <:4318crossmark:848857812565229601> to `decline` or <:4430checkmark:848857812632076314> to `accept` in **60** seconds.")
        await message.add_reaction("<:4318crossmark:848857812565229601>")
        await message.add_reaction("<:4430checkmark:848857812632076314>")

        emojis = ["4318crossmark", "4430checkmark"]

        def check(payload):
            return payload.message_id == message.id and payload.emoji.name in emojis and payload.user_id == opponent.id
            
        try: 
            await self.bot.wait_for("raw_reaction_add", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            return await ctx.send(f"<:alert:819704994612904017> Looks like **{opponent.name}** is away or it declined the invite.")

        await message.delete()
        dfd = await ctx.send("<:4430checkmark:848857812632076314> Picking who goes first...")
        start_turn = random.choice([player1,player2])
        await asyncio.sleep(3)
        await dfd.delete()

        symbols = {
            player1: "<:4430checkmark:848857812632076314>",
            player2: "<:4318crossmark:848857812565229601>"
        }

        mex = await ctx.send(f"{start_turn.mention} turn! {symbols[start_turn]}\n:one::two::three:\n:four::five::six:\n:seven::eight::nine:")

        positions = {
            1: "one",
            2: "two",
            3: "three",
            4: "four",
            5: "five",
            6: "six",
            7: "seven",
            8: "eight",
            9: "nine"
        }

        try:
            msg = await self.bot.wait_for('message', check=lambda message: message.author.id == start_turn.id and message.channel == ctx.channel, timeout=180.0)
        except asyncio.TimeoutError:
            return await ctx.send(f"<:4318crossmark:848857812565229601> **{start_turn.name}** didn't placed anything for over 180 seconds, stopping the game.")
        
        if int(msg.content) not in positions:
            return

        d = positions[int(msg.content)]
        f = mex.content.replace(f":{d}:", symbols[start_turn])
        await mex.edit(content=f)

         # HOW I CONTINUE HERE TO MAKE TURNS AND ENDS?
        

def setup(bot):
    bot.add_cog(Games(bot))

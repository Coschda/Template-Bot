import nextcord, os
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from dotenv import load_dotenv
load_dotenv()

ids = [int(x) for x in os.getenv("IDS").split(",")]

class ForfeitButton(nextcord.ui.Button):
    def __init__(self, y):
        super().__init__(style=nextcord.ButtonStyle.blurple, label="Forfeit", row=y)

    async def callback(self, interaction: Interaction):
        view : TicTacToe = self.view

        for child in view.children:
            child.disabled = True

        view.stop()
        if interaction.user == view.player1:
            await interaction.response.edit_message(content=f"{view.player2.mention} won by forfeit.", view=view)
        else:
            await interaction.response.edit_message(content=f"{view.player1.mention} won by forfeit.", view=view)


class TicTacToeButton(nextcord.ui.Button):
    def __init__(self, x: int, y: int):
        super().__init__(style=nextcord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: Interaction):
        assert self.view is not None
        view : TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X and interaction.user == view.player1:
            self.style = nextcord.ButtonStyle.danger
            self.label = "X"
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = f"It is now {view.player1.mention}'s turn"
        elif view.current_player == view.O and interaction.user == view.player2:
            self.style = nextcord.ButtonStyle.success
            self.label = "O"
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = f"It is now {view.player2.mention}'s turn"
        else:
            await interaction.send("Attends ton tour !", ephemeral=True)

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f"{view.player1.mention} won!"
            elif winner == view.O:
                content = f"{view.player2.mention} won!"
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)

class TicTacToe(nextcord.ui.View):
    X = -1
    O = 1
    Tie = 2

    def __init__(self, player1, player2):
        super().__init__()
        self.current_player = self.X
        self.player1 = player1
        self.player2 = player2
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))
        self.add_item(ForfeitButton(y+1))

    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        # Check tie 
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None

class Diver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(description="Jouez a TicTacToe !", guild_ids=ids)
    async def tictac(self, interaction : Interaction, player1 : nextcord.Member, player2 : nextcord.Member):
        await interaction.send(f"Tic Tac Toe entre {player1.mention} et {player2.mention}, c'est le tour de {player1.mention}", view=TicTacToe(player1, player2))

def setup(bot):
    bot.add_cog(Diver(bot))
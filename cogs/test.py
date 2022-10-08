import nextcord, os
from nextcord.ext import commands
from nextcord import Interaction
from dotenv import load_dotenv
load_dotenv()

ids = [int(x) for x in os.getenv("IDS").split(",")]

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(guild_ids=ids)
    async def test_input(self, interaction: Interaction):
        pass

    @nextcord.slash_command(guild_ids=ids)
    async def send_embed(self, interaction: Interaction, user: nextcord.Member):
        embed1 = nextcord.Embed(
            title="Hey!", 
            description= f"||{user.mention}||"
            )
        embed2 = nextcord.Embed(
            title="Hey!", 
            description= f"||{user.mention}||"
            )
        await interaction.send(embeds=[embed1, embed2], content="Hey")

def setup(bot):
    bot.add_cog(Test(bot))

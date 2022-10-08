import nextcord, os
from nextcord import Interaction
from nextcord.ext import commands
from dotenv import load_dotenv
load_dotenv()

#Environment variables
PREFIX = os.getenv("PREFIX")
COG_PATH = os.getenv("COG_PATH")
TOKEN = os.getenv("TOKEN")

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix = PREFIX, intents = intents)

#Cogs Recognition
#TODO C'est moche
for filename in os.listdir(COG_PATH):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

#all cogs commands.
@bot.command()
async def reload(inter: Interaction, extension):
   bot.unload_extension(f'cogs.{extension}')
   bot.load_extension(f'cogs.{extension}')
   print(f"Reloading {extension}...")
   await inter.send(f"Cog {extension} reloaded.")

@bot.event
async def on_ready():
    await bot.change_presence(status=nextcord.Status.dnd, activity=nextcord.Game("Lapis Lazuli"))
    print('Bot connecte.')

bot.run(TOKEN)
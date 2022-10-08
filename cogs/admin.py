import os
import nextcord
import asyncio
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

ids = [int(x) for x in os.getenv("IDS").split(",")]

def time2sec(time):
    # There is actually a library to make this whole thing easier, humanfriendly, but it would add a dependency.
    mult = {
        'ms': 0.001, 
        's': 1, 
        'm': 60, 
        'h': 3600, 
        'd': 86400, 
        'w': 604800, 
        'y': 31564000, 
    }

    nb = ''
    unit = ''
    for i in time:
        try:
            int(i)
            nb += i
        except:
                unit += i
    ftime = float(int(nb)*mult[unit])
    return ftime 

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="kick", description="Kick un membre du serveur", guild_ids=ids)
    @commands.has_permissions(kick_members = True)
    async def kick(self, inter : Interaction, member : nextcord.Member = SlashOption(description="Member to kick", required=True), *, reason=None):
        await member.kick(reason = reason)
        await inter.response.send_message(f'{member} a été kick.')

    @kick.error
    async def kick_err(self, inter: Interaction, error):
        if isinstance(error, nextcord.errors.Forbidden):
            await inter.send("Vous ou je n'ai pas les permissions requises.", ephemeral=True)
        else:
            raise error
    
    @nextcord.slash_command(name="ban", description="Ban un membre du serveur", guild_ids=ids)
    @commands.has_permissions(ban_members = True)
    async def ban(self, inter : Interaction, member : nextcord.Member = SlashOption(description="Member to ban", required=True), *, reason=None):
        await member.ban(reason = reason)
        await inter.response.send_message(f'{member} a été ban.')

    @ban.error
    async def ban_err(self, inter: Interaction, error):
        if isinstance(error, nextcord.errors.Forbidden):
            await inter.send("Vous ou je n'ai pas les permissions requises.", ephemeral=True)
        else:
            raise error

    @nextcord.slash_command(name="unban", description="Unban un membre du serveur", guild_ids=ids)
    @commands.has_permissions(ban_members=True)
    async def unban(self, inter : Interaction, member : nextcord.Member = SlashOption(description="Member to unban", required=True), *, reason=None):
        await member.unban(reason = reason)
        await inter.send(f'{member} a été unban.')

    @unban.error
    async def unban_err(self, inter: Interaction, error):
        if isinstance(error, nextcord.errors.Forbidden):
            await inter.send("Vous ou je n'ai pas les permissions requises.", ephemeral=True)
        else:
            raise error

    @nextcord.slash_command(name="tempban", description="Ban temporairement un membre du serveur", guild_ids=ids)
    @commands.has_permissions(ban_members=True)
    async def tempban(self, interaction : Interaction, member : nextcord.Member = SlashOption(description="Member to unban", required=True),time : str = SlashOption(description = "Duration of the timeout. (50s, 4h, 7d...)", required=True), *, reason=None):
        await interaction.send(f'{member.mention} a été ban.')
        await member.ban(reason = reason)
        await asyncio.sleep(time2sec(time))
        await member.unban()
        await interaction.send(f'{member.mention} a été unban.')

    @tempban.error
    async def tempban_err(self, inter: Interaction, error):
        if isinstance(error, nextcord.errors.Forbidden):
            await inter.send("Vous ou je n'ai pas les permissions requises.", ephemeral=True)
        else:

            raise error

    @nextcord.slash_command(name="mute", description="mutes a specified member.")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, interaction : Interaction, member : nextcord.Member = SlashOption(description="Member to timeout", required=True), time : str = SlashOption(description = "Duration of the timeout. (50s, 4h, 7d...)", required=True) ,*, reason=None):
        ftime = time2sec(time)
        await member.timeout(timeout = nextcord.utils.utcnow() + timedelta(seconds = ftime), reason = reason)
        await interaction.send(f'{member.mention} has been muted for {time}.')

    @timeout.error
    async def timeout_err(self, interaction: Interaction, error):
        if isinstance(error, nextcord.errors.Forbidden):
            await interaction.send("I or you don't have the required permissions.", ephemeral=True)
        else:
            raise error

    @nextcord.slash_command(name="unmute", description="unmutes a specified member.")
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, interaction : Interaction, member : nextcord.Member = SlashOption(description="Member to untimeout", required=True), *, reason=None):
        await member.timeout(timeout = None, reason = reason)
        await interaction.send(f'{member.mention} has been unmuted.')

    @untimeout.error
    async def untimeout_err(self, interaction: Interaction, error):
        if isinstance(error, nextcord.errors.Forbidden):
            await interaction.send("I or you don't have the required permissions.", ephemeral=True)
        else:
            raise error



def setup(bot):
    bot.add_cog(Admin(bot))
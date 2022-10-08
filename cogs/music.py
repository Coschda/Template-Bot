import nextcord
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.ext import commands
from nextcord.abc import GuildChannel
import random
import wavelink
from datetime import timedelta
import os
from dotenv import load_dotenv
load_dotenv()

ids = [int(x) for x in os.getenv("IDS").split(",")]

global activee

activee = {}

def prettytime(time : int) -> str:
    time = int(time)
    if time < 599:
        min = 0
        while time > 59:
            time -= 60
            min += 1
        return f"{min}:{time//10}{time%10}"
    elif 599 < time < 86400:
        first = True
        txt = str(timedelta(seconds=time))
        txt2 = ''
        for i in txt:
            if i in '0:' and first:
                pass
            elif first and i not in '0:':
                first = False
                txt2 += i
            elif i in '0:' and not first:
                txt2 += i
            else:
                txt2 += i
        return txt2
    else:
        return str(timedelta(seconds=time))

def fillsquare(start : int, end : int, square_nb : int = 20) -> str:
    ratio = round((start / end) * square_nb)
    txt = ''
    for i in range(ratio):
        txt += '▰'
    for i in range(square_nb - ratio):
        txt += '▱'
    return txt

class PauseButton(nextcord.ui.Button):
    def __init__(self, interaction):
        super().__init__(emoji="⏯", row=1)
        try:
            activee[interaction.guild.id]["pause"]
        except:
            activee[interaction.guild.id] = {
                "repeat" : 0,
                "pause" : False,
                "chambles" : False
            }
        if activee[interaction.guild.id]["pause"]:
            self.style=nextcord.ButtonStyle.success
        else:
            self.style = nextcord.ButtonStyle.gray

    async def callback(self, interaction: Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        activee[interaction.guild.id]["pause"] ^= True

        if activee[interaction.guild.id]["pause"]:
            self.style=nextcord.ButtonStyle.success
            await vc.pause()
        else:
            self.style = nextcord.ButtonStyle.gray
            await vc.resume()

        await interaction.response.edit_message(view=self.view)

class RepeatButton(nextcord.ui.Button):
    def __init__(self, interaction):
        super().__init__(emoji = "🔁", row = 1)
        try:
            activee[interaction.guild.id]["pause"]
        except:
            activee[interaction.guild.id] = {
                "repeat" : 0,
                "pause" : False,
                "chambles" : False
            }
        if activee[interaction.guild.id]["repeat"] == 0:
            self.style = nextcord.ButtonStyle.gray
            self.emoji = "🔁"

        elif activee[interaction.guild.id]["repeat"] == 1:
            self.style = nextcord.ButtonStyle.success

        else:
            self.style = nextcord.ButtonStyle.success
            self.emoji = "🔂"
            activee[interaction.guild.id]["repeat"] = -1

    async def callback(self, interaction: Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        activee[interaction.guild.id]["repeat"] += 1

        if activee[interaction.guild.id]["repeat"] == 0:
            self.style = nextcord.ButtonStyle.gray
            self.emoji = "🔁"

            vc.loop = False
            vc.loopone = False

        elif activee[interaction.guild.id]["repeat"] == 1:
            self.style = nextcord.ButtonStyle.success

            vc.loop = True
            vc.loopone = False

        else:
            self.style = nextcord.ButtonStyle.success
            self.emoji = "🔂"
            activee[interaction.guild.id]["repeat"] = -1

            vc.loop = False
            vc.loopone = True

        await interaction.response.edit_message(view = self.view)

class PreviousButton(nextcord.ui.Button):
    def __init__(self, interaction):
        super().__init__(style=nextcord.ButtonStyle.gray, emoji = "⏮", row = 1)
    
    async def callback(self, interaction: Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        try:
            cs: wavelink.Track = vc.track
            ps: wavelink.Track = vc.queue.history[-2]
            vc.queue.history.pop()
            vc.queue.put_at_front(cs)
            await vc.play(ps)
        except IndexError:
            return await interaction.send("There is no previous song.")
    
class NextButton(nextcord.ui.Button):
    def __init__(self, interaction):
        super().__init__(style=nextcord.ButtonStyle.gray, emoji = "⏭", row = 1)
    
    async def callback(self, interaction: Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        try:
            await vc.seek((vc.track.length*1000))
        except wavelink.errors.QueueEmpty:
            if vc.is_playing():
                view = YesorNoView()
                await interaction.send("Il n'y a pas de prochaine musique dans la queue, arreter de jouer ?", view=view)
                await view.wait()
                if view.response is None:
                    print("YesorNo timeout.")
                elif view.response:
                    return await vc.stop()
        except AttributeError:
            try:
                ns = vc.queue.get()
                await vc.play(ns)
                return await Music.status(interaction)
            except wavelink.errors.QueueEmpty:
                if vc.is_playing():
                    view = YesorNoView()
                    await interaction.send("Il n'y a pas de prochaine musique dans la queue, arreter de jouer ?", view=view)
                    await view.wait()
                    if view.response is None:
                        print("YesorNo timeout.")
                    elif view.response:
                        return await vc.stop()
        

class ChamblesButton(nextcord.ui.Button):
    def __init__(self, interaction):
        super().__init__(emoji = "🔀", row = 1)
        try:
            activee[interaction.guild.id]["chambles"]
        except:
            activee[interaction.guild.id] = {
                "repeat" : 0,
                "pause" : False,
                "chambles" : False
            }
        if activee[interaction.guild.id]["chambles"]:
            self.style=nextcord.ButtonStyle.success
        else:
            self.style = nextcord.ButtonStyle.gray

    async def callback(self, interaction: Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        activee[interaction.guild.id]["chambles"] ^= True

        if activee[interaction.guild.id]["chambles"]: 
            self.style=nextcord.ButtonStyle.success

            vc.shuffle = True
        else:
            self.style = nextcord.ButtonStyle.gray

            vc.shuffle = False

        await interaction.response.edit_message(view=self.view)
#self.view.interaction.guild.voice_client.queue.active["chambles"]

class StatusView(nextcord.ui.View):

    def __init__(self, interaction):
        super().__init__()
        self.add_item(RepeatButton(interaction))
        self.add_item(PreviousButton(interaction))
        self.add_item(PauseButton(interaction))
        self.add_item(NextButton(interaction))
        self.add_item(ChamblesButton(interaction))

class YesorNoView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.response = None

    @nextcord.ui.button(label="✓", emoji="✔️", style=nextcord.ButtonStyle.success)
    async def yes(self, button: nextcord.ui.Button, interaction : Interaction):
        self.response = True
        self.stop()

    @nextcord.ui.button(label="✕", emoji="❌", style=nextcord.ButtonStyle.danger)
    async def no(self, button: nextcord.ui.Button, interaction : Interaction):
        self.response = False
        self.stop()

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.node_connect())
        self.active = {
            "repeat" : 0,
            "pause" : False,
            "chambles" : False
        }

    async def node_connect(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(
            bot=self.bot, 
            host='lavalink.oops.wtf', 
            port=443, 
            password='www.freelavalink.ga', 
            https=True
        )

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f'Node <{node.identifier}> is ready!')

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.YouTubeTrack, reason):
        interaction = player.interaction
        vc: player = interaction.guild.voice_client
        prev_track = track
        print(reason)
        #skip : FINISHED
        #stop : STOPPED
        if reason == "STOPPED" or reason == "REPLACED":
            return
        
        if vc.queue.is_empty:
            return 

        if vc.loopone:
            return await vc.play(track)

        if not vc.shuffle:
            ns = vc.queue.get()
        else:
            temp = []
            index = random.choice(range(len(vc.queue.copy())))
            for i in range(index-1):
                temp.append(vc.queue.get())
            ns = vc.queue.get()
            for i in range(index-1):
                vc.queue.put_at_front(temp.pop(-1))
        await vc.play(ns)
        if vc.loop:
            await vc.queue.put_wait(prev_track)
        #await interaction.send(f"Now playing {ns.title}")
        await self.status(interaction)

    @nextcord.slash_command(guild_ids=ids)
    async def play(self, interaction: Interaction, search:str = SlashOption()):
        if interaction.user.voice == None:
            return await interaction.send("Rejoins un channel d'abord.")
        if not interaction.guild.voice_client:
            vc: wavelink.Player = await interaction.user.voice.channel.connect(cls = wavelink.Player)
            vc.interaction = interaction
        elif interaction.user.voice.channel.id != interaction.guild.voice_client.channel.id:
            await interaction.guild.voice_client.move_to(interaction.user.voice.channel)
            vc: wavelink.Player = interaction.guild.voice_client
            vc.interaction = interaction
        else:
            vc: wavelink.Player = interaction.guild.voice_client
            vc.interaction = interaction
        search = await wavelink.YouTubeTrack.search(query=search, return_first = True)

        if not vc.is_playing():
            await vc.queue.put_wait(search)
            ns = vc.queue.get()
            await vc.play(ns)
            #await vc.interaction.send(f"Now playing... {search.title}")
            await self.status(interaction)
        else:
            await vc.queue.put_wait(search)
            await vc.interaction.send(f"{search.title} added to the queue.")
        if not hasattr(vc, "loop"):
            setattr(vc, "loop", False)
        if not hasattr(vc, "loopone"):
            setattr(vc, "loopone", False)
        if not hasattr(vc, "shuffle"):
            setattr(vc, "shuffle", False)

    @nextcord.slash_command(guild_ids=ids)
    async def join(self, interaction: Interaction):
        if interaction.user.voice == None:
            return await interaction.send("Vous n'etes pas dans mon channel vocal.")
        if not interaction.guild.voice_client:
            await interaction.user.voice.channel.connect(cls = wavelink.Player)
            return await interaction.send("Vocal rejoin.")
        if interaction.user.voice.channel.id != interaction.guild.voice_client.channel.id:
            await interaction.guild.voice_client.move_to(interaction.user.voice.channel)
            return await interaction.send("Vocal rejoin.")
        else:
            return await interaction.send("Je suis deja dans ton channel vocal.")

    @nextcord.slash_command(guild_ids=ids)
    async def pause(self, interaction: Interaction):
        if not interaction.guild.voice_client:
            return await interaction.send("Je ne suis dans aucun vocal.")
        elif interaction.user.voice == None:
            return await interaction.send("Vous n'etes pas dans mon channel vocal.")
        else:
            vc: wavelink.Player = interaction.guild.voice_client
        
        await vc.pause()
        await interaction.send("Paused.")

    @nextcord.slash_command(guild_ids=ids)
    async def resume(self, interaction: Interaction):
        if not interaction.guild.voice_client:
            return await interaction.send("Je ne suis dans aucun vocal.")
        elif interaction.user.voice == None:
            return await interaction.send("Vous n'etes pas dans mon channel vocal.")
        else:
            vc: wavelink.Player = interaction.guild.voice_client
        
        await vc.resume()
        await interaction.send("Resumed.")

    @nextcord.slash_command(guild_ids=ids)
    async def stop(self, interaction: Interaction):
        if not interaction.guild.voice_client:
            return await interaction.send("Je ne suis dans aucun vocal.")
        elif interaction.user.voice == None:
            return await interaction.send("Vous n'etes pas dans mon channel vocal.")
        else:
            vc: wavelink.Player = interaction.guild.voice_client
        
        await vc.stop()
        await interaction.send("Stopped.")

    @nextcord.slash_command(guild_ids=ids)
    async def leave(self, interaction: Interaction):
        if not interaction.guild.voice_client:
            return await interaction.send("Je ne suis dans aucun vocal.")
        elif interaction.user.voice == None:
            return await interaction.send("Vous n'etes pas dans mon channel vocal.")
        else:
            vc: wavelink.Player = interaction.guild.voice_client
        
        await vc.disconnect()
        await interaction.send("Disconnected.")

    @nextcord.slash_command(guild_ids=ids)
    async def loopone(self, interaction: Interaction):
        if not interaction.guild.voice_client:
            return await interaction.send("Je ne suis dans aucun vocal.")
        elif interaction.user.voice == None:
            return await interaction.send("Vous n'etes pas dans mon channel vocal.")
        else:
            vc: wavelink.Player = interaction.guild.voice_client

        
        try:
            vc.loopone ^= True
        except Exception:
            setattr(vc, "loopone", False)
        
        if vc.loopone:
            return await interaction.send("Single repeat is now enabled.")
        else:
            return await interaction.send("Single repeat is now disabled.")


    @nextcord.slash_command(guild_ids=ids)
    async def queue(self, interaction : Interaction):
        if not interaction.guild.voice_client:
            return await interaction.send("Je ne suis dans aucun vocal.")
        elif interaction.user.voice == None:
            return await interaction.send("Vous n'etes pas dans mon channel vocal.")
        else:
            vc: wavelink.Player = interaction.guild.voice_client


        if vc.queue.is_empty:
            return await interaction.send("Queue is empty.")
        
        em = nextcord.Embed(title="Queue")
        queue = vc.queue.copy()
        s_count = 0
        for song in queue:
            s_count += 1
            em.add_field(name=f"Song Num {s_count}", value= f"`{song.title}`")
    
        return await interaction.send(embed=em)
        
    @nextcord.slash_command(guild_ids=ids)
    async def skip(self, interaction : Interaction):
        if not interaction.guild.voice_client:
            return await interaction.send("Je ne suis dans aucun vocal.")
        elif interaction.user.voice == None:
            return await interaction.send("Vous n'etes pas dans mon channel vocal.")
        else:
            vc: wavelink.Player = interaction.guild.voice_client

        if not vc.queue.is_empty:
            #ns = vc.queue.get()
            #await vc.play(ns)
            #await interaction.send(f"Now playing... {ns.title}")
            try:
                cs = vc.track
                await vc.seek((vc.track.length*1000))
                return await interaction.send(f"Skipped {cs.title}.")
            except AttributeError:
                ns = vc.queue.get()
                await vc.play(ns)
                return await self.status(interaction)
        else:
            if vc.is_playing():
                view = YesorNoView()
                await interaction.send("Il n'y a rien dans la queue a cette position, arreter la musique ?", view=view)
                await view.wait()
                view.stop()
                if view.response is None:
                    print("YesorNo timeout.")
                elif view.response:
                    return await vc.stop()
            else:
                return await interaction.send("Nothing is currently playing.")

    @nextcord.slash_command(guild_ids=ids)
    async def clear(self, interaction : Interaction):
        if not interaction.guild.voice_client:
            return await interaction.send("Je ne suis dans aucun vocal.")
        elif interaction.user.voice == None:
            return await interaction.send("Vous n'etes pas dans mon channel vocal.")
        else:
            vc: wavelink.Player = interaction.guild.voice_client

        if vc.queue.is_empty:
            return await interaction.send("Queue is already empty.")
        
        vc.queue.clear()
        return await interaction.send("Queue has been cleared.")

    @nextcord.slash_command(guild_ids=ids)
    async def volume(self, interaction : Interaction, volume : float = SlashOption(max_value=500)):
        if not interaction.guild.voice_client:
            return await interaction.send("Je ne suis dans aucun vocal.")
        elif interaction.user.voice == None:
            return await interaction.send("Vous n'etes pas dans mon channel vocal.")
        else:
            vc: wavelink.Player = interaction.guild.voice_client

        if volume <= 0:
            return await interaction.send("Volume can not be under or equal to 0.")
        if volume > 500:
            return await interaction.send("Volume cannot be higher than 500.")
        await interaction.send(f"Setting the volume to {volume}%, this can take 3 to 5 seconds...")
        return await vc.set_volume(volume/100)

    @nextcord.slash_command(guild_ids=ids)
    async def seek(self, interaction : Interaction, position : int):
        if not interaction.guild.voice_client:
            return await interaction.send("Je ne suis dans aucun vocal.")
        elif interaction.user.voice == None:
            return await interaction.send("Vous n'etes pas dans mon channel vocal.")
        else:
            vc: wavelink.Player = interaction.guild.voice_client

        if position < 0:
            return await interaction.send("TU ne peux pas blabla en dessous de 0")
        if position > vc.track.length:
            return await interaction.send("Le temps donné est plus long que la durée de la musique.")
        await interaction.send(f"Seeking to {prettytime(position)}")
        await vc.seek(position*1000)

    @nextcord.slash_command(guild_ids=ids)
    async def loop(self, interaction : Interaction):
        if not interaction.guild.voice_client:
            return await interaction.send("Je ne suis dans aucun vocal.")
        elif interaction.user.voice == None:
            return await interaction.send("Vous n'etes pas dans mon channel vocal.")
        else:
            vc: wavelink.Player = interaction.guild.voice_client

        try:
            vc.loop ^= True
        except Exception:
            setattr(vc, "loop", False)
        
        if vc.loop:
            return await interaction.send("Loop is now enabled.")
        else:
            return await interaction.send("Loop is now disabled.")

    @nextcord.slash_command(guild_ids=ids)
    async def shuffle(self, interaction : Interaction):
        if not interaction.guild.voice_client:
            return await interaction.send("Je ne suis dans aucun vocal.")
        elif interaction.user.voice == None:
            return await interaction.send("Vous n'etes pas dans mon channel vocal.")
        else:
            vc: wavelink.Player = interaction.guild.voice_client

        try:
            vc.shuffle ^= True
        except Exception:
            setattr(vc, "shuffle", False)
        
        if vc.shuffle:
            return await interaction.send("Shuffle is now enabled.")
        else:
            return await interaction.send("Shuffle is now disabled.")

    @nextcord.slash_command(guild_ids=ids)
    async def status(self, interaction : Interaction):
        if not interaction.guild.voice_client:
            return await interaction.send("Je ne suis dans aucun vocal.")
        elif interaction.user.voice == None:
            return await interaction.send("Vous n'etes pas dans mon channel vocal.")
        else:
            vc: wavelink.Player = interaction.guild.voice_client
        
        if not vc.is_playing():
            return await interaction.send("No track playing")

        if hasattr(vc.track, "uri"):
            embed = nextcord.Embed(color=0x2d96e6, title=f"Joue : {vc.track.title}", url=f"{vc.track.uri}")
        else:
            embed = nextcord.Embed(color=0x2d96e6, title=f"Joue : {vc.track.title}")
        if vc.position == vc.track.duration:
            embed.add_field(name="Durée", value=f"{prettytime(0)} {fillsquare(0, vc.track.duration)} {prettytime(vc.track.duration)}", inline=False)
        else:
            embed.add_field(name="Durée", value=f"{prettytime(vc.position)} {fillsquare(vc.position, vc.track.duration)} {prettytime(vc.track.duration)}", inline=False)
        embed.add_field(name="Auteur", value=f"{vc.track.author}", inline=True)
        embed.add_field(name="From", value=f"{vc.track.info['sourceName'].title()}", inline=True)
        embed.set_footer(text="Template Bot")

        await interaction.send(embed=embed, view=StatusView(interaction))

    @nextcord.slash_command(guild_ids=ids)
    async def remove(self, interaction: Interaction, index: int = SlashOption()):
        pass

    @nextcord.slash_command(guild_ids=ids)
    async def queuehistory(self, interaction: Interaction):
        vc: wavelink.Player = interaction.guild.voice_client
        await interaction.send(vc.queue.history)
        liste = []
        for i in vc.queue.history:
            liste.append(type(i))
        await interaction.send(liste)
    
def setup(bot):
    bot.add_cog(Music(bot))
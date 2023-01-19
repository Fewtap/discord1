try:
    import discord
    from discord.ext import commands
    from discord.ext.commands import Bot
    import asyncio
    import random
    import os
    import sys
except Exception as e:
    print("Error: " + str(e))
    print("Installing missing module...")
    #if the import fails, install the missing module
    os.system("pip install " + str(e).split("'")[1])
finally:
    #if the import succeeds, run the bot
    import discord
    from discord.ext import commands
    from discord.ext.commands import Bot
    import asyncio
    import random
    import os
    import sys

token = ''


#if the command line argument is -t or --token then the next argument is the token
if sys.argv[1] == "-t" or sys.argv[1] == "--token":
    token = sys.argv[2]

# Bot Prefix
bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())



#create a function to play a sound
def playSound(member):
    #play the sound
    member.guild.voice_client.play(discord.FFmpegPCMAudio("final.mp3"))
    #wait for the sound to finish
    while member.guild.voice_client.is_playing():
        asyncio.sleep(1)

# Bot Startup
@bot.event
async def on_ready():
    print("Bot is ready!")
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))
        
    #See if there's a voice channel with members in it, if there are several join the one with most members in it
    #get the voice channels the bot is in
    voiceChannels = [x for x in bot.guilds[0].channels if type(x) == discord.channel.VoiceChannel]
    #get the voice channel with the most members
    channel = max(voiceChannels, key=lambda x: len(x.members))
    #if the bot is in the voice channel with the most members
    if bot.user in channel.members:
        #do nothing
        pass
    #if the bot is not in the voice channel with the most members
    else:
        #join the voice channel with the most members
        vc = await channel.connect()
        #play the sound
        vc.play(discord.FFmpegPCMAudio("final.mp3"))
        #wait for the sound to finish
        while vc.is_playing():
            asyncio.sleep(1)
    
    


#On voice state update
@bot.event
async def on_voice_state_update(member, before, after):
    #If the member is a bot do nothing
    if member.bot:
        return


    #If user joins a voice channel
    if before.channel is None and after.channel is not None:
        #If theh bot is already in a voice channel and the user joins the voice channel the bot is in
        if member.guild.voice_client is not None and member.guild.voice_client.channel == after.channel:
            #play the sound
            playSound(member)
        #If the bot is not in a voice channel already, join the voice channel
        if member.guild.voice_client is None:
            channel = after.channel
            vc = await channel.connect()
            #play the sound
            playSound(member)
        #If the bot is in a voice channel already, and there's less members in the new voice channel than the current voice channel, join the new voice channel
        elif member.guild.voice_client is not None:
            if len(after.channel.members) > len(member.guild.voice_client.channel.members):
                pass
            else:
                #leave the current voice channel
                await member.guild.voice_client.disconnect()
                #join the new voice channel
                channel = after.channel
                vc = await channel.connect()
                #play the sound
                playSound(member)


    #If user leaves a voice channel
    elif before.channel is not None and after.channel is None:
        #if the bot is the only one in the voice channel
        if len(before.channel.members) == 1:
            #leave the voice channel
            await before.channel.guild.voice_client.disconnect()
            #If there are memebers in another voice channel join the one with the most members
        else:
            #get the voice channels the bot is in
            voiceChannels = [x for x in member.guild.channels if type(x) == discord.channel.VoiceChannel]
            #get the voice channel with the most members
            channel = max(voiceChannels, key=lambda x: len(x.members))
            #if the bot is in the voice channel with the most members
            if bot.user in channel.members:
                #do nothing
                pass
            #if the bot is not in the voice channel with the most members
            else:
                #join the voice channel with the most members
                vc = await channel.connect()
                playSound(member)


    #If user switches voice channels
    elif before.channel is not None and after.channel is not None:
        #if the bot is the only one in the voice channel
        if len(before.channel.members) == 1:
            #leave the voice channel
            await before.channel.guild.voice_client.disconnect()
            #If there are memebers in another voice channel join the one with the most members
        
            #get the voice channels the bot is in
            voiceChannels = [x for x in member.guild.channels if type(x) == discord.channel.VoiceChannel]
            #get the voice channel with the most members
            channel = max(voiceChannels, key=lambda x: len(x.members))
            #if the bot is in the voice channel with the most members
            if bot.user in channel.members:
                #do nothing
                pass
            #if the bot is not in the voice channel with the most members
            else:
                #join the voice channel with the most members
                vc = await channel.connect()
                playSound(member)
        

        #if there are less members in the new voice channel than the current voice channel
        if len(after.channel.members) < len(before.channel.members):
            #leave the current voice channel
            await before.channel.guild.voice_client.disconnect()
            #join the new voice channel
            channel = after.channel
            vc = await channel.connect()
            #play the sound
            playSound(member)
        




#run the bot
bot.run(token)
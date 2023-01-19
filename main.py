from asyncio import tasks
import datetime
import threading


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
async def playSound(member):
    try:
        #play the sound
        member.guild.voice_client.play(discord.FFmpegPCMAudio("final.mp3"))
        #wait for the sound to finish
        while member.guild.voice_client.is_playing():
           await asyncio.sleep(1)
    except Exception as e:
        print("Error: " + str(e))

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
            await asyncio.sleep(1)
    
    
andreas = 134427081672097793

#On voice state update
@bot.event
async def on_voice_state_update(member, before, after):

    #if the state update is not from switching or joining a voice channel do nothing
    if before.channel == after.channel:
        return

    #If the member is a bot do nothing
    if member.bot:
        return
    
    #if the member leaves a voice channel
    if before.channel != None and after.channel == None:
        
        #if there's no one left in the voice channel
        if len(before.channel.members) == 1:
            #if there's another channel with members in it, join the one with the most members in it, if there's only empty channels, disconnect
            #get the voice channels the bot is in
            voiceChannels = [x for x in bot.guilds[0].channels if type(x) == discord.channel.VoiceChannel]
            #get the voice channel with the most members
            channel = max(voiceChannels, key=lambda x: len(x.members))
            #if the bot is in the voice channel with the most members
            if bot.user in channel.members:
                #disconnect
                await before.channel.guild.voice_client.disconnect()
            #if the bot is not in the voice channel with the most members
            else:
                #join the voice channel with the most members
                vc = await channel.connect()
                #play the sound
                vc.play(discord.FFmpegPCMAudio("final.mp3"))
                #wait for the sound to finish
                while vc.is_playing():
                    await asyncio.sleep(1)
        #if there's someone left in the voice channel
        else:
            #do nothing
            pass

    if member.id == andreas:
        return


            



    #if the member joins a voice channel
    if before.channel == None and after.channel != None:
        #if the member is andreas
        if member.id == andreas:
            return
        #if the member is not andreas
        else:
            #if the bot is in the same voice channel as the member
            if bot.user in after.channel.members:
                #play the sound
                await playSound(member)
            else:
                #disconnect and join the voice channel the member is in
                await before.channel.guild.voice_client.disconnect()
                vc = await after.channel.connect()
                #play the sound
                vc.play(discord.FFmpegPCMAudio("final.mp3"))
                #wait for the sound to finish
                while vc.is_playing():
                    await asyncio.sleep(1)

    #if the member switches voice channels
    if before.channel != None and after.channel != None:
        if member.id == andreas:
            return
        #if the bot is in the same voice channel as the member
        if bot.user in after.channel.members:
            #play the sound
            await playSound(member)
        else:
            #if there's is less members in the voice channel the member is in than the voice channel the bot is in disconnect and join the voice channel the member is in
            if len(after.channel.members) < len(before.channel.members):
                await before.channel.guild.voice_client.disconnect()
                vc = await after.channel.connect()
                #play the sound
                vc.play(discord.FFmpegPCMAudio("final.mp3"))
                #wait for the sound to finish
                while vc.is_playing():
                    await asyncio.sleep(1)
            #else if only the bot is left in the voice channel the bot is in, disconnect and join the voice channel the member is in
            elif len(before.channel.members) == 1:
                await before.channel.guild.voice_client.disconnect()
                vc = await after.channel.connect()
                #play the sound
                vc.play(discord.FFmpegPCMAudio("final.mp3"))
                #wait for the sound to finish
                while vc.is_playing():
                    await asyncio.sleep(1)
        




#On message delete
@bot.event
async def on_message_delete(message):
    #if the message is from a bot do nothing
    if message.author.bot:
        return
    #if the message is not from a bot
    else:
        #send a message in the same channel as the deleted message mentioning the author of the deleted message and calling them out
        botmessage = await message.channel.send("Hörrudu " + message.author.mention + ", jag såg det där!")
        #delete the message after 5 seconds
        await asyncio.sleep(5)
        #delete all messages the bot has sent in the channel
        await botmessage.delete()
        

#On message edit
@bot.event
async def on_message_edit(before, after):
    #if the message is from a bot do nothing
    if before.author.bot:
        return
    #if the message is not from a bot
    else:
        #send a message in the same channel as the edited message mentioning the author of the edited message and calling them out
        botmessage = await before.channel.send("HAHAHAHAH" + before.author.mention + " KAN INTE SKRIVA")
        #delete the message after 5 seconds
        await asyncio.sleep(5)
        #delete all messages the bot has sent in the channel
        await botmessage.delete()





#run the bot
bot.run(token)
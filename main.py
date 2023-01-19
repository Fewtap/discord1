from asyncio import tasks
import datetime
import threading
import praw
from discord.ext import tasks as discord_tasks

#init reddit
reddit = praw.Reddit(client_id='ej-ZEwtd6hUmvrV4nRqPHg', client_secret='UAkc21N6qnsnF9hU2ZAYk9MFIVmbDA', user_agent='your bot 0.1 by /u/your_bot')

mejmejs = True


try:
    import discord
    from discord.ext import commands
    from discord.ext.commands import Bot
    import asyncio
    import random
    import os
    import sys
    #import tasks loop
    from asyncio import tasks
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
    #2 procent chance of playing "arg.mp3"
    number = random.randint(1,100)
    print(number)
    if number <= 10:
        #play the sound
        member.guild.voice_client.play(discord.FFmpegPCMAudio("arg.mp3"))
        #wait for the sound to finish
        while member.guild.voice_client.is_playing():
            await asyncio.sleep(1)
    #if number is between 10 and 30
    elif number > 10 and number <= 30:
        #play the sound
        member.guild.voice_client.play(discord.FFmpegPCMAudio("eww.mp3"))
        #wait for the sound to finish
        while member.guild.voice_client.is_playing():
            await asyncio.sleep(1)
    else:
        #play the sound
        member.guild.voice_client.play(discord.FFmpegPCMAudio("final.mp3"))
        #wait for the sound to finish
        while member.guild.voice_client.is_playing():
            await asyncio.sleep(1)
    

# Bot Startup
@bot.event
async def on_ready():
    print("Bot is ready!")
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))
    if mejmejs == True:
        #start the loop
        send_message.start()
    
        
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
                await playSound(member)
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
                await playSound(member)
                

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
                await playSound(member)
                #wait for the sound to finish
                
            #else if only the bot is left in the voice channel the bot is in, disconnect and join the voice channel the member is in
            elif len(before.channel.members) == 1:
                await before.channel.guild.voice_client.disconnect()
                vc = await after.channel.connect()
                #play the sound
                await playSound(member)
        

#send a message to a specific channel every five minutes
@discord_tasks.loop(minutes=10)
async def send_message():
    #get the channel
    channel = bot.get_channel(1065645686697246810)
    #get the 10 image posts from r/unket and put them in a list
    posts = []
    for submission in reddit.subreddit("unket").hot(limit=10):
        posts.append(submission)
    #get a random post from the list
    post = random.choice(posts)
    lastmessages = []
    #if the post.url already exists in the channel pick another one
    #get the last 100 messages in the channel
    async for message in channel.history(limit=100):
        lastmessages.append(message)
    #while the post.url already exists in the channel
    while post.url in [x.content for x in lastmessages]:
        #get a new post
        post = random.choice(posts)

    #send the post.url in the channel
    
    await channel.send(post.title + "\n" + post.url)
    


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
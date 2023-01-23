from asyncio import tasks
import asyncio
import datetime
import json
import os
import random
import sys
import threading
import time
from xmlrpc.client import SYSTEM_ERROR
import praw
from discord.ext import commands
import discord
from discord.ext import tasks as discord_tasks
import helpermethods

# init reddit
reddit = praw.Reddit(
    client_id="ej-ZEwtd6hUmvrV4nRqPHg",
    client_secret="UAkc21N6qnsnF9hU2ZAYk9MFIVmbDA",
    user_agent="your bot 0.1 by /u/your_bot",
)

mejmejs = True
timer = None
token = ""
blacklistedmembers = [134427081672097793, 632279608930205737]

#read the firs line of the token file and put it in a variable
with open("token.txt", "r") as f:
    token = f.readline()
    

# add necessary intents in a variable
intents = discord.Intents.default()
intents.members = True
intents.message_content = True


bot: commands.Bot = commands.Bot(command_prefix="!", intents=intents)


async def MovetoPopulatedChannel():
    for guild in bot.guilds:

        if guild.voice_client == None:
            continue

            # get the most populated voice channel and connect to it
        voicechannel = max(guild.voice_channels, key=lambda x: len(x.members))
        if voicechannel != None:
            if len(guild.voice_client.channel.members) > 1:
                continue
            if bot.user in voicechannel.members:
                continue
            await voicechannel.guild.voice_client.disconnect()
            await voicechannel.connect()
            break
        else:
            await voicechannel.connect()


movetoChannelLoop = discord_tasks.loop(seconds=10)(MovetoPopulatedChannel)


async def DeleteTextMessages():
    channelID = 675461786056785975
    channel = bot.get_channel(channelID)

    # get all messages that does not contain an image
    """async for message in channel.history(limit=1000):
        if message.attachments == []:
            # if there's a link in the message
            if "http" in message.content:
                break
            await message.delete()
        else:
            pass"""
    # get the last 1000 messages in the channel and put them in a list
    messages = []
    async for message in channel.history(limit=200):
        if message.attachments != []:
            print(message.content)
        elif "http" in message.content:
            print(message.content)
        else:
            # get the time difference between the message and now
            timeDifference = datetime.datetime.now() - message.created_at
            # if the message is less that 14 days old add it to the list
            if timeDifference.days < 14:

                messages.append(message)

        # if there's more than 40 messages in the list split them into chunks of 40 and delete them
        if len(messages) > 40:
            for i in range(0, len(messages), 40):
                await channel.delete_messages(messages[i : i + 40])
            messages = []
        else:
            if len(messages) != 0 and len(messages < 40):
                channel.delete_messages(messages)


selfieschannel = discord_tasks.loop(minutes=10)(DeleteTextMessages)


# Bot Startup
@bot.event
async def on_ready():
    print("Bot is ready!")
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))
    print("Discord Version: {}".format(discord.__version__))

    selfieschannel.start()
    movetoChannelLoop.start()
    # for every guild the bot is in
    for guild in bot.guilds:
        # check for voice channels with members in them
        # check if there's voice channels with members in them and if there are several check which one has the most and put that channel in a variable
        # get the voice channels the bot is in
        voiceChannels = [
            x for x in guild.channels if type(x) == discord.channel.VoiceChannel
        ]
        # get the voice channel with the most members
        channel = max(voiceChannels, key=lambda x: len(x.members))
        # if there's no one in the voice channel, do nothing
        if len(channel.members) == 0:
            return
        # if there's someone in the voice channel, join it
        else:
            if len(channel.members) == 1:
                if channel.members[0] == bot.user:
                    await channel.guild.voice_client.disconnect()
                if channel.members[0].id in blacklistedmembers:
                    return
            # join the voice channel
            await channel.connect()
            # play a generic sound
            await helpermethods.playSound(channel.members[0], generic=True)


# On voice state update
@bot.event
async def on_voice_state_update(member, before, after):

    if member == bot.user:
        return

    await asyncio.sleep(2)
    # if the state update is not from switching or joining a voice channel do nothing
    if before.channel == after.channel:
        return

    # if the bot was not in a voice channel before and is now in a voice channel

    # if the member leaves a voice channel
    if before.channel != None and after.channel == None:

        # if there's no one left in the voice channel
        if len(before.channel.members) == 1:
            # if there's another channel with members in it, join the one with the most members in it, if there's only empty channels, disconnect
            # get the voice channels the bot is in
            voiceChannels = [
                x
                for x in before.channel.guild.channels
                if type(x) == discord.channel.VoiceChannel
            ]
            # get the voice channel with the most members
            channel = max(voiceChannels, key=lambda x: len(x.members))
            # if the bot is in the voice channel with the most members
            if bot.user in channel.members:
                # disconnect
                await before.channel.guild.voice_client.disconnect()
            # if the bot is not in the voice channel with the most members
            else:
                # join the voice channel with the most members
                vc = await channel.connect()
                # play the sound
                await helpermethods.playSound(member)
                # wait for the sound to finish
                while vc.is_playing():
                    await asyncio.sleep(1)
        # if there's someone left in the voice channel
        else:
            # if member id is in blacklist do nothing
            if member.id in blacklistedmembers:
                return

            # wait for the sound to finish
            while vc.is_playing():
                await asyncio.sleep(1)

    if member.id in blacklistedmembers:
        return

    # if the member joins a voice channel
    if before.channel == None and after.channel != None:

        if "AFK" in after.channel.name:
            return

        # if the bot is not in a voice channel
        if bot.user not in after.channel.members:
            # join the voice channel the member is in
            vc = await after.channel.connect()
            # play the sound
            await helpermethods.playSound(member)
            playInjections.start()
            return
        # if the bot is in the same voice channel as the member
        if bot.user in after.channel.members:
            if member == bot.user:
                pass
            else:
                # play the sound
                await helpermethods.playSound(member)
        else:
            # if there's is less members in the voice channel the member is in than the voice channel the bot is in disconnect and join the voice channel the member is in
            if len(after.channel.members) < len(before.channel.members):
                await before.channel.guild.voice_client.disconnect()
                vc = await after.channel.connect()
                # play the sound
                await helpermethods.playSound(member)
                playInjections.start()
                return

    # if the member switches voice channels
    if before.channel != None and after.channel != None:
        # if the after channels name contains "AFK" do nothing
        if "AFK" in after.channel.name:
            return

        # if the bot is in the same voice channel as the member
        if bot.user in after.channel.members:
            # play the sound
            await helpermethods.playSound(member)
        else:
            # if there's is less members in the voice channel the member is in than the voice channel the bot is in disconnect and join the voice channel the member is in
            if len(after.channel.members) < len(before.channel.members):
                await before.channel.guild.voice_client.disconnect()
                vc = await after.channel.connect()
                # play the sound
                await helpermethods.playSound(member)
                playInjections.start()

            # else if only the bot is left in the voice channel the bot is in, disconnect and join the voice channel the member is in
            elif len(before.channel.members) == 1:
                await before.channel.guild.voice_client.disconnect()
                vc = await after.channel.connect()
                # play the sound
                await helpermethods.playSound(member)


# on message




@bot.event
async def on_message(message: discord.message.Message):

    selfaware = "Fan Mäc, the är lite k-ringe att du inte gett mig fler kommentarer att svara med."

    

    
    channel = message.channel

    #if the more than 5 messages have been sent from the bot in the last 20 seconds in the channel variable
    if len([m for m in await channel.history(limit=20).flatten() if m.author == bot.user]) > 5:
        await message.channel.send(selfaware)
    

    

    # write to file
    if message.author == bot.user:
        return

    with open("logs.txt", "a", encoding="utf-8") as f:
        # create a dict with the message data and all values as strings
        messageData = {
            "author": str(message.author),
            "author_id": str(message.author.id),
            "content": str(message.content),
            "channel": str(message.channel),
            "channel_id": str(message.channel.id),
            "guild": str(message.guild),
            "guild_id": str(message.guild.id),
            "created_at": str(message.created_at),
        }

        #make a list of dicts
        messageDataList = []

        #check if there's a folder with the guild id as the name
        if not os.path.exists(f"{message.guild.id}"):
            # if not create one
            os.makedirs(f"{message.guild.id}")
            #check if there's a folder with the channel id as the name
            if not os.path.exists(f"{message.guild.id}/{message.channel.id}"):
                # if not create one
                os.makedirs(f"{message.guild.id}/{message.channel.id}")
                #create a json file with the message creation date as the name but only the date
                with open(f"{message.guild.id}/{message.channel.id}/{message.created_at.date()}.json", "w") as f:
                    # append the message data to the list
                    messageDataList.append(messageData)
                    # write the list to the json file
                    json.dump(messageDataList, f, indent=4)
        else:
            #check if there's a folder with the channel id as the name
            if not os.path.exists(f"{message.guild.id}/{message.channel.id}"):
                # if not create one
                os.makedirs(f"{message.guild.id}/{message.channel.id}")
                #create a json file with the message creation date as the name
                with open(f"{message.guild.id}/{message.channel.id}/{message.created_at.date()}.json", "w") as f:
                    # append the message data to the list
                    messageDataList.append(messageData)
                    # write the list to the json file
                    json.dump(messageDataList, f, indent=4)
            else:
                #check if there's a json file with the message creation date as the name
                if not os.path.exists(f"{message.guild.id}/{message.channel.id}/{message.created_at.date()}.json"):
                    # if not create one
                    with open(f"{message.guild.id}/{message.channel.id}/{message.created_at.date()}.json", "w") as f:
                        # append the message data to the list
                        messageDataList.append(messageData)
                        # write the list to the json file
                        json.dump(messageDataList, f, indent=4)
                else:
                    # if there is a json file with the message creation date as the name
                    with open(f"{message.guild.id}/{message.channel.id}/{message.created_at.date()}.json", "r") as f:
                        # read the json file
                        messageDataList = json.load(f)
                        # append the message data to the list
                    with open(f"{message.guild.id}/{message.channel.id}/{message.created_at.date()}.json", "w") as f:
                        messageDataList.append(messageData)
                        # write the list to the json file
                        json.dump(messageDataList, f, indent=4)

    Moa = 131007135877300224
    Bill = 454025791777275905

    tjackphrases = [
        "Fett sunkigt att sitta och prata om droger men ok",
        "Sluta tjacka ta en havreboll istället",
    ]
    botphrases = [
        "Käften hora du kan va en bot",
        "Jag bot? HAHA jag är i alla fall ingen NPC irl som dig",
        "Sitter du och pratar bakom min rygg? Det hade jag också gjort om jag såg ut som du",
    ]

    mentionPhrases = [
        "Sluta pinga mig horunge",
        "Lägg av bara Bill får pinga mig",
        "Jag är inte din hund, sluta pinga mig",
        f"Visste ni att det är @<{Moa}> som ger min röst? Synd att hon inte gör mina bröst.",
        "Det är Mäc som har programmerat mig. Det är därför jag är lite cp"
    ]

    billPhrases = [
        f"Va det nån som sa @<{Bill}> ? Hade ridit på den idiotens nylle om jag inte varit digital"
    ]

    botmessage = None

    if bot.user in message.mentions:
        phrase = random.choice(mentionPhrases)
        botmessage = await message.reply(phrase)

    elif "tjack" in message.content.lower():
        phrase = random.choice(tjackphrases)
        await message.reply(phrase)

    # elif bot and tindra is anywhere in the string
    elif "bot" in message.content.lower() and "tindra" in message.content.lower():
        phrase = random.choice(botphrases)
        await message.reply(phrase)
    
    elif "bill" in message.content.lower():
        phrase = random.choice(billPhrases)
        await message.reply(phrase)


# send a message to a specific channel every five minutes
@discord_tasks.loop(minutes=10)
async def send_message():
    # get the channel
    channel = bot.get_channel(1065645686697246810)
    # get the 10 image posts from r/unket and put them in a list
    posts = []
    for submission in reddit.subreddit("shitposting").hot(limit=10):
        posts.append(submission)
    # get a random post from the list
    post = random.choice(posts)
    lastmessages = []
    # if the post.url already exists in the channel pick another one
    # get the last 100 messages in the channel
    async for message in channel.history(limit=100):
        lastmessages.append(message)
    # while the post.url already exists in the channel
    while post.url in [x.content for x in lastmessages]:
        # get a new post
        post = random.choice(posts)

    # send the post.url in the channel

    await channel.send(post.title + "\n" + post.url)


# On message delete
@bot.event
async def on_message_delete(message):
    # if the message is from a bot do nothing
    if message.author.bot:
        return
    # if the message is not from a bot
    else:
        # send a message in the same channel as the deleted message mentioning the author of the deleted message and calling them out
        botmessage = await message.channel.send(
            "Hörrudu " + message.author.mention + ", jag såg det där!"
        )
        # delete the message after 5 seconds
        await asyncio.sleep(5)
        # delete all messages the bot has sent in the channel
        await botmessage.delete()


# On message edit
@bot.event
async def on_message_edit(before, after):
    # if the message is from a bot do nothing
    if before.author.bot:
        return
    # if the message is not from a bot
    else:
        if "http" in after.content:
            return
        # if there's an attachment in the message do nothing
        if len(after.attachments) > 0:
            return
        # send a message in the same channel as the edited message mentioning the author of the edited message and calling them out
        botmessage = await before.channel.send(
            "HAHAHAHAH " + before.author.mention + " KAN INTE SKRIVA"
        )
        # delete the message after 5 seconds
        await asyncio.sleep(5)
        # delete all messages the bot has sent in the channel
        await botmessage.delete()


# loop every 3 to 5 minutes
@discord_tasks.loop(minutes=3)
async def playInjections():
    print("Running injections loop")
    injections = os.listdir("sounds/injections")
    for guild in bot.guilds:
        # check if the bot is in a voice channel
        if guild.voice_client != None:
            # check if the bot is in a voice channel with members
            if len(guild.voice_client.channel.members) > 1:
                # get the voice channel the bot is in
                channel = guild.voice_client.channel
                # get the members in the voice channel
                members = channel.members
                # get a random member from the members in the voice channel
                member = random.choice(members)

                # build a path to the sound file
                path = "sounds/injections/" + random.choice(injections)

                # play the sound
                guild.voice_client.play(discord.FFmpegPCMAudio(path))
                # wait for the sound to finish
                while guild.voice_client.is_playing():
                    await asyncio.sleep(1)
            else:
                # if the bot is in a voice channel with no members disconnect
                await guild.voice_client.disconnect()


# run the bot
bot.run(token)

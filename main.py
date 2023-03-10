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
from helpermethods import *
import firestoreclient

# init reddit
reddit = praw.Reddit(
    client_id="ej-ZEwtd6hUmvrV4nRqPHg",
    client_secret="UAkc21N6qnsnF9hU2ZAYk9MFIVmbDA",
    user_agent="your bot 0.1 by /u/your_bot",
)
config = {}
# read the config.json file and put it in a variable
with open("config.json", "r") as f:
    config = json.load(f)


# read the firs line of the token file and put it in a variable
token = ""
with open("token.txt", "r") as f:
    token = f.readline()

blacklistedmembers = config["blacklistedmembers"]

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

    if config["runVoiceFunctions"]:
        # selfieschannel.start()
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

                # play a generic sound
                vc: discord.VoiceClient = await channel.connect()
                playInjections.start()


# On voice state update
@bot.event
async def on_voice_state_update(member, before, after):
    if config["runVoiceFunctions"] == False:
        return

    if member == bot.user:
        return

    await asyncio.sleep(2)
    # if the state update is not from switching or joining a voice channel do nothing
    if before.channel == after.channel:
        return

    # if the bot was not in a voice channel before and is now in a voice channel

    # if the member leaves a voice channel
    if before.channel != None and after.channel == None:
        memberLeaves(
            before,
            after,
            member,
            bot,
        )

    # if the member joins a voice channel
    if before.channel == None and after.channel != None:

        if "AFK" in after.channel.name:
            return

        # if the bot is not in a voice channel
        if bot.user not in after.channel.members:
            # join the voice channel the member is in
            vc = await after.channel.connect()
            # play the sound
            await playSound(member)
            playInjections.start()
            return
        # if the bot is in the same voice channel as the member
        if bot.user in after.channel.members:
            if member == bot.user:
                pass
            else:
                # play the sound
                await playSound(member)
        else:
            # if there's is less members in the voice channel the member is in than the voice channel the bot is in disconnect and join the voice channel the member is in
            if len(after.channel.members) < len(before.channel.members):
                await before.channel.guild.voice_client.disconnect()
                vc = await after.channel.connect()
                # play the sound
                await playSound(member)
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
            await playSound(member)
        else:
            # if there's is less members in the voice channel the member is in than the voice channel the bot is in disconnect and join the voice channel the member is in
            if len(after.channel.members) < len(before.channel.members):
                await before.channel.guild.voice_client.disconnect()
                vc = await after.channel.connect()
                # play the sound
                await playSound(member)
                playInjections.start()

            # else if only the bot is left in the voice channel the bot is in, disconnect and join the voice channel the member is in
            elif len(before.channel.members) == 1:
                await before.channel.guild.voice_client.disconnect()
                vc = await after.channel.connect()
                # play the sound
                await playSound(member)


# on message


@bot.event
async def on_message(message: discord.message.Message):

    await firestoreclient.LogData(message)

    if config["runTextFunctions"] == False:
        return

    if "!dc" in message.content:
        if message.author in message.guild.voice_client.channel.members:
            await message.channel.send("Hej D??!")
            await message.guild.voice_client.disconnect()
            return
    elif "!join" in message.content.lower():
        if message.guild.voice_client != None:
            if message.author in message.guild.voice_client.channel.members:
                await message.channel.send("Jag ??r redan h??r!")
                return
        else:
            if message.guild.voice_client != None:
                await message.guild.voice_client.disconnect()
            vc = await message.author.voice.channel.connect()
            await message.channel.send("Jag ??r h??r!")
            return

    # write to file
    if message.author == bot.user:
        return

    Moa = 131007135877300224
    Bill = 454025791777275905

    tjackphrases = [
        "Fett sunkigt att sitta och prata om droger men ok",
        "Sluta tjacka ta en havreboll ist??llet",
    ]
    botphrases = [
        "K??ften hora du kan va en bot",
        "Jag bot? HAHA jag ??r i alla fall ingen NPC irl som dig",
        "Sitter du och pratar bakom min rygg? Det hade jag ocks?? gjort om jag s??g ut som du",
    ]

    mentionPhrases = [
        "Sluta pinga mig horunge",
        "L??gg av bara Bill f??r pinga mig",
        "Jag ??r inte din hund, sluta pinga mig",
        f"Visste ni att det ??r <@{Moa}> som ger min r??st? Synd att hon inte g??r mina br??st.",
        "Det ??r M??c som har programmerat mig. Det ??r d??rf??r jag ??r lite cp",
    ]

    billPhrases = [
        f"Va det n??n som sa <@{Bill}>? Hade ridit p?? den idiotens nylle om jag inte varit digital"
    ]

    sauce = ["Mmm... S??s...", "S??s, my favourite"]

    botmessage = None
    if config["runTextFunctions"]:
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
        elif "s??s" in message.content.lower():
            phrase = random.choice(sauce)
            await message.reply(phrase)
        # if bot and j??vel is anywhere in the string or if bot and j??vla is anywhere in the string
        elif "j??vel" in message.content.lower() or "j??vla" in message.content.lower():
            if "bot" in message.content.lower():
                await message.reply("Tro du jag bryr mig?")


# send a message to a specific channel every five minutes
@discord_tasks.loop(minutes=10)
async def send_message():
    if config["runTextFunctions"]:
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
    await firestoreclient.DeleteMessage(message)
    # if the message is from a bot do nothing
    if message.author.bot:
        return
    # if the message is not from a bot
    else:
        if config["runTextFunctions"]:
            # send a message in the same channel as the deleted message mentioning the author of the deleted message and calling them out
            botmessage = await message.channel.send(
                "H??rrudu " + message.author.mention + ", jag s??g det d??r!"
            )
            # delete the message after 5 seconds
            await asyncio.sleep(5)
            # delete all messages the bot has sent in the channel
            await botmessage.delete()


# On message edit
@bot.event
async def on_message_edit(before, after):
    await firestoreclient.LogEdit(before, after)
    # if the message is from a bot do nothing
    if before.author.bot:
        return
    # if the message is not from a bot
    else:
        if config["runTextFunctions"]:
            # send a message in the same channel as the edited message mentioning the author of the edited message and calling them out
            botmessage = await before.channel.send(
                "H??rrudu " + before.author.mention + ", jag s??g det d??r!"
            )
            # delete the message after 5 seconds
            await asyncio.sleep(5)
            # delete all messages the bot has sent in the channel
            await botmessage.delete()


# loop every 3 to 5 minutes
@discord_tasks.loop(minutes=3)
async def playInjections():
    if config["runSoundFunctions"]:
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


# on reaction add
@bot.event
async def on_reaction_add(reaction: discord.reaction.Reaction, user):
    # if the reaction is not from a bot
    if not user.bot:
        message = reaction.message
        message.add_reaction(reaction.emoji)


# run the bot
bot.run(token)

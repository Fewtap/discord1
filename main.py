from asyncio import tasks
import asyncio
import datetime
import os
import random
import sys
import threading
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

# if the command line argument is -t or --token then the next argument is the token
if len(sys.argv) > 1:
    if sys.argv[1] == "-t" or sys.argv[1] == "--token":
        token = sys.argv[2]
    else:
        print("Invalid command line arguments")
        sys.exit(1)

# Bot Prefix
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
bot.intents.message_content = True
bot.intents.members = True
bot.intents.guilds = True
bot.intents.presences = True
bot.intents.guild_messages = True
bot.intents.guild_reactions = True


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
    async for message in channel.history(limit=1000):
        if message.attachments != []:
            print(message.content)
        elif "http" in message.content:
            print(message.content)
        else:
            await message.delete()
    # if the message contains an image or a link print the message


selfieschannel = discord_tasks.loop(minutes=10)(DeleteTextMessages)


# Bot Startup
@bot.event
async def on_ready():
    print("Bot is ready!")
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))
    print("Discord Version: {}".format(discord.__version__))

    selfieschannel.start()
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

last_run_timeTjack = None


@bot.event
async def on_message(message):
    print(message.content)

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
    ]
    global last_run_timeTjack
    global last_run_mentions
    global last_run_botMention
    current_time = datetime.datetime.now()
    if last_run_timeTjack is not None:
        time_since_last_run = current_time - last_run_timeTjack
        if time_since_last_run.total_seconds() < 10800:  # 3 hours in seconds
            pass
        else:
            last_run_timeTjack = current_time

            if message.author == bot.user:
                return
            if message.author.id in blacklistedmembers:
                return
            if "tjack" in message.content.lower():
                # send a random phrase from the list
                await message.channel.send(random.choice(tjackphrases))
    if last_run_timeTjack is not None:
        time_since_last_run = current_time - last_run_mentions
        if time_since_last_run.total_seconds() < 10800:  # 3 hours in seconds
            pass
        else:
            last_run_timeTjack = current_time

            # if the bot was mentioned respond with a random phrase from the list
            if bot.user.mentioned_in(message):
                await message.channel.send("S")
    if last_run_timeTjack is not None:
        time_since_last_run = current_time - last_run_botMention
        if time_since_last_run.total_seconds() < 10800:  # 3 hours in seconds
            pass
        else:
            last_run_botMention = current_time

            # if the message contains the word "bot" and "Tilda" respond with a random phrase from the list
            if "bot" in message.content.lower() and "tilda" in message.content.lower():
                return


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
        # send a message in the same channel as the edited message mentioning the author of the edited message and calling them out
        botmessage = await before.channel.send(
            "HAHAHAHAH" + before.author.mention + " KAN INTE SKRIVA"
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

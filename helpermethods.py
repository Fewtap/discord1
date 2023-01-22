# create a function to play a sound
import asyncio
import os
import random
import supabase
from discord.ext import commands
import discord
from discord.ext import tasks as discord_tasks
from supabase import create_client, Client


async def playSound(member, generic=False):

    if generic == True:
        # get sound files in the sounds/generic folder
        soundfiles = [x for x in os.listdir("sounds/generic") if x.endswith(".mp3")]
        # get a random sound file
        soundfile = random.choice(soundfiles)
        # build a path to the sound file
        path = "sounds/generic/" + soundfile
        # play the sound with high volume
        member.guild.voice_client.play(discord.FFmpegPCMAudio(path))
        # wait for the sound to finish
        while member.guild.voice_client.is_playing():
            await asyncio.sleep(1)
        return

    # get the sound files in the sounds folder ending with .mp3 and .m4a
    soundfiles = [
        x for x in os.listdir("sounds") if x.endswith(".mp3") or x.endswith(".m4a")
    ]

    # get the id of the member and compare it to the names of the mp3 files
    for x in soundfiles:
        # if the id of the member is in the name of the mp3 file
        if str(member.id) in x:
            # build a path to the sound file
            path = "sounds/" + x
            # play the sound with high volume

            member.guild.voice_client.play(discord.FFmpegPCMAudio(path))

            # wait for the sound to finish
            while member.guild.voice_client.is_playing():
                await asyncio.sleep(1)
            # stop the loop
            break
    else:
        # get sound files in the sounds/generic folder
        soundfiles = [x for x in os.listdir("sounds/generic") if x.endswith(".mp3")]
        # get a random sound file
        soundfile = random.choice(soundfiles)
        # build a path to the sound file
        path = "sounds/generic/" + soundfile
        # play the sound with high volume
        member.guild.voice_client.play(discord.FFmpegPCMAudio(path))
        # wait for the sound to finish
        while member.guild.voice_client.is_playing():
            await asyncio.sleep(1)


async def UploadToDB(bot: commands.Bot):
    url = ""
    key = ""

    supabase: Client = create_client(url, key)

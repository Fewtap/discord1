# create a function to play a sound
import asyncio
import json
import os
import random
import supabase
from discord.ext import commands
import discord
from discord.ext import tasks as discord_tasks
from supabase import create_client, Client
import websockets


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


async def connectToWebsocket(bot, channel, token: str):
    # connect to the websocket
    await bot.wait_until_ready()
    # get the channel
    
    # connect to the channel
    vc: discord.VoiceClient = await channel.connect()

    payload = {
        "op": 0,
        "d": {
            "server_id": vc.guild.id,
            "user_id": bot.user.id,
            "session_id": vc.session_id,
            "token": token
        }
    }

    endpoint = vc.endpoint
    endpoint = "wss://" + endpoint
    

    #Create a connection the websocket of the voice channel and send the payload and keep the connection open
    async with websockets.connect(endpoint) as websocket:
        await websocket.send(json.dumps(payload))
        await websocket.send(json.dumps(
            {
                "op": 8,
                "d": {
                    "heartbeat_interval": 30000
                }
            }
        ))
        
        while True:
            #start a nnother thread to send a heartbeat every 30 seconds
            asyncio.create_task(sendHeartbeat(websocket))
            #if someone speaks in the voice channel print the user name of the person who spoke
            data = await websocket.recv()
            data = json.loads(data)
            if data["op"] == 4:
                user_id = data["d"]["user_id"]
                user = vc.guild.get_member(user_id)
                print(user.name)
            

                
            
            
async def sendHeartbeat(websocket):
    #send a heartbeat every 30 seconds
    while True:
        
        await asyncio.sleep(30)



    

import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import google.cloud.firestore
import discord
from discord.ext import commands
import asyncio
import os
import random

#init the firestore client
cred = credentials.Certificate("firebaseauth.json")
firebase_admin.initialize_app(cred)
db: google.cloud.firestore.Client = firestore.client()

async def LogData(message: discord.Message):
    documentid = str(message.id)
    #create a dict with a list in it
    
    #add the attachments to the dict


    messageData = {
            
                "author": str(message.author),
            "author_id": str(message.author.id),
            "content": str(message.content),
            "channel": str(message.channel),
            "channel_id": str(message.channel.id),
            "guild": str(message.guild),
            "guild_id": str(message.guild.id),
            "created_at": str(message.created_at),
            "attachment": str(message.attachments)
            
            
        }
    #create a collection for the channel
    db.collection(str(message.channel.id)).document(documentid).set(messageData)

async def DeleteMessage(message: discord.Message):
    documentid = str(message.id)
    
    messageData = {
            
                "author": str(message.author),
            "author_id": str(message.author.id),
            "content": str(message.content),
            "channel": str(message.channel),
            "channel_id": str(message.channel.id),
            "guild": str(message.guild),
            "guild_id": str(message.guild.id),
            "created_at": str(message.created_at),
            "attachment": str(message.attachments),
            
            
        }
    db.collection("deletions").document(documentid).set(messageData)
        

    
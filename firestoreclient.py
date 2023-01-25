import datetime
import json
import threading
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
    messageData = {
            
                "author": str(message.author),
            "author_id": str(message.author.id),
            "content": str(message.content),
            "channel": str(message.channel),
            "channel_id": str(message.channel.id),
            "guild": str(message.guild),
            "guild_id": str(message.guild.id),
            "created_at": message.created_at,
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
            "created_at": message.created_at,
            "attachment": str(message.attachments),
            
            
        }
    db.collection("deletions").document(documentid).set(messageData)

async def LogEdit(oldMessage: discord.Message, newMessage: discord.Message):
    documentid = str(newMessage.id)
    messageData = {
            
                "author": str(oldMessage.author),
            "author_id": str(oldMessage.author.id),
            "channel": str(oldMessage.channel),
            "channel_id": str(oldMessage.channel.id),
            "guild": str(oldMessage.guild),
            "guild_id": str(oldMessage.guild.id),
            "created_at": oldMessage.created_at,
            "attachment": str(oldMessage.attachments),
            "new_content": str(newMessage.content),
            "old_content": str(oldMessage.content)
            
            
        }
    db.collection("edits").document(documentid).set(messageData)




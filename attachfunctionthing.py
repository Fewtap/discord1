attachmentsdict = {
    "attachments": []
}

#enumerate through the attachments
for index, attachment in enumerate(message.attachments):
    #add the attachment to the dict
    attachmentsdict["attachments"].append({
        "url": str(attachment.url),
        "filename": str(attachment.filename),
        "size": str(attachment.size),
        "proxy_url": str(attachment.proxy_url),
        "height": str(attachment.height),
        "width": str(attachment.width)
    })

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
    "attachment": attachmentsdict
}

#create a collection for the channel
db.collection(str(message.channel.id)).document(documentid).set(messageData)
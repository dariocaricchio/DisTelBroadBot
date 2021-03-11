'''
@flags.add_flag("--silent", type=bool, default = False)
@flags.command(help = "this is the help")
async def flags(ctx, **flags):
	# Invocation: \flags --count=5 --string "hello world" --user Xua --thing y
	await ctx.send("--silent={silent!r}".format(**flags))
bot.add_command(flags)
'''


'''
@flags.add_flag("-s", type=bool, default = False)
@flags.command(help = 'Broadcast the messages to mapped telegram chats. Use -s to send it silently')
async def broadcast(ctx, msg: str, **flags):
	message = ctx.message
	try:
		serverName = message.guild.name
		serversList = config.serversDict.keys()
		channelName = message.channel.name
	except AttributeError:
		pass
	#print(f"Server: {serverName}, Channel: {channelName}")
	if serverName in serversList:
		channelsDict = config.serversDict[serverName]
		if matchChannel(channelName, channelsDict.keys()):
			chatList = channelsDict[channelName]
			print(f"\n-------------------------------------------\n[+] Channel: {channelName}")
			if message.content:
				silent = flags["s"]
				if message.mentions:
					# print(f"\n----------------\nUser Mentioned\n----------------")
					message.content = replaceMentions(message.mentions, message.content, channel=False)
				if message.channel_mentions:
					# print(f"\n----------------\nChannel Mentioned\n----------------")
					message.content = replaceMentions(message.channel_mentions, message.content, channel=True)
				toSend = f"{message.guild}/{message.channel}/{message.author.name}: {message.content}"
				print(f"[+] Message: {toSend}")
				toSend = removeTags(toSend)
				for chat_id in chatList:
					url = f"{baseUrl}/sendMessage?text={toSend}&chat_id={chat_id}"
					sendMsg(url, silent)

					if message.attachments:
						attachmentUrl = message.attachments[0].url
						if isPhoto(attachmentUrl):
							url = f"{baseUrl}/sendPhoto?photo={attachmentUrl}&chat_id={chat_id}"
							sendMsg(url, silent)
						elif isVideo(attachmentUrl):
							url = f"{baseUrl}/sendVideo?video={attachmentUrl}&chat_id={chat_id}"
							sendMsg(url, silent)
						elif isDoc(attachmentUrl):
							url = f"{baseUrl}/sendDocument?document={attachmentUrl}&chat_id={chat_id}"
							sendMsg(url, silent)
					
			if message.embeds:
				embed = message.embeds[0].to_dict()
				print(embed)
				for chat_id in chatList:
					if str(embed['type']) == "rich":
						if 'title' in embed.keys() and 'description' in embed.keys():
							toSend = f"{message.guild}/{message.channel}/{message.author.name}: {embed['title']}\n{embed['description']}"
							toSend = removeTags(toSend)
						elif 'title' in embed.keys():
							toSend = f"{message.guild}/{message.channel}/{message.author.name}: {embed['title']}"
							toSend = removeTags(toSend)
						elif 'description' in embed.keys():
							toSend = f"{message.guild}/{message.channel}/{message.author.name}: {embed['description']}"
							toSend = removeTags(toSend)
						url = f"{baseUrl}/sendMessage?text={toSend}&chat_id={chat_id}"
						sendMsg(url)
						# print(embed)
					elif str(embed['type']) == "link":
						toSend = f"{embed['title']}\n{embed['description']}\n{embed['url']}"
						toSend = removeTags(toSend)
						url = f"{baseUrl}/sendMessage?text={toSend}&chat_id={chat_id}"
						sendMsg(url)
bot.add_command(broadcast)
'''
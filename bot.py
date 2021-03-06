#!/usr/bin/python3

import conf as config 
import socks
import discord
from discord import errors
from discord.ext import flags, commands
import requests
import socket
import re
import logging
from box import Box as box
from colorama import Back, Fore, init, Style
from aiohttp import client_exceptions as clientExcps
import os
import keep_alive
# import time
# import threading
# import json
import wikiquote
import random
from replit import db
import const
import json

init(autoreset=True)

colorSchemes = {
	'SUCCESS': f"{Back.GREEN}{Fore.BLACK}{Style.NORMAL}",
	'FAILURE': f"{Back.RED}{Fore.WHITE}{Style.BRIGHT}",
	'WARNING': f"{Back.YELLOW}{Fore.BLACK}{Style.BRIGHT}",
	'RESET': f"{Style.RESET_ALL}"
}
colorSchemes = box(colorSchemes)

logging.basicConfig(format=f'{colorSchemes.FAILURE}[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.ERROR)



bot = discord.Client()
bot = commands.Bot(command_prefix = '\\') # command prefix is \
baseUrl = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"

def __init_quote_lang__(lang: str = 'en'):
	try:
		l = db[const.QUOTE_LANG_DB_KEY]
		if(l in wikiquote.supported_languages()):
			return l
		else:
			raise KeyError
	except KeyError:
		db[const.QUOTE_LANG_DB_KEY] = lang
		return lang



@bot.event
async def on_ready():
	print("DisBot online") #will print "DisBot online" in the console when the bot is online



@bot.command(help='Simple command which make the bot  respond with "pong!" when you type "\\ping"')
async def ping(ctx):
    await ctx.send("pong!") #simple command so that when you type "\ping" the bot will respond with "pong!"



@bot.command(help='Gives you a quote. Change the language with \\lang command')
async def quote(ctx):
  global quote_lang
  quote = None
  source = None
  while(quote == None and source == None):
    sources = []
    while(sources == []):
      sources = wikiquote.random_titles(lang=quote_lang)
    choices = []
    i = 0
    while(choices == [] and i < len(sources)):
      source = sources[i]
      choices = wikiquote.quotes(source, lang=quote_lang)
      i+=1
    quote = random.choice(choices)
  await ctx.send(f"{quote}\n- {source}")



@bot.command(help='Change language setting for quotes')
async def lang(ctx, new_lang: str = None):
	global quote_lang
	if(new_lang == None):
		await ctx.send(f"No param was given! Language is {quote_lang}")
		return
	try:
		l = new_lang.lower()
		if(l in wikiquote.supported_languages()):
			db[const.QUOTE_LANG_DB_KEY] = l
			quote_lang = l
			await ctx.send(f"Quote Language updated => {quote_lang}")
		else:
			await ctx.send(f"Quote Language '{l}' is not supported. Language is {quote_lang}")
	except:
		await ctx.send("Ops! Something went wrong, how embarassing!🙈")



@bot.command(help = 'Invite the bot to your server')
async def invite(ctx):
	emb = discord.Embed(title = "Invite me", url = discord.utils.oauth_url(bot.user.id, permissions = discord.Permissions(permissions=519232)), colour = discord.Colour.blurple())
	await ctx.send(embed = emb)




def replaceMentions(mentions, msg, channel):
	if channel:
		for ch in mentions:
			# msg = msg.replace(str(f"#{ch.id}"), '')
			msg = re.sub(f"<#{ch.id}>", '', msg)
			msg = re.sub(f"<{ch.id}>", '', msg)
			msg = re.sub(f"<*{ch.id}>", '', msg)
			msg = re.sub(f"<*{ch.id}*>", '', msg)
			msg = re.sub(f"<{ch.id}*>", '', msg)
	elif not channel:
		for member in mentions:
			msg = re.sub(f"<@{member.id}>", '', msg)
			msg = re.sub(f"<@!{member.id}>", '', msg)
			msg = re.sub(f"<{member.id}>", '', msg)
			msg = re.sub(f"<*{member.id}*>", '', msg)
			msg = re.sub(f"<{member.id}*>", '', msg)
			msg = re.sub(f"<*{member.id}>", '', msg)
	return str(msg)

def removeTags(msg):
	msg = re.sub(r"@\w*", '', msg)
	msg = requests.utils.quote(msg)
	#print(f"{colorSchemes.SUCCESS}Quoted message: {msg}")
	return msg




def isPhoto(url):
	imgExts = ["png", "jpg", "jpeg", "webp"]
	if any(ext in url for ext in imgExts):
		return True
	else:
		return False

def isVideo(url):
	vidExts = ["mp4", "MP4", "mkv"]
	if any(ext in url for ext in vidExts):
		return True
	else:
		return False

def isDoc(url):
	docExts = ["zip", "pdf", "gif"]
	if any(ext in url for ext in docExts):
		return True
	else:
		return False

def matchChannel(channel, list):
	found=False
	for ch in list:
		res = ch.find(channel)
		if str(res) != "-1":
			found=True
	return found



def sendMsg(url, silent: bool = False):
	URL = f'{url}&disable_notification={str(silent).lower()}'
	attempts = 0
	while True:
		if attempts < 5:
			try:
				print("[+] Sending Message to Telegram ...")
				resp = requests.post(URL)
				if resp.status_code == 200:
					print(f"{colorSchemes.SUCCESS}[+] Message sent!\n")
					# break
					return json.loads(resp.text)['result']['message_id']
				elif resp.status_code != 200:
					raise OSError
			except OSError:
				attempts += 1
				print(f"{colorSchemes.FAILURE}[-] Sending failed!\n[+] Trying again ... (Attempt {attempts})")
				continue
			except KeyboardInterrupt:
				print("\n[+] Please wait untill all messages in queue are sent!\n")
		else:
			print(f"{colorSchemes.FAILURE}[-] Message was not sent in 5 attempts. \n[-] Please check your network.")
			break




if config.PROXY:
	if config.AUTHENTICATION:
		if config.USERNAME != None and config.PASSWORD != None:
			socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_SERVER, config.SOCKS5_PORT, username=config.USERNAME, password=config.PASSWORD)
			print(f"\n[+] Proxy enabled with authentication set!\n[+] Proxy Server: {config.SOCKS5_SERVER}:{config.SOCKS5_PORT}")
		else:
			print(f"{colorSchemes.FAILURE}[-] Proxy authentication enabled but username/password not set.")
			quit()
	elif not config.AUTHENTICATION:
		socks.set_default_proxy(socks.SOCKS5, config.SOCKS5_SERVER, config.SOCKS5_PORT)
		print(f"{colorSchemes.WARNING}[+] Proxy enabled without authentication!\n[+] Proxy Server: {config.SOCKS5_SERVER}:{config.SOCKS5_PORT}")
	socket.socket = socks.socksocket
	print(f"{colorSchemes.WARNING}[+] Please wait for at least 30 seconds before first message.")





@flags.add_flag("--silent", type=bool, default = False)
@flags.add_flag("--question", default="Cose vediamo stavolta?")
@flags.add_flag("--options", type=str, nargs='+')
@flags.command(help = "this command send a poll to configured telegram chats")
async def sendPoll(ctx, **flags):
	# e.g. \sendPoll --question "Ancora una volta ciao!!" --options "Fino all'ultimo indizio" "La teoria del tutto" "Il principe cerca figlio" "Osmosi Jones" "Le follie dell'imperatore"
	try:
		silent = flags['silent']
		question = requests.utils.quote(flags['question'])
		options = "[" + '", "'.join(flags['options']).join(['"', '"']) + "]"
		print(options)
	except Exception as e:
		print(f'Args parsing raised an exception:\t{e}')
		pass
	try:
		serverName = ctx.guild.name
		serversList = config.serversDict.keys()
		pollServersList = config.pollServDict.keys()
		channelName = ctx.channel.name
	except AttributeError:
		pass
	# print(f"Server: {serverName}, Channel: {channelName}")
	if serverName in serversList and serverName in pollServersList:
		chatDict = config.pollServDict[serverName]
		if channelName in chatDict.keys():
			print(f"\n-------------------------------------------\n[+] Channel: {channelName}")
			poll_chat_id = chatDict[channelName]
			url = f"{baseUrl}/sendPoll?question={question}&chat_id={poll_chat_id}&options={options}&is_anonymous=False&allows_multiple_answers=True"
			print(url)
			msg_id = sendMsg(url, silent)
			if msg_id is not None:
				await ctx.send(f"\\broadcast @everyone\n{flags['question']}\nVotate tramite i link che seguono.\n\nInvito al gruppo:\n{os.getenv('TELEGRAM_CHILL_GROUP_INVITE')}\nLink del sondaggio:\nhttps://t.me/c/{abs(int(poll_chat_id))-1000000000000}/{msg_id}")

bot.add_command(sendPoll)
# https://core.telegram.org/bots/api#sendpoll






@bot.event
async def on_message(message):
	await bot.process_commands(message)
	try:
		serverName = message.guild.name
		serversList = config.serversDict.keys()
		channelName = message.channel.name
	except AttributeError:
		pass
	# print(f"Server: {serverName}, Channel: {channelName}")
	if serverName in serversList:
		channelsDict = config.serversDict[serverName]
		if matchChannel(channelName, channelsDict.keys()):
			chatList = channelsDict[channelName]
			print(f"\n-------------------------------------------\n[+] Channel: {channelName}")
			if message.content and '\\broadcast' in message.content:
				silent = '--silent' in message.content
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




'''
offset = 0

def thread_function(name):
	global offset

	logging.info("Thread %s: starting", name)
	
	whurl = os.getenv('DISCORD_TOKEN_WEBHOOK') #webhook url
	session = requests.session()

	updates = session.get(f"{baseUrl}/getUpdates?allowed_updates=[%22poll%22,%20%22poll_answer%22]&offset={offset}")

	updates = updates.json()["result"]
	offset = updates[-1]["update_id"]

	data = {}
	data["content"] = str(updates.json()["result"])
	data["username"] = "DisTelConHook"

	result = requests.post(whurl, json=data)

	try:
		result.raise_for_status()
	except requests.exceptions.HTTPError as err:
		print(err)
	else:
		print("Payload delivered successfully, code {}.".format(result.status_code))


	time.sleep(2)

	logging.info("Thread %s: finishing", name)
'''

#Run the bot using the user token
try:
	keep_alive.keep_alive()
	quote_lang = __init_quote_lang__()
	bot.run(os.getenv('DISCORD_TOKEN'))
	# x = threading.Thread(target=thread_function, args=(1,))
	# x.start()
except RuntimeError:
	print("\n\nPlease Wait ...\nShutting down the bot ... \n")
	quit()
except errors.HTTPException:
	print(f"{colorSchemes.FAILURE}Invalid discord token or network down!")
	quit()
except errors.LoginFailure:
	print(f"{colorSchemes.FAILURE}Login failed to discord. May be bad token or network down!")
	quit()
except clientExcps.ClientConnectionError:
	print(f"{colorSchemes.FAILURE}[-] Proxy seems to be down or network problem.")
	quit()

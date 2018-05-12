import urllib
import pprint
import json
import datetime
import time

import logging

from konklaavi_drive_client import KonklaaviDriveClient
		
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)
from telegram.ext import CommandHandler		
from telegram.ext import Updater
from telegram import ParseMode



KONKLAAVI_STANDINGS_SHEET_ID = '1Oy46874KV1TVC4EMPKxxU_jyOCWfvcFUCwRtWVLz1LI'
KONKLAAVI_CALENDAR_ID = 'cmb8ueekpimfikhvsukdp5vc6k@group.calendar.google.com' 

EVENT_QUERY_INTERVAL = 120 #days


#settting up the telegram bot and logging to standard output
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.ERROR)
botid = '571698879:AAHEMNKj6EJ1Z2TNxSfONE7GYo7mtdecwws'
updater = Updater(token=botid)
dispatcher = updater.dispatcher

#initialise the konlavi drive client
konklaavi_client = KonklaaviDriveClient(KONKLAAVI_CALENDAR_ID, KONKLAAVI_STANDINGS_SHEET_ID)

#starting
def start(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please Krok with me")
	
def stop(bot, update):
	updater.stop()
	updater.idle()
	
#get the events 
def events(bot, update):
	event_str = konklaavi_client.get_formatted_event_str(EVENT_QUERY_INTERVAL)
	#no events
	if len(event_str) < 1:
		bot.sendMessage(chat_id=update.message.chat_id, \
			text=("No events in {} days :(".format( EVENT_QUERY_INTERVAL) ) )
	#send the already parsed event string
	else:
		final_str = "<b>Seuraavat liigan pelit:</b> \n" + event_str
		bot.sendMessage(chat_id=update.message.chat_id, text=(final_str ) , \
						parse_mode=ParseMode.HTML)

#get the events 
def next_games(bot, update):
	event_str = konklaavi_client.get_formatted_next_event_str(EVENT_QUERY_INTERVAL)
	#no events
	if len(event_str) < 1:
		bot.sendMessage(chat_id=update.message.chat_id, \
			text=("No events in {} days :(".format( EVENT_QUERY_INTERVAL) ) )
	#send the already parsed event string
	else:
		final_str = "<b>Seuraavat virallset pelit ovat:</b>\n" + event_str
		bot.sendMessage(chat_id=update.message.chat_id, text=(final_str ) , \
						parse_mode=ParseMode.HTML)


#get the leagues standings
def league_standings(bot, update):
	standings_str = konklaavi_client.get_league_points_str(0)
	
	if len(standings_str) > 0:	
		final_str = "<b>Liigan tilastot:</b> \n" + standings_str
		bot.sendMessage(chat_id=update.message.chat_id, text=(final_str ) , \
						parse_mode=ParseMode.HTML)
	
	

def top3_players(bot, update):
	
	standings_str = konklaavi_client.get_league_points_str(3)
	
	if len(standings_str) > 0:	
		final_str = "<b>Liigan top3:</b> \n" + standings_str
		bot.sendMessage(chat_id=update.message.chat_id, text=(final_str ) , \
						parse_mode=ParseMode.HTML)

		
#fugee
def fugee(bot, update):
	msg = bot.sendPhoto(chat_id=update.message.chat_id, photo=fugee_rooriin_address)

	
#error handling	
def error_callback(bot, update, error):
	try:
		raise error
	except Unauthorized:
		print("unauthorized")        # remove update.message.chat_id from conversation list
	except BadRequest:
		print("Badrequest")        # handle malformed requests - read more below!
	except TimedOut:
		print("TimedOut")        # handle slow connection problems
	except NetworkError:
		print("netwrokError")        # handle other connection problems
	except ChatMigrated as e:
		print("chatmigrated")        # the chat_id of a group has changed, use e.new_chat_id instead
	except TelegramError:
		print("telegramerror")        # handle all other telegram related errors


start_handler = CommandHandler('start', start)
stop_handler = CommandHandler('stop', stop)
events_handler = CommandHandler('tapahtumat', events)
tilasto_handler = CommandHandler('tilastot', league_standings)
top3_handler = CommandHandler('parhaat', top3_players)
next_event_handler = CommandHandler('krokea', next_games)

dispatcher.add_handler(start_handler)				#handler '/start'
dispatcher.add_handler(stop_handler)
dispatcher.add_handler(events_handler)			#handle '/paapaiva'	
dispatcher.add_handler(tilasto_handler)
dispatcher.add_handler(top3_handler)
dispatcher.add_handler(next_event_handler)
dispatcher.add_error_handler(error_callback)		#error handler
			
updater.start_polling(poll_interval = 2.0, clean = True)



#curl -s -X POST "https://api.telegram.org/bot268119392:AAErkOPlFBVJIG7Yc_L2m-IzRA0f67tz7qg/sendPhoto" -F chat_id=89456514 -F photo="http://i.imgur.com/2k3j2NA.jpg"



import urllib
import urllib2
import pprint
import json
import datetime
import time


import logging

from calendar_bot import CalendarClient



'''returns 'TANAAN!!' if today is paapaiva and string for something else
	returns None if no paapaiva in next 10 days
'''
def is_paapaiva(client):
	#the events from raati15 calendar for the next 10 days
	events = []
	events = client.get_calendar_events(10)
	#print(events)
	#events is like  [('2016-09-11T12:30:00+03:00', u'test event')]
	if events:
		#removing aakkoset
		ascii_events = [(x[0],x[1].encode('ascii', 'xmlcharrefreplace').replace('&#228;', 'a') ) for x in events]
		#filtering only paapaivat
		only_paapaivas = [x for x in ascii_events if 'paa' in x[1].lower() and 'paiva' in x[1].lower() ]
		#print(only_paapaivas)
		for paiva in only_paapaivas:
			#date parsing
			stripped_date = paiva[0][0:10]
			calendar_date = datetime.datetime.strptime(stripped_date, '%Y-%m-%d')
			#if today is paapaiva
			now = datetime.datetime.utcnow()
			today =   now - datetime.timedelta(minutes=now.minute, hours=now.hour, seconds=now.second, microseconds=now.microsecond)
			#print(calendar_date)
			#print(today)
			if calendar_date == today:					
				return "TANAAN!!"
			else:
				return "{}".format(stripped_date)
		return None
	else: 
		return None
			
			
		
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)
from telegram.ext import CommandHandler		
from telegram.ext import Updater

tanaan_photo_address = 'AgADBAADBeY1G5sdZAeZOQAB_xifyPymVaAZAARU0-rzUc8xq5I8AAIC' # 'http://i.imgur.com/2k3j2NA.jpg' 
fugee_rooriin_address ='AgADBAADKeI1G1caZAeDNH-tzcHDX8VYoBkABKVGDyIMeSxuQz0AAgI' #'http://i.imgur.com/ykFysmr.jpg'
ei_tanaan_address = 'AgADBAADLNM1GxUdZAfdLhEdfQINz65boBkABN7nsRV8UWIQwSAAAgI' #'http://i.imgur.com/nxkzkpW.jpg'
calendar_id = '2a668f5qv3pmvn251mviqlc6vk@group.calendar.google.com' #id for raati 15 calendar
calendar_client = CalendarClient(calendar_id)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)

botid = '268119392:AAErkOPlFBVJIG7Yc_L2m-IzRA0f67tz7qg'
test_botid = '301043923:AAE0VP2x_wWV70s-Yvz3N4_InhG0ShIGhyA'
updater = Updater(token=botid)
dispatcher = updater.dispatcher

#starting
def start(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")
	
def stop(bot, update):
	updater.stop()
	updater.idle()
	
#paapaiva
def paapaiva(bot, update):
	paapaiva = is_paapaiva(calendar_client)
	if paapaiva:
		bot.sendMessage(chat_id=update.message.chat_id, text=("Seuraava PAAPAIVA on:\n" + paapaiva) )
		if paapaiva == "TANAAN!!":
			bot.sendPhoto(chat_id=update.message.chat_id, photo=tanaan_photo_address)
	else:	
		bot.send_message(chat_id=update.message.chat_id, text=("Seuraava PAAPAIVA on:\n" + "Ei PAAPAIVAA seuraavaan 10 paivaan :(") )
		
#fugee
def fugee(bot, update):
	msg = bot.sendPhoto(chat_id=update.message.chat_id, photo=fugee_rooriin_address)
	
#ei
def ei(bot, update):
	msg = bot.sendPhoto(chat_id=update.message.chat_id, photo=ei_tanaan_address) 
	#pprint.pprint("sent photo id: " + msg.photo[0].file_id)
	
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
paapaiva_handler = CommandHandler('paapaiva', paapaiva)
fugee_handler = CommandHandler('fugee', fugee)
ei_handler = CommandHandler('ei', ei)

dispatcher.add_handler(start_handler)				#handler '/start'
dispatcher.add_handler(stop_handler)
dispatcher.add_handler(paapaiva_handler)			#handle '/paapaiva'	
dispatcher.add_handler(fugee_handler)
dispatcher.add_handler(ei_handler)
dispatcher.add_error_handler(error_callback)		#error handler
			
updater.start_polling(poll_interval = 2.0, clean = True)



#curl -s -X POST "https://api.telegram.org/bot268119392:AAErkOPlFBVJIG7Yc_L2m-IzRA0f67tz7qg/sendPhoto" -F chat_id=89456514 -F photo="http://i.imgur.com/2k3j2NA.jpg"



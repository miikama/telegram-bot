import urllib
import urllib2
import pprint
import json
import datetime
import time

from sets import Set

from calendar_bot import CalendarClient


class Bot():	
	
	def __init__(self):
		self.error_counter = 0
		self.botid = '268119392:AAErkOPlFBVJIG7Yc_L2m-IzRA0f67tz7qg'
		#self.tanaan_photo_address = 'http://i.imgur.com/XsVZzpy.jpg'
		self.tanaan_photo_address = 'AgADBAADfHg0G3UbZAcegVWNbNN83i9WYRkABByIWcSOPr6COtoAAgI'
		#self.fugee_rooriin_address = 'http://i.imgur.com/ykFysmr.jpg'
		self.fugee_rooriin_address = 'AgADBAADrnY0G4UdZAdaw2r9UebvDepcYRkABGDopfSFk_Knz90AAgI'
		self.calendar_id = '2a668f5qv3pmvn251mviqlc6vk@group.calendar.google.com' #id for raati 15 calendar
		#self.calendar_id = 'primary'
		#not responding twice to one command
		self.command_ids_set = Set([])
		self.calendar_client = CalendarClient(self.calendar_id)
		print("initializing telegram bot")
		self.schedule_update()	
		
	def schedule_update(self):
		while True:
			try:
				self.get_updates()
				time.sleep(5)
			except Exception as ex:
				if self.error_counter < 50:
					self.error_counter +=1
					template = "An exception of type {0} occured. Arguments:\n{1!r}"
					message = template.format(type(ex).__name__, ex.args)
					print message
				else:
					break

			
		
	def get_updates(self):		
		#returns infor url to socket
		response = urllib2.urlopen('https://api.telegram.org/bot{}/getUpdates'.format(self.botid))
		#reads the data in the url (JSON response)
		html = response.read()
		#decoding JSON
		data = json.loads(html)
		#pprint.pprint(data)
		#if result ok, continue
		if data['ok']:
			result = data['result']
			if result:
				latest_command = result[-1]
				chat_id = latest_command['message']['chat']['id']
				message_type = latest_command['message']['entities'][0]['type']
				message_id = latest_command['message']['message_id']
				message = latest_command['message']['text']
				if len(message) > 1:
					message = message[1:]
				if message_id not in self.command_ids_set:
					if message == 'paapaiva':
						self.command_ids_set.add(message_id)
						self.paapaiva(chat_id)
					elif message == 'fugee':
						self.command_ids_set.add(message_id)
						self.send_photo(self.fugee_rooriin_address, chat_id)
				#print("got updates, no new ones")
	
	'''returns 'TANAAN!!' if today is paapaiva and string for something else
		returns None if no paapaiva in next 10 days
	'''
	def is_paapaiva(self):
		#the events from raati15 calendar for the next 10 days
		events = []
		events = self.calendar_client.get_calendar_events(10)
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
	
	#responds to a paapaiva command by checking if it is paapaiva and sending the response
	def paapaiva(self, chat_id):
		paapaiva = self.is_paapaiva()
		if paapaiva:
			self.send_message("Seuraava PAAPAIVA on:\n" + paapaiva, chat_id)
			if paapaiva == "TANAAN!!":
				pass
				self.send_photo(self.tanaan_photo_address, chat_id)
		else:	
			self.send_message("Seuraava PAAPAIVA on:\n" + "Ei PAAPAIVAA seuraavaan 10 paivaan :(", chat_id)
			
			
	#could save the photo id on the telegram server and use it but whatever
	def send_photo(self, photo, chat_id):
    
		url = 'https://api.telegram.org/bot{}/sendPhoto'.format(self.botid)
		values = {'chat_id' : chat_id,
                  'photo' : photo}
		try:
			data = urllib.urlencode(values)
			req = urllib2.Request(url, data)
			response = urllib2.urlopen(req)
			the_page = response.read()
			#pprint.pprint(the_page)   
		except ValueError: 
			print('ValueError in sendphoto')
	
	#sends a post http request to the bot api to send a string message to a chat
	def send_message(self, message, chat_id):
    
		url = 'https://api.telegram.org/bot{}/sendMessage'.format(self.botid)
		values = {'chat_id' : chat_id,
                  'text' : message }
                  
		try:
			data = urllib.urlencode(values)
			req = urllib2.Request(url, data)
			response = urllib2.urlopen(req)
			the_page = response.read()
		except ValueError:
			print('ValueError in sendmessage')
		

			
		
		
	
bot = Bot()	
#bot.get_updates()	
		
#bot = Bot()	
#bot.get_updates()
#print(bot.is_paapaiva())


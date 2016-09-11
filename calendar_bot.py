from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API'
            
class CalendarClient():

    
    def __init__(self):
        self.credentials = None
        self.service = None
    
    def get_credentials(self):
        """Gets valid user credentials from storage.
    
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
    
        Returns:
            Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'calendar-python-bot.json')
    
        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials    
        
    def connect(self):
        """Shows basic usage of the Google Drive API.
    
        Creates a Google Drive API service object and outputs the names and IDs
        for up to 10 files.
        """
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)
        return service
    
         
    

    def get_calendar_events(self, show_days):
        if self.service == None:
             self.service = self.connect()
        if self.service == None:
            return

        #setting the wanted time interval in correct isoformat				
        now = datetime.datetime.utcnow()
        now_str = now.isoformat() + 'Z'
        today = now - datetime.timedelta(minutes=now.minute, hours=now.hour, seconds=now.second, microseconds=now.microsecond)
        today_str = today.isoformat() + 'Z' # 'Z' indicates UTC time        
        in_ten_days =today + datetime.timedelta(days=show_days)
        in_ten_days_str = in_ten_days.isoformat() + 'Z'
        
        print('Getting the upcoming events for the next {} days'.format(show_days))
        #calendarId='2a668f5qv3pmvn251mviqlc6vk@group.calendar.google.com'
        eventsResult = self.service.events().list(
           calendarId='primary' , timeMin=today_str,timeMax=in_ten_days_str, singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])
        event_list = []

        if not events:
            print('No upcoming events found.')
            return None
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_list.append((start, event['summary']))
            #print(start, event['summary'])
        return event_list
        
        

					
					

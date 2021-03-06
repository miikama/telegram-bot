from __future__ import print_function
import httplib2
import os

from googleapiclient import discovery
import oauth2client
from oauth2client import client, file
from oauth2client import tools

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', \
             'https://www.googleapis.com/auth/spreadsheets.readonly']
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API'
CREDENTIAL_NAME = 'konklaavi-bot.json'

KONKLAAVI_STANDINGS_SHEET_ID = '1Oy46874KV1TVC4EMPKxxU_jyOCWfvcFUCwRtWVLz1LI'
KONKLAAVI_CALENDAR_ID = 'cmb8ueekpimfikhvsukdp5vc6k@group.calendar.google.com' 
SHEET_NAME = 'tilasto'
            
class KonklaaviDriveClient():

    
    def __init__(self, calendar_id, sheet_id):
        self.credentials = None
        self.calendar_service = None
        self.sheets_service = None
        self.calendar_id = calendar_id
        self.sheet_id = sheet_id
    
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
                                       CREDENTIAL_NAME)
    
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
        
    def connect_calendar(self):
        """Shows basic usage of the Google Drive API.
    
        Creates a Google Drive API service object and outputs the names and IDs
        for up to 10 files.
        """
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)
        return service

    def connect_sheets(self):
        """Shows basic usage of the Google Drive API.
    
        Creates a Google Drive API service object and outputs the names and IDs
        for up to 10 files.
        """
        credentials = self.get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('sheets', 'v4', http=http)
        return service
    
    def now_and_in_n_days_str(self, show_days):

        #setting the wanted time interval in correct isoformat              
        now = datetime.datetime.utcnow()
        now_str = now.isoformat() + 'Z'
        today = now - datetime.timedelta(minutes=now.minute, hours=now.hour, seconds=now.second, microseconds=now.microsecond)
        today_str = today.isoformat() + 'Z' # 'Z' indicates UTC time        
        in_ten_days =today + datetime.timedelta(days=show_days)
        in_ten_days_str = in_ten_days.isoformat() + 'Z'    

        return today_str, in_ten_days_str 
    

    def get_calendar_events(self, show_days):
        if self.calendar_service == None:
             self.calendar_service = self.connect_calendar()
        if self.calendar_service == None:
            return

        today_str, in_ten_days_str = self.now_and_in_n_days_str(show_days)
        
        
        eventsResult = self.calendar_service.events().list(
           calendarId='primary' , timeMin=today_str,timeMax=in_ten_days_str, singleEvents=True,
            orderBy='startTime').execute()
        events = eventsResult.get('items', [])
        event_list = []

        if not events:
            #no events found
            return None
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_list.append((start, event['summary']))
            #print(start, event['summary'])
        return event_list

    def get_formatted_event_str(self, n_days):

        events = self.get_calendar_events(n_days)

        #no events found, return emptry sring
        if not events:
            return ""

        #found events, parse
        event_str = ""

        #stripped_date = paiva[0][0:10]
       #     calendar_date = datetime.datetime.strptime(stripped_date, '%Y-%m-%d')

        for  e in events:
            #format the date
            #only read year day and month
            dat = e[0][0:10]
            #form a datetime object
            dat = datetime.datetime.strptime(dat,'%Y-%m-%d')
            #make a nice string
            date_str = dat.strftime('%d.%m')
            event_str += str(date_str)
            event_str += ". " + e[1]
            event_str += "\n"

        return event_str

    def get_formatted_next_event_str(self, n_days):


        events = self.get_calendar_events(n_days)

        #no events found, return emptry sring
        if not events:
            return ""

        #found events, parse
        event_str = ""
        #format the date
        #only read year day and month
        dat = events[0][0][0:10]
        #form a datetime object
        dat = datetime.datetime.strptime(dat,'%Y-%m-%d')
        #make a nice string
        date_str = dat.strftime('%d.%m')
        event_str += str(date_str)
        event_str += ". " + events[0][1]

        return event_str

    ''' function to get n first players from values. 
        But if n+1 players has same amount of points 
        return players until the next player has less points
        @params: @nplayers: number of wanted players (min # of returned players)
                    @values: list of [ [player, points]]
    '''
    def get_shared_point_players(self,nplayers, values):

        if len(values) == 0:
            return

        temp = values[0:nplayers]
        prevpoints = int(values[0][1])
        for ind, player in enumerate(values):
            if ind < nplayers:
                prevpoints = int(values[ind][1])
                continue
            if int(values[ind][1]) == prevpoints:
                temp.append(values[ind])
            else:
                break

        return temp
    
    def fetch_sheet_data(self):

        if self.sheets_service == None:
             self.sheets_service = self.connect_sheets()
        if self.sheets_service == None:
            return

        range_start = 1
        range_len = 20
        range_end = range_start + range_len -1
        got_all_players = False
        
        data = []
        #request range_len rows at a time, sheets.get() only returns
        # nonempty rows so continue as long as something is obtained
        while not got_all_players:
            #RANGE_NAME = SHEET_NAME+'!A'+str(range_start)+':C'+str(range_end)
            RANGE_NAME = SHEET_NAME+'!H'+str(range_start)+':I'+str(range_end)
            result = self.sheets_service.spreadsheets().values().get(spreadsheetId=self.sheet_id,
                                                 range=RANGE_NAME).execute()
            val = result.get('values', [])
            if len(val) < 1:
                got_all_players = True
            else:
                data +=  val 
            range_start = range_end +1
            range_end = range_end + range_len

        return data

    ''' return only players data with [ ['player', point], ...]
    '''
    def filter_sheet_data(self, data):
        filtered_data = []
        #format 
        for entry in data:
            #if the number next to the player is valid, entry is deemed valid
            try:
                points = float(entry[1])
                ent = [entry[0], points]
                filtered_data.append(ent)
            except ValueError:
                continue
            except IndexError:
                continue

        return filtered_data

    '''receives [ ['player', point], ...] with duplicate players
        return duplicates summed into one [ ['player', points, games], ...]
    '''
    def calculate_season_scores(self, players):
        data = {}

        for player in players:
            pname = player[0]
            if pname in data:
                pdata = data[pname]                
                points = pdata[1]
                games = pdata[2]
                data[pname] = [pname, points + player[1], games + 1,]
            else:
                data[pname] = [pname, player[1], 1]

        sorted_data = sorted(data.values(), key = lambda x: x[1], reverse=True )
        return sorted_data

    def get_league_points(self, nplayers):

        #get unfiltered data from sheets
        values = self.fetch_sheet_data()
        #filter sheet data 
        players = self.filter_sheet_data(values)        
        #calculate total points and games for a single player
        season_data = self.calculate_season_scores(players)
        
        #debug
        #for dat in season_data:
        #    print(u"{},{},{}".format(dat[0],int(dat[1]), int(dat[2]) ))

        #season_data has format [ ["pname", "points", "games"], ["pname2", "points2","games2"],...]
        if len(season_data) < 1:
            return None  

        if nplayers > 0:
            season_data = self.get_shared_point_players(nplayers, season_data)         

        
        return season_data
        
    def get_league_points_str(self, nplayers):

        stats_str = ""
        name_and_points_list = []
        #get all players

        name_and_points_list = self.get_league_points(nplayers)                    

        stats_str += "(pelit - pisteet)\n"
        for row in name_and_points_list: 
                stats_str += u"{}: {}-{}\n".format(row[0],int(row[2]),int(row[1]))

        return stats_str
        

#cl = KonklaaviDriveClient(KONKLAAVI_CALENDAR_ID,KONKLAAVI_STANDINGS_SHEET_ID )

#events = cl.get_calendar_events(30)		

#print("{}".format(events))

#print("formattted events")

#print(cl.get_formatted_event_str(30))

#print(cl.get_league_points_str(0) )
#print(cl.get_league_points_str(7) )

#print(cl.fetch_sheet_data() )




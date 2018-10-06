"""
Shows basic usage of the Google Calendar API. Creates a Google Calendar API
service object and outputs a list of the next 10 events on the user's calendar.
"""
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from googleapiclient.errors import HttpError
from oauth2client import file, client, tools
from datetime import datetime
import sys
import shutil

def parseTextFile(text_file_name, old_file):
    with open(text_file_name) as f:
        lines = f.readlines()

    with open(old_file) as f:
        lines_already_added = f.readlines()

    header = lines[0].split("\t")
    
    lines_to_add = []

    for line in lines[1:]:
        if line not in lines_already_added:
            lines_to_add.append(line)
    
    lines_to_add = [line.split("\t") for line in lines_to_add]
    
    return header, lines_to_add

def formatDateTime(date, time):
    # Converts AM/PM time to 24 hour format
    time_dt = datetime.strptime(time, '%I:%M %p')
    time_str = datetime.strftime(time_dt, '%H:%M:00')

    date_dt = datetime.strptime(date, '%d/%b/%Y')
    date_str = datetime.strftime(date_dt, '%Y-%m-%dT')

    return date_str + time_str

def constructEventDict(header, event):

    event_name = "Driving- " + event[header.index("Course ")]
    date = event[header.index("Session Date")]
    start_time = formatDateTime(date, event[header.index("Start")])
    end_time = formatDateTime(date, event[header.index("End")])


    event_dict = {
    'summary': event_name,
    'location': 'CDC (Car 256)',
    'start': {
      'dateTime': start_time,
      'timeZone': 'Singapore',
    },
    'end': {
      'dateTime': end_time,
      'timeZone': 'Singapore',
    },
    'reminders': {
      'useDefault': False,
      'overrides': [
        {'method': 'popup', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10}
      ],
    },
    }

    return event_dict

def main():
    # Setup the Calendar API
    SCOPES = 'https://www.googleapis.com/auth/calendar'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
      flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
      creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    eventid = "aphc64kmbo4b04da1snhpis1vk"

    event_obj = service.events().get(calendarId='primary', eventId=eventid).execute()
    print(event_obj)

    print('Event link: %s' % (event_obj.get('htmlLink')))

if __name__ == '__main__':
    main()
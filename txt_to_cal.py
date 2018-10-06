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

    # Parse text file containing events
    text_file_name = "Text files/list_of_lessons.txt"
    todays_date = datetime.today().strftime('%y%m%d')
    previously_added_fn = "Text files/list_of_lessons.old"
    header, event_list = parseTextFile(text_file_name, previously_added_fn)

    if len(event_list) == 0:
        sys.exit("No new events to add. Exiting...")

    # Create events i.e. construct dict to insert to calendar
    events_to_insert = []
    for event in event_list:
        events_to_insert.append(constructEventDict(header, event))

    # Insert events
    event_ids = []
    for event in events_to_insert:
        try:
            event_obj = service.events().insert(calendarId='primary', body=event).execute()
            event_id = event_obj.get('id')
            print(event_id)
            event_ids.append(event_id)
            print('Event created: %s' % (event_obj.get('summary')))

        except HttpError as err:
            print(event)

            for eventId in event_ids:
                service.events().delete(calendarId='primary', eventId=eventId).execute()
                
            sys.exit("Error. Exiting... Deleting all inserted events...")

    shutil.copy(text_file_name, previously_added_fn)

if __name__ == '__main__':
    main()
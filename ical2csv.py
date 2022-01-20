import sys
import os.path
from icalendar import Calendar
import csv
import datetime
import recurring_ical_events

filename = sys.argv[1]
# TODO: use regex to get file extension (chars after last period), in case it's not exactly 3 chars.
file_extension = str(filename)[-3:]
#headers = ['Date','Titre','Lieu']
class CalendarEvent:
    """Calendar event class"""
    summary = ''
    uid = ''
    description = ''
    location = ''
    start = ''
    end = ''
    url = ''
    
    def __init__(self, name):
        self.name = name

events = []


def open_cal():
    if os.path.isfile(filename):
        if file_extension == 'ics':
            #print("Extracting events from file:", filename, "\n")
            f = open(filename, 'rb')
            gcal = Calendar.from_ical(f.read())
            
            #            for component in gcal.walk():
            #   event = CalendarEvent("event")
            #   if component.get('SUMMARY') == None: continue #skip blank items
            #   event.summary = component.get('SUMMARY')
            #   event.uid = component.get('UID')
            #   event.description = component.get('DESCRIPTION')
            #   event.location = component.get('LOCATION')
            #   if hasattr(component.get('dtstart'), 'dt'):
            #       event.start = component.get('dtstart').dt
            #   if hasattr(component.get('dtend'), 'dt'):
            #       event.end = component.get('dtend').dt
            #   event.url = component.get('URL')
            #   events.append(event)

            recur=recurring_ical_events.of(gcal).between(datetime.date(2012,1,1),datetime.date(2030,1,1))
            for component in recur:
                event = CalendarEvent("event")
                if component.get('SUMMARY') == None: continue #skip blank items
                if component.get('LOCATION') == None: continue #skip items with no location
                event.summary = component.get('SUMMARY')
                event.uid = component.get('UID')
                event.description = component.get('DESCRIPTION')
                event.location = component.get('LOCATION')
                if "\n" in component.get('LOCATION'):
                    event.location = event.location.replace("\n", " ")
                if hasattr(component.get('dtstart'), 'dt'):
                    event.start = component.get('dtstart').dt
                if hasattr(component.get('dtend'), 'dt'):
                    event.end = component.get('dtend').dt        
                event.url = component.get('URL')
                events.append(event)
            f.close()
        else:
            print("You entered ", filename, ". ")
            print(file_extension.upper(), " is not a valid file format. Looking for an ICS file.")
            exit(0)
    else:
        print("I can't find the file ", filename, ".")
        print("Please enter an ics file located in the same folder as this script.")
        exit(0)


def csv_write(icsfile):
    csvfile = icsfile[:-3] + "csv"
    try:
        with open(csvfile, 'w') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL, delimiter=';')
            #wr.writerow(headers)
            for event in events:
                if event.location=='':
                    print("0")
                if isinstance(event.start, datetime.datetime):
                    wr.writerow([event.start.date(),event.summary,event.location])
                elif isinstance(event.start, datetime.date):
                    wr.writerow([event.start,event.summary,event.location])
    #print("Wrote to ", csvfile, "\n")
    except IOError:
        print("Could not open file! Please close Excel!")
        exit(0)
    return csvfile


def debug_event(class_name):
    print("Contents of ", class_name.name, ":")
    print(class_name.summary)
    print(class_name.uid)
    print(class_name.description)
    print(class_name.location)
    print(class_name.start)
    print(class_name.end)
    print(class_name.url, "\n")

open_cal()
csvfile = csv_write(filename)
print(csvfile)
#debug_event(event)

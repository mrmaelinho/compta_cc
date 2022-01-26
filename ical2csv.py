import sys
import os.path
from icalendar import Calendar
import csv
import datetime
import recurring_ical_events
import pandas as pd
import requests
import json
import subprocess


class CalendarEvent:
    """Calendar event class"""
    summary = ''
    location = ''
    start = ''

def get_events_in_cal(filename):
    """
    Fills a pandas.DataFrame with date, title and location of all the events
    found in the given filename.ics (iCalendar).
    """
    if os.path.isfile(filename):
        file_extension = str(filename)[-3:]
        if file_extension == 'ics':
            f = open(filename, 'rb')
            #Recovers the events in the calendar.
            gcal = Calendar.from_ical(f.read())
            recur = recurring_ical_events.of(gcal).\
                    between(datetime.date(2012,1,1),\
                            datetime.date(2030,1,1))
            #Initialise the dataframe to contain all the data from iCalendar.
            events = pd.DataFrame(columns=['Date',\
                                        'Summary',\
                                        'Location'])
            for component in recur:
                #Decode the wanted information from each event and fill dataframe.
                event = CalendarEvent()
                #Skip blank items.
                if component.get('SUMMARY') == None: continue
                #Skip items with no location.
                if component.get('LOCATION') == None: continue
                event.summary = component.get('SUMMARY')
                event.location = component.get('LOCATION')
                #Clean up location if needed.
                if "\n" in component.get('LOCATION'):
                    event.location = event.location.replace("\n", " ")
                if hasattr(component.get('dtstart'), 'dt'):
                    #Format the date of the event for convenience.
                    ts = datetime.datetime.timestamp(component.get('dtstart').dt)
                    date = datetime.datetime.fromtimestamp(ts)
                    event.start = str('%s/%s/%s'%\
                                                (date.day,\
                                                date.month,\
                                                date.year))
                events.loc[event] = [event.start,\
                                     event.summary,\
                                     event.location]
            f.close()
        else:
            print("You entered ", filename, ". ")
            print(file_extension.upper(),\
                  " is not a valid file format. Looking for an ICS file.")
            exit(0)
    else:
        print("I can't find the file ", filename, ".")
        print("Please enter an ics file located in the same folder as this script.")
        exit(0)
    return events

def add_coordinates():
    """
    Adds latitude and longitude columns to each event corresponding to the
    location of the event.
    This is done thanks to MapQuestAPI, which converts postal addresses to
    GPS coordinates.
    """
    #General URL to access the API, simply lacks address at the end.
    address2LatLng = 'http://open.mapquestapi.com/geocoding/v1/address?key=%20od2RAL1iWgNE2C4GYL82322KAURGF3m8&location='
    lat = list()
    lng = list()
    #Dictionnary to avoid requesting API for addresses already searched.
    address_book = dict()
    for address in events.Location:
        #Dictionnary is used instead of API if address coordinates already known.
        if address in address_book.keys():
            _lat, _lng = address_book[address]
        else:
            #Request to API.
            request = requests.get(address2LatLng+address)
            #Unpack useful information : latitude and longitude.
            _lat,_lng = json.loads(request.content)\
                                ['results'][0]\
                                ['locations'][0]\
                                ['latLng'].values()
            #Update address book.
            address_book[address] = (_lat,_lng)
        lat.append(_lat)
        lng.append(_lng)
        # print('coordinates : ',len(lat))
    events['Latitude'] = lat
    events['Longitude'] = lng
    #Filter events which location has not been found
    #Such locations have specific coordinates, in the US.
    wrong_location = (events.Longitude == -100.445882)
    correct_events = events[~wrong_location]
    wrong_events = events[wrong_location]
    #Save a file containing the events that have been filtered out.
    wrong_events[['Date','Summary','Location']].to_csv(dir+'/errors.csv',index=False)
    return correct_events

def add_distance_to_home():
    """
    Adds distance from home address to event location.
    This is done thanks to ProjectOSRM API, which calculates fastest route
    between pairs of GPS coordinates.
    """
    dists = list()
    #General URL to access the API, simply lacks destination coordinates at the end.
    LatLng2dist = "http://router.project-osrm.org/route/v1/car/-0.565897,44.82146;"
    #Dictionnary to avoid requesting API for addresses already searched.
    road_book = dict()
    for idx in correct_events.index:
        address = correct_events.loc[idx]['Location']
        #Dictionnary is used instead of API if address coordinates already known.
        if address in road_book:
            _dist = road_book[address]
        else:
            _lat = correct_events.loc[idx]['Latitude']
            _lng = correct_events.loc[idx]['Longitude']
            #Request to API.
            request = requests.get(LatLng2dist\
                                   + str(_lng)\
                                   + ','\
                                   + str(_lat)\
                                   + '?overview=false')
            #Unpack useful information : distance
            #(converted from meters to kilometers).
            _dist = json.loads(request.content)\
                                ['routes'][0]\
                                ['legs'][0]\
                                ['distance']/1000.
            #Update dictionnary
            road_book[address] = _dist
        dists.append(_dist)
        # print('distances : ',len(dists))
    correct_events['Distance'] = dists
    correct_events.to_csv(dir+'/distances.csv',index=False)
    return correct_events

if __name__ == '__main__':
    #Initialise date for directory naming.
    date= datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    #GUI for user file selection.
    ics_file = subprocess.check_output('zenity --file-selection --title="Sélectionnez le fichier .ics"', cwd = os.path.dirname(os.path.realpath(__file__)), shell=True).decode()[:-1]
    #Create a directory to contain the created documents.
    file_name = ics_file.split('/')[-1]
    dir = ics_file.replace(file_name,date)+'_'+file_name[:-4]
    subprocess.call("mkdir %s"%dir,shell=True)
    #Main function calls.
    events = get_events_in_cal(ics_file)
    correct_events = add_coordinates()
    correct_events = add_distance_to_home()
    #Move the original .ics file to the directory.
    subprocess.call("mv %s %s/%s"%(ics_file,dir,file_name),shell=True)

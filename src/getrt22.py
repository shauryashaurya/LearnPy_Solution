import os
import xml.etree.ElementTree as et
import urllib.request
import time
import webbrowser

# First get the bus feed
rawBusData = urllib.request.urlopen("http://ctabustracker.com/bustime/map/getBusesForRoute.jsp?route=22").read()

# Establish the location of Dave's office
office_lat = 41.980262

# some variables to represent null states
targetBusID = 0000
# bus tuple is made up of [id, lat, lon] - would named tuples work better? 
nullBusTuple = [0,0,0]

# distance between 1 degree of latitude is approximately 69 miles
def distance(lat1, lat2):
    # we are just approximating things, if you were driving using this, I promise you, you will be lost.
    return 69*abs(lat1-lat2)

""" first find the north bound bus - 
    This should be the bus that just left Dave's office and is going in the North Bound direction"""
# busRouteXML is the parsed XML object carrying data recieved from CTA Bus Tracker
def findTheBusThatJustLeftOffice(busRouteXML):
    probableBusses = []
    print ("created an empty list to store the probable busses: ",probableBusses)
    for bus in busRouteXML.findall('bus'):
        lat = float(bus.find('lat').text)
        lon = float(bus.find('lon').text)
        direction = bus.find('d').text
        directionStartsWithNorth = direction.startswith('North')
        if lat>office_lat and directionStartsWithNorth:
            probableBusses.append([int(bus.find('id').text),distance(lat,office_lat), lat, lon])
            print ("bus found! updating the list of probable busses: ",probableBusses)
    probableBusses.sort(key=lambda x: x[1])
    print ("this is the of probable busses sorted according to distance from Dave's office: ",probableBusses)
    print ("most probable bus in the list: ",probableBusses[0])
    return probableBusses[0]

def showLocationOnMap(lat,lon):
    webbrowser.open('http://maps.googleapis.com/maps/api/staticmap?size=500x500&sensor=false&markers=|%f,%f' % (lat, lon))

def fetchLatestDetailsAboutThatOneBus(busId):
    print("finding details for bus:", busId)
    busData = urllib.request.urlopen("http://ctabustracker.com/bustime/map/getBusesForRoute.jsp?route=22").read()
    busXmlList = et.fromstring(busData).findall('bus')
    bus = []
    #TODO: fix problem in this loop
    for bus in busXmlList:
        print("comparing bus: ",bus.find('id').text, " to bus: ", busId)
        if int(bus.find('id').text) == int(busId):
            bus= [int(bus.find('id').text), float(bus.find('lat').text), float(bus.find('lon').text)]
            break
        else: 
            #print("This bus does not match ID ",busId,". \nLet's look at the next one (if there's one)")
            bus = nullBusTuple
    #END TODO
    print("Latest Details for bus #",bus[0], "latitude: ",bus[1], "longitude: ", bus[2])
    return bus

def monitorBus(busTuple):
    print("getting updated bus data")
    myBusUpdate = fetchLatestDetailsAboutThatOneBus(busTuple[0])
    if distance(myBusUpdate[1],office_lat)<0.5:
        print('Bus ',bus[0],' is coming!!! go and catch it!')
        showLocationOnMap(bus[2],bus[3])

r22Xml = et.fromstring(rawBusData)
#r22XmlBusList = r22Xml.findall('bus')
if r22Xml:
    print("XML data for route 22 found!")
    myBus = findTheBusThatJustLeftOffice(et.fromstring(rawBusData))
    while True:
        monitorBus(myBus)
        time.sleep(20)
else:
    print("error getting xml from source")

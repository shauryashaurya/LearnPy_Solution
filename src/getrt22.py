import os
import xml.etree.ElementTree as et
import urllib.request
import time
import webbrowser

""" Travis traveled to Chicago and took the Clark Street #22 bus up to Dave's Office"""
""" He left his suitcase on the bus"""

""" We track the bus via the CTA Bustracker API, when it gets within half a mile of Dave's Office again,
we alert Dave by opening a static map showing the bus' location and Dave + Travis can run down and retrieve the suitcase"""

""" Approach:
1. Get the bus feed
2. Figure out which bus it was - with any luck it's the one that just left Dave's office
3. Run a timed method to get latest updates for the bus
4. Check the updates to see if the bus is close to Dave's office
5. If the bus is within 0.5 miles, open up a static map to display the location of the bus"""

#START

# First get the bus feed
rawBusData = urllib.request.urlopen("http://ctabustracker.com/bustime/map/getBusesForRoute.jsp?route=22").read()

# Establish the location of Dave's office, picked up from the video
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
# see the end of this file to get an idea of the structure of busRouteXML
def findTheBusThatJustLeftOffice(busRouteXML):
    probableBusses = []
    # print ("created an empty list to store the probable busses: ",probableBusses)
    for bus in busRouteXML.findall('bus'):
        lat = float(bus.find('lat').text)
        lon = float(bus.find('lon').text)
        direction = bus.find('d').text
        directionStartsWithNorth = direction.startswith('North')
        if lat>office_lat and directionStartsWithNorth:
            probableBusses.append([int(bus.find('id').text),distance(lat,office_lat), lat, lon])
            print ("bus found! updating the list of probable busses: ",probableBusses)
    probableBusses.sort(key=lambda x: x[1])
    print ("This is the of probable busses sorted according to distance from Dave's office: ",probableBusses)
    print ("Most probable bus in the list, is the one that just left, with any luck this is the one that's closest to Dave's Office: ",probableBusses[0])
    return probableBusses[0]

def showLocationOnMap(lat,lon):
    webbrowser.open('http://maps.googleapis.com/maps/api/staticmap?size=500x500&sensor=false&markers=|%f,%f' % (lat, lon))

def fetchLatestDetailsAboutThatOneBus(busId):
    print("finding details for bus:", busId)
    busData = urllib.request.urlopen("http://ctabustracker.com/bustime/map/getBusesForRoute.jsp?route=22").read()
    busXmlList = et.fromstring(busData).findall('bus')
    bus = []
    for bus in busXmlList:
        print("comparing bus: ",bus.find('id').text, " to bus: ", busId)
        if int(bus.find('id').text) == int(busId):
            bus= [int(bus.find('id').text), float(bus.find('lat').text), float(bus.find('lon').text)]
            break
        else: 
            #print("This bus does not match ID ",busId,". \nLet's look at the next one (if there's one)")
            bus = nullBusTuple
    print("Latest Details for bus #",bus[0], "latitude: ",bus[1], "longitude: ", bus[2])
    return bus

def monitorBusLocation(busTuple):
    print("getting updated bus data")
    myBusUpdate = fetchLatestDetailsAboutThatOneBus(busTuple[0])
    if distance(myBusUpdate[1],office_lat)<0.5:
        print('Bus ',bus[0],' is coming!!! go and catch it!')
        showLocationOnMap(bus[2],bus[3])

# convert the XML data into an element tree xml object
r22Xml = et.fromstring(rawBusData)

# if all's well, go ahead, find the right bus and start monitoring it
if r22Xml:
    print("XML data for route 22 found!")
    myBus = findTheBusThatJustLeftOffice(et.fromstring(rawBusData))
    while True:
        monitorBusLocation(myBus)
        # check again every two minutes
        time.sleep(120)
else:
    print("error getting XML from the CTA source")

# END

""" Here's a sample of the bus data XML:

<?xml version="1.0"?>
<buses rt="22">
	<time>5:49 AM</time>
	<bus>
		<id>4135</id>
		<rt>22</rt><d>South Bound</d>
		<dd>South Bound</dd>
		<dn>S</dn>
		<lat>41.96690515886273</lat>
		<lon>-87.66707691393401</lon>
		<pid>3929</pid>
		<pd>South Bound</pd>
		<run>P851</run>
		<fs>Harrison</fs>
		<op>42892</op>
		<dip>3379</dip>
		<bid>6627878</bid>
		<wid1>0P</wid1>
		<wid2>851</wid2>
	</bus>
</buses>
"""
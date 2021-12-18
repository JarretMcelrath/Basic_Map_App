import tkinter
import math
import ssl
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlencode, quote_plus
import json


GOOGLEAPIKEY = "Your API Key Here"


class Globals:
    rootWindow = None
    mapLabel = None
    choiceVar = None

    defaultLocation = "Mt. Fuji, Japan"
    mapLocation = defaultLocation
    mapFileName = 'googlemap.gif'
    mapSize = 400
    mapType = "roadmap"
    zoomLevel = 9


# Given a string representing a location, return 2-element tuple
# (latitude, longitude) for that location
#
# See https://developers.google.com/maps/documentation/geocoding/
# for details about Google's geocoding API.
#
#
def geocodeAddress(addressString):
    urlbase = "https://maps.googleapis.com/maps/api/geocode/json?address="
    geoURL = urlbase + quote_plus(addressString)
    geoURL = geoURL + "&key=" + GOOGLEAPIKEY

    # required (non-secure) security stuff for use of urlopen
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    stringResultFromGoogle = urlopen(geoURL, context=ctx).read().decode('utf8')
    jsonResult = json.loads(stringResultFromGoogle)
    if (jsonResult['status'] != "OK"):
        print("Status returned from Google geocoder *not* OK: {}".format(jsonResult['status']))
        result = (
        0.0, 0.0)  # this prevents crash in retrieveMapFromGoogle - yields maps with lat/lon center at 0.0, 0.0
    else:
        loc = jsonResult['results'][0]['geometry']['location']
        result = (float(loc['lat']), float(loc['lng']))
    return result


# Construct a Google Static Maps API URL that specifies a map that is:
# - is centered at provided latitude lat and longitude long
# - is "zoomed" to the Google Maps zoom level in Globals.zoomLevel
# - Globals.mapSize-by-Globals.mapsize in size (in pixels),
# - will be provided as a gif image
#
# See https://developers.google.com/maps/documentation/static-maps/
def getMapUrl():
    lat, lng = geocodeAddress(Globals.mapLocation)
    urlbase = "http://maps.google.com/maps/api/staticmap?"
    args = "center={},{}&zoom={}&size={}x{}&format=gif&maptype={}&markers=color:red%7Clabel:%7C{},{}". \
        format(lat, lng, Globals.zoomLevel, Globals.mapSize, Globals.mapSize, Globals.mapType, lat, lng)
    args = args + "&key=" + GOOGLEAPIKEY
    mapURL = urlbase + args
    return mapURL


# Retrieve a map image via Google Static Maps API, storing the
# returned image in file name specified by Globals' mapFileName
#
def retrieveMapFromGoogle():
    url = getMapUrl()
    urlretrieve(url, Globals.mapFileName)


def displayMap():
    retrieveMapFromGoogle()
    mapImage = tkinter.PhotoImage(file=Globals.mapFileName)
    Globals.mapLabel.configure(image=mapImage)
    Globals.mapLabel.mapImage = mapImage


def readEntryAndDisplayMap():
    newLocation = Globals.enterLocation.get()
    Globals.mapLocation = newLocation
    displayMap()


def zoomOut():
    Globals.zoomLevel -= 1
    displayMap()


def zoomIn():
    Globals.zoomLevel += 1
    displayMap()


def radioButtonChosen():
    if Globals.choiceVar.get() == 1:
        Globals.mapType = 'roadmap'
    elif Globals.choiceVar.get() == 2:
        Globals.mapType = 'terrain'
    elif Globals.choiceVar.get() == 3:
        Globals.mapType = 'satellite'
    elif Globals.choiceVar.get() == 4:
        Globals.mapType = 'hybrid'
    displayMap()


##########
#  basic GUI code

def initializeGUIetc():
    Globals.rootWindow = tkinter.Tk()
    Globals.rootWindow.title("HW10")
    Globals.choiceVar = tkinter.IntVar()
    Globals.rootWindow.iconbitmap("myIcon.ico")

    mapType = tkinter.StringVar()
    mapType.set("roadmap")
    Globals.mapType = mapType

    label = tkinter.Label(Globals.rootWindow, text="Enter Location Here")
    label.pack(side=tkinter.TOP)

    mainFrame = tkinter.Frame(Globals.rootWindow)
    mainFrame.pack()

    bottomFrame = tkinter.Frame(Globals.rootWindow)
    bottomFrame.pack(side=tkinter.BOTTOM)

    Globals.enterLocation = tkinter.Entry(mainFrame, width=20)
    Globals.enterLocation.pack()

    readEntryAndDisplayMapButton = tkinter.Button(mainFrame, text="Show me the map!", command=readEntryAndDisplayMap)
    readEntryAndDisplayMapButton.pack()

    Globals.mapLabel = tkinter.Label(mainFrame, width=Globals.mapSize, bd=2, relief=tkinter.FLAT)
    Globals.mapLabel.pack()

    hybridButton = tkinter.Radiobutton(bottomFrame, text="hybrid", variable=Globals.choiceVar, value=4,
                                       command=radioButtonChosen)
    hybridButton.pack(side=tkinter.RIGHT)

    satelliteButton = tkinter.Radiobutton(bottomFrame, text="Satellite", variable=Globals.choiceVar, value=3,
                                          command=radioButtonChosen)
    satelliteButton.pack(side=tkinter.RIGHT)

    terrainButton = tkinter.Radiobutton(bottomFrame, text="Terrain", variable=Globals.choiceVar, value=2,
                                        command=radioButtonChosen)
    terrainButton.pack(side=tkinter.RIGHT)

    roadMapButton = tkinter.Radiobutton(bottomFrame, text="Road", variable=Globals.choiceVar, value=1,
                                        command=radioButtonChosen)
    roadMapButton.pack(side=tkinter.RIGHT)

    labelZoom = tkinter.Label(bottomFrame, text="Zoom")
    labelZoom.pack(side=tkinter.LEFT)

    zoomOutButton = tkinter.Button(bottomFrame, text="-", command=zoomOut)
    zoomOutButton.pack(side=tkinter.LEFT)

    zoomInButton = tkinter.Button(bottomFrame, text="+", command=zoomIn)
    zoomInButton.pack(side=tkinter.LEFT)


def startMap():
    initializeGUIetc()
    displayMap()
    Globals.rootWindow.mainloop()

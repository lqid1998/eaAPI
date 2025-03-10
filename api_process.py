import requests
import sys
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from decimal import Decimal


class JsonIO:
    def read(self, file):
        try:
            with open(file,"r") as f:
                jsonData = json.load(f)
            return jsonData
        except Exception as err:
            sys.exit(f"an error occured when open {file}\n{err}")

    def write(self, jsonData, file="data.json"):
        with open(file, "a+") as f:
            json.dump(jsonData, f, indent=4)


class EaFloodAPIParser:
    def getResponse(url):
        return getResponse(url)
    
    def getItems(url):
        return getItems(url)
    
    # def getAllStationsJson():
    #     return getAllStationsJson()
    
    def getStationsJsonByFilter(key, value):
        return getStationsJsonByFilter(key, value)
    
    def getStationByID(stationID)-> "Station":
        return getStationByID(stationID)

    def getMeasureByID(measureID) -> "Measure":
        return getMeasureByID(measureID)
    
    def getMeasuresOfStation(measureID) -> list["Measure"]:
        return getMeasuresOfStation(measureID)
    
    def getReadingsOfMeasure(measureID) -> "Measure":
        return getReadingsOfMeasure(measureID)


class Station:

    RLOIid: str 
    catchmentName: str
    dateOpened: str
    datumOffset: str
    label: str
    eaAreaName: str
    eaRegionName: str
    notation: str
    riverName: str
    stationReference: str
    town: str
    wiskiID: str
    lat: Decimal
    long: Decimal
    easting: int
    northing: int
    status: str
    statusReason: str
    statusDate: str

    def __init__(self, json):
        self.json = json
        for key, value in json.items():
            setattr(self, key, value)

    @classmethod
    def fromID(cls, id) -> "Station":
        return EaFloodAPIParser.getStationByID(id)
    
    @classmethod
    def fromList(cls, jsonList) -> list[ "Station"]:
        stationList = []
        for json in jsonList:
            stationList.append(Station(json))
        return stationList

    def getMeasures(self) -> "Measure":
        return EaFloodAPIParser.getMeasuresOfStation(self.notation)
    
    def printStationInfo(self):
        printStationInfo(self)


class Measure:

    notation: str

    def __init__(self, json):
        self.json = json
        for key, value in json.items():
            setattr(self, key, value)

    @classmethod
    def fromID(cls, measureID) -> "Measure":
        return EaFloodAPIParser.getMeasureByID(measureID)

    def getReadings(self) -> "Readings":
        return Readings.fromMeasure(self)

class Readings:
    dateTimes: list[datetime]
    values: list[Decimal]
    measureID: str


    def __init__(self, json):
        self.json = json
        self.dateTimes = []
        self.values = []
        for reading in json:
            self.dateTimes.append(datetime.strptime(reading.get("dateTime"), "%Y-%m-%dT%H:%M:%SZ"))
            self.values.append(reading.get('value'))
        self.measureID = json[0].get('measure').split("/")[-1] # original measure contains the whole url

    @classmethod
    def fromMeasure(cls, measureID) -> "Readings":
        return EaFloodAPIParser.getReadingsOfMeasure(measureID)

    def plotReadings(self):
        plotReadings(self)

    def plotReadingsWithTable(self):
        plotReadingsWithTable(self)

def getResponse(url):
    
    response = requests.get(url)
    responseJson = response.json()
    return responseJson

def getItems(url):
    response = requests.get(url)
    if response.status_code == 200:
        responseJson = response.json()
        items = responseJson["items"]
        return items
    else:
        response.raise_for_status()
    

def getAllStationsJson():
    url = "https://environment.data.gov.uk/flood-monitoring/id/stations"
    return getItems(url)

def getStationsJsonByFilter(key, value):
    url = f"https://environment.data.gov.uk/flood-monitoring/id/stations?{key}={value}"
    return getItems(url)

def getStationByID(stationID):
    url = f"https://environment.data.gov.uk/flood-monitoring/id/stations/{stationID}.json?_view=full"
    try:
        return Station(getItems(url))
    except requests.exceptions.HTTPError as e:
        # print(f"{e}")
        print(f"No station find with {stationID}")

def getMeasureByID(measureID):
    url = f"https://environment.data.gov.uk/flood-monitoring/id/measures/{measureID}"
    return Measure(getItems(url))

def getMeasuresOfStation(stationID):
    url = f"https://environment.data.gov.uk/flood-monitoring/id/stations/{stationID}/measures"
    measuresList = []
    jsonList = getItems(url)
    if jsonList:
        for json in jsonList:
            measuresList.append(Measure(json))
        return measuresList

def getReadingsOfMeasure(measureID):
    url = f"https://environment.data.gov.uk/flood-monitoring/id/measures/{measureID}/readings?_sorted"
    jsonList = getItems(url)
    if jsonList:
        return Readings(jsonList)
    

def printStationInfo(station:Station):
        print(f"\nStation ID:                                 {station.notation}")
        print(f"River Levels On the Internet(RLOI) ID:      {getattr(station, 'RLOIid', '')}")
        print(f"Catchment:                                  {getattr(station, 'catchmentName', '')}")
        print(f"Date Opened:                                {getattr(station, 'dateOpened', '')}")
        print(f"Label:                                      {getattr(station, 'label', '')}")
        print(f"Area Name:                                  {getattr(station, 'eaAreaName', '')}")
        print(f"River Name:                                 {getattr(station, 'riverName', '')}")
        print(f"Station Reference:                          {getattr(station, 'stationReference', '')}")
        print(f"Town:                                       {getattr(station, 'town', '')}")
        print(f"wiskiID:                                    {getattr(station, 'wiskiID', '')}")
        print(f"lat:                                        {getattr(station, 'lat', '')}")
        print(f"long:                                       {getattr(station, 'long', '')}")
        print(f"easting:                                    {getattr(station, 'easting', '')}")
        print(f"northing:                                   {getattr(station, 'northing', '')}")
        print(f"status:                                     {getattr(station, 'status', '')}")

def plotReadings(readings:Readings):
    plt.figure(figsize=(12, 9))
    ax = plt.subplot(111)
    ax.plot(readings.dateTimes[0:96], readings.values[0:96], color="black", marker='x', markersize=10)
    ax.set_title(readings.measureID)
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))  
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    # plt.show()
    plt.savefig(f'{readings.measureID}.png',format='png', bbox_inches='tight')
    print(f"Plot of readings saved in {readings.measureID}.png\n")
    plt.close()

def plotReadingsWithTable(readings:Readings):
    plt.figure(figsize=(12, 9))

    # plot
    ax1  = plt.subplot(111)
    ax1.plot(readings.dateTimes[0:96], readings.values[0:96], color="black", marker='x', markersize=10)
    ax1.set_title(readings.measureID)
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=2))  
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    # table
    labels = ["data tiem", "readings"]
    texts = []

    for i in range(0, 96):
        texts.append([readings.dateTimes[i], readings.values[i]])

    ax1.table(cellText=texts, colLabels=labels, loc="top", bbox=[0, -3.1, 0.3, 3])

    plt.subplots_adjust(hspace=0.1)
    # plt.show()
    plt.savefig(f'{readings.measureID}.png',format='png', bbox_inches='tight')
    print(f"Plot of readings saved in {readings.measureID}.png\n")
    plt.close()

# def getReadingsByStationID(id,):
#     url = f"https://environment.data.gov.uk/flood-monitoring/id/stations/{id}/readings?_sorted"
#     return getItems(url)

# def getReadingsFromStation(station:Station):
#     return getReadingsByStationID(station.notation)
        




# def get_town_rearranged(stations):

#     town_rearranged = {'other':[]}
#     for i in range(len(stations)):
#         town = stations[i].get('town')
#         if town:
#             list_of_stations = town_rearranged.get(town)
#             if not list_of_stations:
#                 town_rearranged[town] = []
#             town_rearranged.get(town).append(stations[i])
#         else:
#             town_rearranged.get('other').append(stations[i])
#     return town_rearranged



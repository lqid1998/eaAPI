from api_process import EaFloodAPIParser, Station, Measure, Readings


def printManu():
    print("\nGet readings of station from Environment Agency Real Time flood-monitoring API")
    print("1. Station’s readings over the last 24 hours")
    print("2. Stations Search")
    print("3. Quit")

def manu():




    while True:
        printManu()
        option = str(input("Enter your option: \n").strip())
        if option == '1':
            stationReadings(stationID="")
        elif option == '2':
            stationBrowser()
        elif option == '3':
            print("Exiting")
            break
        else:
            print("Please enter a valid number")
        # stations = io.get_stations()
        # rearranged = process.get_station_by_stationReference(stations)
        # print(rearranged.keys())
        # print(io.get_station_by_stationReference("E70024"))

def stationReadings(stationID):
    if not stationID:
        stationID = str(input("Enter the station id: ").strip())
    station = Station.fromID(stationID)
    station.printStationInfo()
    print(f"\nSave station({stationID})’s readings over the last 24 hours?")
    plotStationReadings(station)

def yesOrNo(func):
    def wrapper(*args, **kwargs):
        while True:
            option = str(input("[y]/n?\n").strip())
            if (option == 'y') or (option == 'N') or not option:
                func(*args, **kwargs)
                break
            elif (option == 'n') or (option == 'n'):
                break
            else:
                print("Please enter a valid option")
    return wrapper

@yesOrNo
def plotStationReadings(station: Station):
    measures = station.getMeasures()
    if len(measures) == 0:
        print("No measure in this station")
    else:
        print(f"{len(measures)} Measures in the station")
        for measure in measures:
            readings = Readings.fromMeasure(measure.notation)
            if readings:
                print(f"Measure {measure.label} has readings.")
                readings.plotReadings()
            else:
                print(f"Measure {measure.label} has no readings.")

def stationBrowser():
    while True:
        print("\nSearch Stations via")
        print("1. Catchment Name")
        print("2. River Name")
        print("3. Town")
        print("4. Search Name")
        print("5. Back")

        option = str(input("Enter your option: ").strip())
        if option == '1':
            filterKey = "catchmentName"
            value = str(input("Please Enter the Catchment Name\n").strip())
        elif option == '2':
            filterKey = "riverName"
            value = str(input("Please Enter the River Name\n").strip())
        elif option == '3':
            filterKey = "town"
            value = str(input("Please Enter the Town\n").strip())
        elif option == '4':
            filterKey = "search"
            value = str(input("Please Enter the keyword to search\n").strip())
        elif option == '5':
            break
        else:
            print("Please enter a valid number")
            continue

        stationsJson = EaFloodAPIParser.getStationsJsonByFilter(filterKey, value)
        amountOfStations = len(stationsJson)
        if amountOfStations == 0:
            print("no station found")
        elif amountOfStations <= 100:
            stations = Station.fromList(stationsJson)
            displayStationsList(stations, filterKey, value)
            pass
        else:
            print("Amount over 100, are you sure to display?")
            yesOrNo(displayStationsList)


def displayStationsList(stations: list[Station], filterKey, value):
    amountOfStations = len(stations)
    pages = amountOfStations // 9
    if amountOfStations % 9 > 0:
        pages += 1

    pageCounter = 0
    while True:
        print(f"{amountOfStations} stations found whose {filterKey} contains {value}")
        restNumberOfStations = amountOfStations - pageCounter * 9
        for i in range(0, restNumberOfStations if restNumberOfStations < 9 else 9):
            print(f"\n{i+1}: {stations[i + pageCounter * 9].label}")
        print(f"its page {pageCounter + 1} of {pages}")
        option = str(input("Choose the station to display information\n[j] Next page | [k] Previous page | [q] Go back\n").strip())
        if str.isdigit(option):
            station = stations[pageCounter * 9 + int(option[0]) -1 ]
            station.printStationInfo()
            print("\nShow station’s readings over the last 24 hours?")
            plotStationReadings(station)
            break
        elif option == 'j':
            if pageCounter < (pages - 1):
                pageCounter +=1
            pass
        elif option == 'k':
            if pageCounter > 0:
                pageCounter -=1
            pass
        elif option == 'q':
            break
        else:
            print("Please enter a valid option")
import sys
import json

file_name = sys.argv[1]

file = open(file_name, "r")
data = json.loads(file.read())
file.close()

# Service validation
for service in data["services"]:
    for schedule_item in data["services"][service]:
        for station in schedule_item.split(" - "):
            if station not in data["stations"]:
                print("Station '" + station + "' found in service '" + service + "' does not exist")
            if service not in data["stations"][station]:
                print("Service '" + service + "' not found to serve station '" + station + "'")

# Station validation
for station in data["stations"]:
    for line in data["stations"][station]:
        if line not in data["services"]:
            print("Station '" + station + "' not found in service '" + line + "'")
        else:
            found = False
            for item in data["services"][line]:
                if station in item:
                    found = True
            if not found:
                print("Station '" + station + "' not found in service '" + line + "'")
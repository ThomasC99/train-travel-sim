import sys
import json

file_name = sys.argv[1]

file = open(file_name, "r")
data = json.loads(file.read())
file.close()

num = 0
# Service validation
for service in data["services"]:
    for schedule_item in data["services"][service]["schedule"]:
        for station in schedule_item.split(" - "):
            if station not in data["stations"]:
                print("Station '" + station + "' found in service '" + service + "' does not exist")
                num += 1
            elif service not in data["stations"][station]:
                print("Service '" + service + "' not found to serve station '" + station + "'")
                num += 1

# Station validation
for station in data["stations"]:
    for line in data["stations"][station]:
        if line not in data["services"]:
            print("Station '" + station + "' not found in service '" + line + "'")
            num += 1
        else:
            found = False
            for item in data["services"][line]["schedule"]:
                if station in item:
                    found = True
            if not found:
                print("Station '" + station + "' not found in service '" + line + "'")
                num += 1
print("Total defects : " + str(num))

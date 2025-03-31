import json
import sys

level = sys.argv[1]
file = open(level, "r")
level_data = json.loads(file.read())
file.close()

file = open("save.json", "r")
save_data = json.loads(file.read())
file.close()

if "network-data" not in save_data:
    save_data["network-data"] = {}

if "services" not in save_data["network-data"]:
    save_data["network-data"]["services"] = {}

if "stations" not in save_data["network-data"]:
    save_data["network-data"]["stations"] = {}

for service in level_data["services"]:
    if service not in save_data["network-data"] and service not in save_data["service-data"]["services"]:
        save_data["network-data"]["services"][service] = level_data["services"][service]
        for station in level_data["stations"]:
            if station not in save_data["network-data"]["stations"]:
                save_data["network-data"]["stations"][station] = []
            save_data["network-data"]["stations"][station].append(service)

file = open("save.json", "w")
file.write(json.dumps(save_data, indent=2))
file.close()
import json
import sys

level = sys.argv[1]
level_data = None
with open(level, "r", encoding="UTF-8") as file:
    level_data = json.loads(file.read())

save_data = None
with open("save.json", "r", encoding="UTF-8") as file:
    save_data = json.loads(file.read())

if "network-data" not in save_data or save_data["network-data"] is None:
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

save_data["visited-all-stations"] = False

with open("save.json", "w", encoding="UTF-8") as file:
    file.write(json.dumps(save_data, indent=2))

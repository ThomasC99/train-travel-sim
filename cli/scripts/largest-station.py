import json

data = None
with open("save.json", "r", encoding="UTF-8") as file:
    data = json.loads(file.read())

station_name = ""
most = 0

for station in data["service-data"]["stations"]:
    if len(data["service-data"]["stations"][station]) > most:
        most = len(data["service-data"]["stations"][station])
        station_name = station

print("Most Transfers : " + station_name)
print("Transfers      : " + str(most))
for service in data["service-data"]["stations"][station_name]:
    print(service)
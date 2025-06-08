import json

data = {}
data["services"] = {}
data["stations"] = {}

file = open("rail-data.json", "r")
rail_data = json.loads(file.read())
file.close()

for line in rail_data:
    line_name = "R" + str(len(data["services"].keys()) + 1) + " " + line
    data["services"][line_name] = {}

    for i in range (0, rail_data[line]["length"] + 1): # matagami sub, R1
        base = line + " Kilometer "
        station_name = base + str(i)

        if str(i) in rail_data[line]["stations"]:
            station_name = rail_data[line]["stations"][str(i)]

        if station_name not in data["stations"]:
            data["stations"][station_name] = [line_name]
        else:
            data["stations"][station_name].append(line_name)

        if i > 0:
            prev_station = base + str(i - 1)
            if str(i - 1) in rail_data[line]["stations"]:
                prev_station = rail_data[line]["stations"][str(i - 1)]
            data["services"][line_name][prev_station+ " - " + station_name] = 2

file = open("level-data/canrail.json", "w")
file.write(json.dumps(data, indent=4))
file.close()
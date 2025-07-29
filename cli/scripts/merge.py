import json
import sys

dest = sys.argv[1]
source = sys.argv[2]

dest_file = open(dest, "r")
dest_json = json.loads(dest_file.read())
dest_file.close()

source_file = open(source, "r")
source_json = json.loads(source_file.read())
source_file.close()

for service in source_json["services"]:
    dest_json["services"][service] = source_json["services"][service]

for station in source_json["stations"]:
    if station not in dest_json["stations"]:
        dest_json["stations"][station] = source_json["stations"][station]
    else:
        for service in source_json["stations"][station]:
            dest_json["stations"][station].append(service)

dest_file = open(dest, "w")
dest_file.write(json.dumps(dest_json, indent=4))
dest_file.close()
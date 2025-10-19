import json
import time
import progressbar

start = time.time()

levels = None
with open("level-compositions.json", "r", encoding="UTF-8") as file:
    levels = json.loads(file.read())

for i in progressbar.progressbar(range(len(levels))):
    level = levels[i]
    comp = {
        "services" : {
        },
        "stations" : {
        }
    }
    for a in level["components"]:
        a_data = None
        with open(a, "r", encoding="UTF-8") as file:
            a_data = json.loads(file.read())
        for service in a_data["services"]:
            if service not in comp["services"]:
                comp["services"][service] = a_data["services"][service]
            else:
                print("Warning : duplicate id found for " + service)
        for station in a_data["stations"]:
            if station not in comp["stations"]:
                comp["stations"][station] = []
            for line in a_data["stations"][station]:
                if line not in comp["stations"][station]:
                    comp["stations"][station].append(line)
                else:
                    print("Warning : duplicate line id " + line + " found for station " + station)
    with open(level["output-file"], "w", encoding="UTF-8") as file:
        file.write(json.dumps(comp, indent=4))
    seg_time = time.time() - start

end = time.time()
total_time = end - start
print("Generated " + str(len(levels)) + " levels in ", end="")

print(str(int(total_time * 1000)) + " miliseconds")

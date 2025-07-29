import json
from dijkstar import Graph, find_path
import sys

file_name = sys.argv[1]
t = int(sys.argv[2])

file = open(file_name, "r")
data = json.loads(file.read())
file.close()

graph = Graph (undirected = True)

for line in data["services"]:
    schedule = data["services"][line]
    for item in schedule:
        a = item.split(" - ")[0]
        b = item.split(" - ")[1]
        graph.add_edge(a, b, schedule[item])

stations = list(data["stations"].keys())

highest = 0
highest_pair = ""
num = 0
for a in range (0, len(stations) - 1):
    for b in range (a + 1, len(stations)):
        dist = find_path(graph, stations[a], stations[b])[3]
        if dist > t:
            print(stations[a] + " - " + stations[b] + " : " + str(dist))
            num += 1
        if dist > highest:
            highest = dist
            highest_pair = stations[a] + " - " + stations[b]

print(num)
print()
print(highest_pair + " : ", end="")
if highest < 60:
	print(highest)
else:
	hours = highest // 60
	minutes = highest % 60
	print(str(hours) + "h" + str(minutes))

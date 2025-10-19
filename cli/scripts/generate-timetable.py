import json
import progressbar

train_data = None
with open("rolling-stock.json", "r") as file:
	train_data = json.loads(file.read())
print("generating performace data")
for i in progressbar.progressbar(range(len(train_data.keys()))):
	train = list(train_data.keys())[i]
	train_data[train]["perf"] = {}
	tick = 0.001
	current_speed = 0
	maximum_speed = train_data[train]["max-speed"] / 3.6 # m/s
	power = train_data[train]["power"] * 1000 # W
	mass = train_data[train]["weight"] * 1000 # kg
	dist = 0.0
	time = 0.0
	tmp_prf = {}
	while current_speed < maximum_speed:
		time += tick
		acc = 1
		if current_speed > 0:
			current_acc = (power / current_speed) / mass
			if current_acc < acc:
				acc = current_acc
		dist += current_speed * tick
		dist += (acc / 2) * (tick ** 2)
		current_speed += acc * tick
		stopping_time = time + current_speed
		stopping_dist = dist + (0.5 * (current_speed ** 2))
		tmp_prf[stopping_dist] = stopping_time + 15
	last = 0.0
	for perf in tmp_prf:
		perf_conv = int(perf / 100) / 10
		if perf_conv > last:
			perf_conv = round(perf_conv, 1)
			last = perf_conv
			train_data[train]["perf"][perf_conv] = int(tmp_prf[perf])
	rem_dist = ((last + 0.1) * 1000) - list(tmp_prf.keys())[-1]
	rem_time = rem_dist / maximum_speed
	train_data[train]["perf"][round(last + 0.1, 1)] = int(rem_time + tmp_prf[list(tmp_prf.keys())[-1]])

print("Generating Timetables")
config = None
with open("level-generate.json", "r") as file:
	config = json.loads(file.read())
for i in progressbar.progressbar(range(len(config))):
	current_config = config[i]
	system = None
	train = current_config["train"]
	with open(current_config["source"], "r") as file:
		system = json.loads(file.read())
	for service in system["services"]:
		schedule = system["services"][service]["schedule"]
		for leg in schedule:
			dist = schedule[leg]
			time = 0
			if dist not in train_data[train]["perf"]:
				rem = dist - list(train_data[train]["perf"].keys())[-1]
				rem_time = int((rem / train_data[train]["max-speed"]) * 3600)
				time = train_data[train]["perf"][list(train_data[train]["perf"].keys())[-1]] + rem_time
			schedule[leg] = (time // 60) + 1
	with open(current_config["output"], "w") as file:
		file.write(json.dumps(system, indent=4))

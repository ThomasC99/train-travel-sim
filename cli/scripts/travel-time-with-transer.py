import json
from dijkstar import Graph, find_path
import sys

limit = int(sys.argv[1])

print("\n\n\n")

# Load data from the save file
with open("save.json", "r", encoding="utf-8") as file:
    data = json.load(file)

stations = list(data["service-data"]["stations"].keys())
stations.sort()
services = data["service-data"]["services"]

total_routes = 0

for i in range (0, len(stations)):
    current_station = stations[i]
    for j in range (i + 1, len(stations)):
        target_station = stations[j]
        if target_station != current_station:

            # Initialize the graph as an undirected graph
            graph = Graph(undirected=True)

            # Dictionary to hold the line stops in both directions
            lines = {}

            # Add edges to the graph based on the services data and build the lines dictionary
            for service, service_data in services.items():
                line_origin = f"{service} ({service_data['destination']})"
                line_destination = f"{service} ({service_data['origin']})"
                
                # Initialize lists for both directions
                lines[line_origin] = [service_data['origin']]
                lines[line_destination] = [service_data['destination']]
                
                # Add edges and populate stops for each direction
                for leg, time in service_data["schedule"].items():
                    start_station, end_station = leg.split(" - ")
                    graph.add_edge(start_station, end_station, time)
                    
                    # Add stations to the respective direction lists
                    lines[line_origin].append(end_station)
                    lines[line_destination].insert(1, start_station)  # Prepend in reverse order

            # Step 1: Check if there is a direct line between current_station and target_station
            direct_route_found = False
            for line_name, stops in lines.items():
                if current_station in stops and target_station in stops:
                    # Check if the order of stations is consistent for a direct route
                    if stops.index(current_station) < stops.index(target_station):
                        # Calculate total travel time for the direct route
                        route_stations = stops[stops.index(current_station):stops.index(target_station) + 1]
                        total_time = find_path(graph, route_stations[0], route_stations[-1])[3]
                        # total_time = sum(
                        #     graph.get_edge(route_stations[i], route_stations[i + 1])
                        #     for i in range(len(route_stations) - 1)
                        # )
                        route = [{"line": line_name, "stations": route_stations}]
                        direct_route_found = True
                        break

            if not direct_route_found:
                # Find the shortest path and total travel time
                total_time = 0
                try:
                    path_data = find_path(graph, current_station, target_station)
                    total_time = path_data.total_cost
                    path = path_data.nodes
                except Exception as e:
                    print(f"Error finding path: {e}")
                    path = []

                # Determine which lines to take to match the path
                route = []
                current_line = None

                # Increased transfer penalty to reduce unnecessary transfers
                transfer_penalty = 5
                transfers = 0

                # Iterate through consecutive station pairs in the path
                for i in range(len(path) - 1):
                    start, end = path[i], path[i + 1]
                    segment_found = False

                    # Check each line direction to see if it covers the segment
                    for line_name, stops in lines.items():
                        if start in stops and end in stops:
                            # Ensure the order of stations matches the direction
                            if stops.index(start) < stops.index(end):
                                # Check if we should switch lines
                                if current_line != line_name:
                                    # Switch only if needed and it significantly reduces travel time
                                    if current_line is not None:
                                        transfers += 1
                                    route.append({"line": line_name, "stations": [start]})
                                    current_line = line_name
                                route[-1]["stations"].append(end)
                                segment_found = True
                                break
                    
                    # If no line was found to cover the segment
                    if not segment_found:
                        print(f"No line found covering the segment: {start} - {end}")

                # Add transfer penalty to total travel time
                total_time += transfers * transfer_penalty
            

            # Convert total time to hours and minutes for display
            hours = total_time // 60
            minutes = total_time % 60

            # Output the route with total time and line details

            if total_time > limit:
                total_routes += 1
                print (current_station + " - " + target_station)
                for segment in route:
                    seg_time = find_path(graph, segment["stations"][0], segment["stations"][-1])[3]
                    print(f"Take {segment['line']} to {segment['stations'][-1]} ({seg_time} minutes)")

                if hours > 0:
                    print(f"Total travel time: {hours} hours and {minutes} minutes")
                else:
                    print(f"Total travel time: {minutes} minutes")

                print("")
    
print ("")
print ("Total routes : " + str(total_routes))
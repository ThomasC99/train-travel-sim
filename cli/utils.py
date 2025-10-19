"""libary for converting json objects to and from a string"""
import json
import time
from typing import Any
from urllib import error, request
from player import Player



def load_json_file (name: str):
    """loads a file and converts it into a josn object"""
    data = None
    with open(name, "r", encoding="utf-8") as file:
        data = json.loads(file.read())
    return data

def calc_points_needed (player: Player) -> int: # TODO
    """calculates the total points needed to complete a level"""
    total: int = 0
    network_data = player.get_network_data()
    if network_data is not None and "services" in network_data:
        for service in network_data["services"]:
            service_data = network_data["services"][service]["schedule"]
            service_total = 0
            for leg in service_data:
                service_total += service_data[leg]
            service_total *= 2
            total += service_total * 288
    service_data = player.get_service_data().get_json_data()
    for service in service_data["services"]:
        service_total = 0
        for leg in service_data["services"][service]["schedule"]:
            service_total += service_data["services"][service]["schedule"][leg]
        service_total *= 2
        total += service_total * (288 - len(service_data["services"][service]["departures"]))
    return total

def points_to_time_str (points: int):
    """Takes in points needed to complete a level, and converts them into a human-readable time
    sting"""
    points_str: str = ""
    if points >= 525960: # years
        years = points // 525960
        points = points % 525960
        points_str += str(years) + " "
        if years > 1:
            points_str += "years, "
        else:
            points_str += "year, "

    if points >= 43200: # months
        months = points // 43200
        points = points % 43200
        points_str += str(months) + " "
        if months > 1:
            points_str += "months, "
        else:
            points_str += "month, "

    if points >= 10080: # weeks
        weeks = points // 10080
        points = points % 10080
        points_str += str(weeks)
        if weeks > 1:
            points_str += " weeks, "
        else:
            points_str += " week, "

    if points >= 1440: # days
        days = points // 1440
        points = points % 1440
        points_str += str(days)
        if days > 1:
            points_str += " days, "
        else:
            points_str += " day, "

    if points >= 60: # hours
        hours = points // 60
        points_str += str(hours) + " "
        if hours > 1:
            points_str += "hours, "
        else:
            points_str += "hour, "
        points = points % 60

    if points > 1: # minutes
        points_str += str(points) + " minutes"
    if points == 1:
        points_str += "1 minute"
    if points == 0:
        points_str += "0 minutes"
    return points_str

def display_stats (screen: Any, player: Player): # TODO
    """displays the player's stats"""
    running = True
    min_points = 0
    points = calc_points_needed(player)
    points_str = points_to_time_str(points)
    station_list: list[str] = []
    for station in player.get_service_data().get_stations().keys():
        if station not in station_list:
            station_list.append(station)
    for service in player.get_service_data().get_services():
        service_data = player.get_service_data().get_services()[service]
        if len(service_data["departures"]) < 288:
            for leg in service_data["schedule"]:
                min_points += service_data["schedule"][leg] * 2
    if player.get_network_data() is not None and "stations" in player.get_network_data():
        for station in player.get_network_data()["stations"].keys():
            if station not in station_list:
                station_list.append(station)
    num_stations = len(station_list)
    stations_visited = len(player.get_visited_stations())
    ratio: int = int(stations_visited / num_stations * 100)
    while running:
        screen.clear()
        screen.addstr(0, 0, "Points                     : " + str(player.get_points()))
        screen.addstr(1, 0, "Minimum Points Recommended : " + str(min_points))
        screen.addstr(2, 0, "Current Location           : " + player.get_current_station())
        screen.addstr(3, 0, "Destination                : " + player.get_target_station())
        screen.addstr(4, 0, "Time to compelte           : " + points_str)
        screen.addstr(5, 0, "Stations visited           : " + str(stations_visited) +
                      " / " + str(num_stations) + " (" + str(ratio) + "%)")
        screen.refresh()
        c = screen.getch()
        if c == ord("\n"):
            running = False
        time.sleep(0.1)

def get_time_string (hours: int, minutes: int) -> str:
    """creates a time string from integer hours and minutes"""
    string = ""
    if hours < 10:
        string += "0"
    string += str(hours) + ":"
    if minutes < 10:
        string += "0"
    string += str(minutes)
    return string

def is_connected(url:str="https://www.google.com", timeout:int=1):
    """tests internet connectivity"""
    try:
        with request.urlopen(url, timeout=timeout):
            return True
    except error.URLError:
        return False
    except TimeoutError:
        return False

def get_longest_station_departure (station_departures: Any):
    """read function name"""
    longest = 0
    for departure in station_departures.items():
        for i in range(0, len(departure[1])):
            length = 6 + len(departure[1][i]["name"]) + 5 + len(departure[1][i]["destination"]) + 3
            longest = max(longest, length)
    return longest

# pokemon mini : 96 x 64 (9 x 3) : too small
# gameboy : 160 x 144 (16 x 7) : too small
# gameboy advance : 240 x 160 (24 x 8)
# pico calc : 320 x 320 (32 x 16)
# uConsole (720p) : 1,280 x 720 (128 x 36)

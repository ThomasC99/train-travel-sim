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
            service_data = network_data["services"][service]
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
    points_str = ""
    if points >= 43200: # months
        points_str += str(int(points // 43200)) + " months, "
        points = points % 43200
    if points >= 10080: # weeks
        points_str += str(int(points // 10080)) + " weeks, "
        points = points % 10080
    if points >= 1440: # days
        points_str += str(int(points // 1440)) + " days, "
        points = points % 1440
    if points >= 60: # hours
        points_str += str(int(points // 60)) + " hours, "
        points = points % 60
    points_str += str(points) + " mintues"
    return points_str

def display_stats (screen: Any, player: Player): # TODO
    """displays the player's stats"""
    running = True
    points = calc_points_needed(player)
    points_str = points_to_time_str(points)
    station_list: list[str] = []
    for station in player.get_service_data().get_stations().keys():
        if station not in station_list:
            station_list.append(station)
    if player.get_network_data() is not None and "stations" in player.get_network_data():
        for station in player.get_network_data()["stations"].keys():
            if station not in station_list:
                station_list.append(station)
    num_stations = len(station_list)
    stations_visited = len(player.get_visited_stations())
    ratio: int = int(stations_visited / num_stations * 100)
    while running:
        screen.clear()
        screen.addstr(0, 0, "Points           : " + str(player.get_points()))
        screen.addstr(1, 0, "Current Location : " + player.get_current_station())
        screen.addstr(2, 0, "Destination      : " + player.get_target_station())
        screen.addstr(3, 0, "Time to compelte : " + points_str)
        screen.addstr(4, 0, "Stations visited : " + str(stations_visited) +
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

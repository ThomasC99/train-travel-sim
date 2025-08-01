"""library for cli screens"""
import curses
import json
import random
import time
from curses import wrapper
from typing import Any
import pygame

from gtts import gTTS # type: ignore
from pydub import AudioSegment # type: ignore

from player import Player
from utils import load_json_file, get_time_string, display_stats, is_connected
from loc import get_and_text, get_station_announcement_base, get_announcement_base
from loc import get_route_announcement_base

def handle_opts (player: Player, c: int):
    """handles character inputs for playing options"""
    if c == ord("r") or c == ord("R"):
        player.set_random_route(not player.get_random_route())
    if c == ord("s") or c == ord("S"):
        player.set_silence(not player.get_silence())
    if c == ord("A") or c == ord("a"):
        player.set_announcement(not player.get_announcement())

def select_departure_time (screen: Any):
    """Allows the user to select a departure time"""
    screen.nodelay(False)
    running = True
    user_time = ""
    while running:
        screen.clear()
        screen.addstr(0, 0, "Input departure time")
        screen.addstr(1, 0, user_time)
        screen.refresh()
        c = screen.getkey()
        if c == "\n":
            running = False
        elif c in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ":"]:
            user_time += c
        time.sleep(0.01)
    screen.nodelay(True)
    return user_time

def save_debug_data (data: Any):
    """Saves a log when the program crashes"""
    with open("log.txt", "w", encoding="utf-8") as file:
        file.write(data)

def get_time_string_seocnds (hours: int, minutes: int, seconds: int):
    """creates a time string from integer hours, minutes and seconds"""
    string = get_time_string(hours, minutes) + ":"
    if seconds < 10:
        string += "0"
    string += str(seconds)
    return string

def work (screen: Any, player: Player):
    """allows the player to work and earn points"""
    running = True
    worked = time.time()
    wage: float = player.get_wage()
    r = time.time()
    while running:
        screen.clear()
        screen.addstr(0, 0, get_time_string(time.localtime().tm_hour, time.localtime().tm_min))
        screen.addstr(1, 0, f"Wage   : {wage:,.2f}")
        screen.addstr(2, 0, "Points : " + str(player.get_points()))
        screen.addstr(4, 0, "Back", curses.A_STANDOUT)
        if (((time.time() - worked) / 3600) * wage) > 1:
            player.set_points(player.get_points() + int(((time.time() - worked) / 3600) * wage))
            worked = time.time()
        if (time.time() - r) >= 1:
            wage *= 1 + (0.00000125 / (3 * 60))
            r = time.time()
        screen.refresh()
        c = screen.getch()
        if c == ord("\n"):
            running = False
        time.sleep(0.01)
    player.set_wage(wage)

def level_select (screen: Any) -> str:
    """"Allows the user to select a level"""
    levels: dict[str, str]
    level_list: list[str]
    with open("levels.json", "r", encoding="utf-8") as file:
        levels = json.loads(file.read())
        level_list = list(levels.keys())
    file.close()
    cursor = 0
    running = True
    result = ""
    while running:
        screen.clear()
        for i in range (0, len(level_list)): # TODO pylint: disable=consider-using-enumerate
            if i == cursor:
                screen.addstr(i, 0, level_list[i], curses.A_STANDOUT)
            else:
                screen.addstr(i, 0, level_list[i])
        c = screen.getch()
        if c == curses.KEY_UP and cursor > 0:
            cursor -= 1
        elif c == curses.KEY_DOWN and cursor < len(level_list) - 1:
            cursor += 1
        elif c == ord("\n"):
            result = levels[level_list[cursor]]
            running = False
    return result

def get_reversed_schedule (service: Any) -> Any:
    """reverses the schedule of a service"""
    reversed_schedule: Any = {}
    for i in range (len(list(service["schedule"].keys())) - 1, -1, -1):
        reversed_element = ""
        element = list(service["schedule"].keys())[i]
        element = element.split(" - ")
        reversed_element = element[1] + " - " + element[0]
        reversed_schedule[reversed_element] = service["schedule"][list(service["schedule"].keys())[i]]
    return reversed_schedule

def combine_departures (target: Any, source: Any) -> Any:
    """combines departures"""
    for key in source:
        if key not in target:
            target[key] = []
        for element in source[key]:
            target[key].append(element)
    return target

def sort_departures (current_time: str, departures: Any) -> Any: # TODO
    """sorts the departures based on the current time"""
    index = 0
    keys = list(departures.keys())
    keys.sort()
    for departure in keys:
        current_time_hours = int(current_time.split(":")[0])
        if (current_time_hours == int(departure.split(":")[0]) and int(current_time.split(":")[1]) <= int(departure.split(":")[1])) and index == 0:
            index = keys.index(departure)
        if (int(current_time.split(":")[0]) < int(departure.split(":")[0])) and index == 0:
            index = keys.index(departure)
        if current_time == departure:
            index = keys.index(departure)
            break
    sort: list[str] = []
    for i in range (index, len(departures)):
        sort.append(keys[i])
    for i in range (0, index):
        sort.append(keys[i])
    sorted_departures: Any = {}
    for element in sort:
        sorted_departures[element] = departures[element]
    return sorted_departures

def generate_service_times (service_data: Any, station_name: str, direction: str, current_time: str) -> Any: # TODO
    """Generates the service times for a given station"""
    sequence: Any = {}
    hour = int(current_time.split(":")[0])
    minute = int(current_time.split(":")[1])
    if station_name == service_data["origin"]:
        total_time = 0
        sequence[current_time] = station_name
        for item in service_data["schedule"]:
            total_time += service_data["schedule"][item]
            new_min = minute + total_time
            new_hour = hour + new_min // 60
            new_hour = new_hour % 24
            new_min = new_min % 60
            sequence[get_time_string(new_hour, new_min)] = item.split(" - ")[1]
    elif station_name == service_data["destination"]:
        total_time = 0
        schedule = get_reversed_schedule(service_data)
        sequence[current_time] = station_name
        for item in schedule:
            total_time += schedule[item]
            new_min = minute + total_time
            new_hour = hour + new_min // 60
            new_hour = new_hour % 24
            new_min = new_min % 60
            sequence[get_time_string(new_hour, new_min)] = item.split(" - ")[1]
    elif direction == service_data["destination"]:
        schedule = get_reversed_schedule(service_data)
        keys = list(service_data["schedule"].keys())
        index = 0
        for i in range (0, len(keys)):
            if station_name == keys[i].split(" - ")[0]:
                index = i
        total_time = 0
        for i in range (index, len(keys)):
            total_time += service_data["schedule"][keys[i]]
            new_min = minute + total_time
            new_hour = hour + new_min // 60
            new_hour = new_hour % 24
            new_min = new_min % 60
            sequence[get_time_string(new_hour, new_min)] = keys[i].split(" - ")[1]
    elif direction == service_data["origin"]:
        schedule = get_reversed_schedule(service_data)
        sequence[current_time] = station_name
        keys = list(schedule.keys())
        index = 0
        for i in range (0, len(keys)):
            if station_name == keys[i].split(" - ")[0]:
                index = i
        total_time = 0
        for i in range (index, len(keys)):
            total_time += schedule[keys[i]]
            new_min = minute + total_time
            new_hour = (hour + (new_min // 60)) % 24
            new_min = new_min % 60
            sequence[get_time_string(new_hour, new_min)] = keys[i].split(" - ")[1]
    return sequence

def get_travel_time (schedule: Any, start: str, end: str) -> int:
    """Calculates the travel time between two stations in a schedule."""
    if start == end:
        return 0
    start_index = 0
    items = list(schedule.keys())
    for i in range (0, len(items)):
        if start == items[i].split(" - ")[0]:
            start_index = i
            break
    total_time = 0
    for i in range (start_index, len(items)):
        total_time += schedule[items[i]]
        if items[i].split(" - ")[1] == end:
            return total_time
    return total_time

def add_route (screen: Any, player: Player, service_name: str):
    """Adds a route to the player's service data"""
    network_data = player.get_network_data()
    service_data = player.get_service_data()
    service = network_data["services"][service_name]
    service_data["services"][service_name] = {} # TODO
    service_data["services"][service_name]["origin"] = list(service.keys())[0].split(" - ")[0] # TODO
    service_data["services"][service_name]["destination"] = list(service.keys())[-1].split(" - ")[1] # TODO
    service_data["services"][service_name]["schedule"] = network_data["services"][service_name] # TODO
    schedule = list(service.keys())
    stations: list[str] = []

    for i in range (0, len(schedule)):
        schedule_item = schedule[i].split(" - ")
        stations.append(schedule_item[0])
        stations.append(schedule_item[1])

    # add stations into player data
    for station in stations:
        if station not in list(service_data["stations"].keys()): # TODO
            service_data["stations"][station] = [] # TODO
        if service_name not in service_data["stations"][station]: # TODO
            service_data["stations"][station].append(service_name) # TODO

    departure_time = select_departure_time(screen)
    hours = int(departure_time.split(":")[0]) % 24
    minutes = int(departure_time.split(":")[1]) % 60

    time_offset = minutes % 5
    service_data["services"][service_name]["time-offset"] = time_offset # TODO
    service_data["services"][service_name]["departures"] = [] # TODO

    service_data["services"][service_name]["departures"].append(get_time_string(hours, minutes)) # TODO
    del network_data["services"][service_name] # TODO
    if len(network_data["services"]) == 0: # TODO
        del network_data["services"] # TODO
    for station in stations:
        if station in network_data["stations"]: # TODO
            if service_name in network_data["stations"][station]: # TODO
                del network_data["stations"][station][network_data["stations"][station].index(service_name)] # TODO
    for station in stations:
        if station in list(network_data["stations"].keys()): # TODO
            if len(network_data["stations"][station]) == 0: # TODO
                del network_data["stations"][station] # TODO
    player.set_network_data(network_data)
    player.set_service_data(service_data)

def display_menu (screen: Any, menu: list[str]) -> str:
    """Displays a curses menu and returns the option selected"""
    rows = screen.getmaxyx()[0]
    rows -= 3
    page = 0
    running = True
    cursor = 0
    option = ""
    while running:
        pages = int((len(menu) / (rows)) - 1) + 1
        if page > pages:
            page = pages
        screen.clear()
        for i in range (page * rows, len(menu) if len(menu) < (page + 1) * rows else (page + 1) * rows):
            if cursor == i:
                screen.addstr(i, 0, menu[i], curses.A_STANDOUT)
            else:
                screen.addstr(i, 0, menu[i])
        screen.refresh()
        c = screen.getch()
        if c == curses.KEY_UP and cursor > 0:
            cursor -=1
        elif c == curses.KEY_DOWN and cursor < len(menu) - 1:
            cursor += 1
        elif c == curses.KEY_LEFT and page == 0:
            running = False
            return "Back"
        elif c == curses.KEY_LEFT and page > 0:
            page -= 1
        elif c == curses.KEY_RIGHT and page < pages:
            page += 1
        elif c == ord("\n"):
            running = False
            option = menu[cursor]
    return option

def create_annoucement (text: str, lang: str, accent: str) -> gTTS:
    """creates an announcement using GTTS"""
    result = None
    if accent != "":
        result = gTTS(text=text, lang=lang, tld=accent, slow=False, timeout=30)
    else:
        result = gTTS(text=text, lang=lang, slow=False, timeout=30)
    return result

def beep (player: Player, current_time: str):
    """plays the alert beep"""
    if player.get_last_beep() != current_time and not player.get_silence():
        pygame.mixer.music.load("./temp/arrival-chime.mp3")
        pygame.mixer.music.play(1)
        player.set_last_beep(current_time)

def create_announcement_and_play(player: Player, announcement: Any, time_str: str, lang:str, tld:str):
    """creates an announcement and plays it"""

    # Check for silence setting or duplicate beep within the same minute
    if player.get_silence() or player.get_last_beep() == time_str:
        return

    if not player.get_announcement():
        beep(player, time_str)
        return

    # Check for internet connection
    if not is_connected():
        beep(player, time_str)
        return

    try:
        # Generate and save the announcement speech
        text_to_speech: Any = None
        if tld != "":
            text_to_speech = gTTS(text=announcement, lang=lang, tld=tld, slow=False, timeout=30)
        else:
            text_to_speech = gTTS(text=announcement, lang=lang, slow=False, timeout=30)
        text_to_speech.save("temp/announce.mp3")

        # Load and merge audio files
        sound1: Any = AudioSegment.from_mp3("./temp/arrival-chime.mp3") # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        sound2: Any = AudioSegment.from_mp3("./temp/announce.mp3") # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        sound3: Any = sound1.append(sound2) # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        sound_file: Any = sound3.export("./temp/chime-announce.mp3", format="mp3") # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        pygame.mixer.music.load(sound_file) # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType, reportUnknownMemberType]
        pygame.mixer.music.play()
        player.set_last_beep(time_str)

    except (FileNotFoundError, IOError):
        beep(player, time_str)

    except Exception:
        beep(player, time_str)

def display_opts (player: Player, screen: Any):
    """Displays the playing options"""
    if player.get_random_route():
        screen.addstr(0, 11, "R")
    if player.get_silence():
        screen.addstr(0, 12, "S")
    if player.get_announcement():
        screen.addstr(0, 13, "A")

def display_route_header(player: Player, screen: Any, time_str: str, destination: str,
                         service_name: str, direction: str):
    """Creates the route header, to be used to diplay a service"""
    screen.addstr(0, 0, time_str)
    display_opts(player, screen)
    screen.addstr(1, 0, destination)
    screen.addstr(2, 0, f"{service_name} ({direction})")

def display_service (screen: Any, service: Any, service_name: str, direction: str,
                     destination: str, player: Player):
    """displays the progression of the service that the player is riding"""
    running = True
    new_station = ""
    delete_first = False
    rows, cols = screen.getmaxyx()
    station_length = 0
    menu_items = list(service.keys())
    for item in menu_items:
        item_length = len(service[item]) + 18
        if item_length > station_length:
            station_length = item_length
    station_columns = int(cols / station_length) - 1
    while running:
        route_announcement: str = get_route_announcement_base(player.get_language()).replace("SERVICE", service_name).replace("DIR", direction)
        hour = time.localtime().tm_hour
        minute = time.localtime().tm_min
        sec = time.localtime().tm_sec
        time_str = get_time_string(hour, minute)
        time_str_sec = get_time_string_seocnds(hour, minute, sec)
        screen.clear()
        display_route_header(player, screen, time_str_sec, destination, service_name, direction)
        menu_items = 0
        highlight = False
        station = ""
        column = 0
        for i in range (0, len(list(service.keys()))):
            station_iter = service[list(service.keys())[i]]
            if station_iter not in player.get_visited_stations():
                station_iter += " *"
            if time_str == list(service.keys())[i]:
                screen.addstr(4 + menu_items, column * station_length, list(service.keys())[i] +
                              "   " + station_iter, curses.A_STANDOUT)
                station = service[list(service.keys())[i]]
                highlight = True
            else:
                screen.addstr(4 + menu_items, column * station_length, list(service.keys())[i] +
                              "   " + station_iter)
            if column > station_columns:
                break
            elif menu_items >= rows - 7:
                column += 1
                menu_items = 0
            else:
                menu_items += 1
        c = screen.getch()
        if c == ord("\n") and time_str in service:
            new_station = service[time_str]
            running = False
        handle_opts(player, c)
        if player.get_random_route() and time_str in service and service[time_str] == destination:
            new_station = service[time_str]
            running = False
        first = list(service.keys())[0]
        if first == time_str:
            delete_first = True
        if first == time_str:
            create_announcement_and_play(player, get_announcement_base(player.get_language()) + " "
                                         + station, time_str, player.get_language(),
                                         player.get_accent())
            player.set_last_beep(time_str)
        if delete_first and time_str != first:
            if len(service) == 1:
                new_station = service[list(service.keys())[0]]
            del service[first]
            delete_first = False
        if len(list(service.keys())) == 0:
            running = False
            break
        if highlight == False and player.get_last_beep() != time_str:
            length = len(list(service.keys()))
            for i in range (0, length):
                route_announcement += service[list(service.keys())[i]] + ", "
                if i == length - 2:
                    route_announcement += get_and_text(player.get_language())
            create_announcement_and_play(player, route_announcement, time_str,
                                         player.get_language(), player.get_accent())
        screen.refresh()
        time.sleep(0.01)
    return new_station

def create_initial_timetable (player: Player, screen: Any):
    """Creates the timetable when the user first begins a level"""
    network_data = player.get_network_data()
    service_list = list(network_data["services"].keys())
    service_name = ""

    running = True
    cursor = 0
    while running:
        screen.clear()
        for i in range(0, len(service_list)):
            screen.addstr(i, 0, service_list[i], curses.A_STANDOUT if cursor == i else curses.A_NORMAL)
        c = screen.getch()
        if c == ord("\n"):
            service_name = service_list[cursor]
            running = False
        elif c == curses.KEY_UP and cursor > 0:
            cursor -= 1
        elif c == curses.KEY_DOWN and cursor < len(service_list) - 1:
            cursor += 1
        time.sleep(0.01)


    # service_name = service_list[random.randint(0, len(service_list) - 1)]
    service_data = player.get_service_data()
    service_data["services"] = {} # TODO
    service_data["services"][service_name] = {} # TODO
    service_data["services"][service_name]["schedule"] = network_data["services"][service_name] # TODO
    service_data["stations"] = {} # TODO
    service = network_data["services"][service_name] # TODO
    service_data["services"][service_name]["origin"] = list(service.keys())[0].split(" - ")[0] # TODO
    service_data["services"][service_name]["destination"] = list(service.keys())[-1].split(" - ")[1] # TODO
    schedule = list(service.keys()) # TODO
    stations: list[str] = []

    for i in range (0, len(schedule)):
        schedule_item = schedule[i].split(" - ")
        stations.append(schedule_item[0])
        stations.append(schedule_item[1])

    # add stations into player data
    for station in stations:
        if station not in list(service_data["stations"].keys()): # TODO
            service_data["stations"][station] = [] # TODO
        if service_name not in service_data["stations"][station]: # TODO
            service_data["stations"][station].append(service_name) # TODO

    departure_time = select_departure_time(screen)

    hours = int(departure_time.split(":")[0]) % 24
    minutes = int(departure_time.split(":")[1]) % 60
    time_offset = minutes % 5
    service_data["services"][service_name]["time-offset"] = time_offset # TODO
    service_data["services"][service_name]["departures"] = [] # TODO

    service_data["services"][service_name]["departures"].append(get_time_string(hours, minutes)) # TODO
    del network_data["services"][service_name] # TODO
    if len(network_data["services"]) == 0: # TODO
        del network_data["services"] # TODO
    for station in stations:
        if station in network_data["stations"]: # TODO
            if service_name in network_data["stations"][station]: # TODO
                del network_data["stations"][station][network_data["stations"][station].index(service_name)] # TODO
    for station in stations:
        if station in list(network_data["stations"].keys()): # TODO
            if len(network_data["stations"][station]) == 0: # TODO
                del network_data["stations"][station] # TODO
    if len(network_data["stations"]) == 0: # TODO
        del network_data["stations"] # TODO
    if len(network_data) == 0: # TODO
        network_data = None
    player.set_service_data(service_data)
    player.set_network_data(network_data)

def get_station_departures (service_name: str, service: Any, station: str) -> Any:
    """Gets the departures for 24 hours for the specified station"""
    departures: Any = {}
    if station == service["destination"]: # TODO
        for departure in service["departures"]: # TODO
            if departure not in departures:
                departures[departure] = []
            departures[departure].append(service_name + " (" + service["origin"] + ")") # TODO
    elif station == service["origin"]: # TODO
        for departure in service["departures"]: # TODO
            if departure not in departures:
                departures[departure] = []
            departures[departure].append(service_name + " (" + service["destination"] + ")") # TODO
    else:

        # Forward direction
        for departure in service["departures"]: # TODO
            total_time = 0
            for stop in service["schedule"]: # TODO
                total_time += service["schedule"][stop] # TODO
                if stop.split(" - ")[1] == station:
                    break
            minute = int(departure.split(":")[1]) + total_time
            hours = int(departure.split(":")[0]) + (minute // 60)
            hours = hours % 24
            minute = minute % 60
            time_str = get_time_string(hours, minute)
            if time_str not in departures:
                departures[time_str] = []
            departures[time_str].append(service_name + " (" + service["destination"] + ")") # TODO

        # Backward direction
        reversed_schedule = get_reversed_schedule(service)

        for departure in service["departures"]: # TODO
            total_time = 0
            for stop in reversed_schedule:
                total_time += reversed_schedule[stop]
                if stop.split(" - ")[1] == station:
                    break
            minute = int(departure.split(":")[1]) + total_time
            hours = int(departure.split(":")[0]) + (minute // 60)
            hours = hours % 24
            minute = minute % 60
            time_str = get_time_string(hours, minute)
            if time_str not in departures:
                departures[time_str] = []
            departures[time_str].append(service_name + " (" + service["origin"] + ")") # TODO

    return departures

def discovered_all_stations (screen: Any, points: int):
    """shows a screen telling the player that they have discovered all station in a level"""
    running: bool = True
    while running:
        screen.clear()
        screen.addstr(2, 0, "Congradulations!")
        screen.addstr(3, 0, "You have discovered all stations in this system!")
        screen.addstr(4, 0, "You have been awarded " + str(points) + " points.")
        screen.refresh()
        time.sleep(0.1)
        c: int = screen.getch()
        if c == ord("\n"):
            running = False

def discovered_station (screen: Any, station: str):
    """shows a player a screen telling them they have discovered a new station"""
    running: bool = True
    while running:
        screen.clear()
        screen.addstr(2, 0, "Congradulations!")
        screen.addstr(3, 0, "You have visited " + station + " for the first time!")
        screen.addstr(4, 0, "You have been awarded 60 points.")
        screen.refresh()
        time.sleep(0.1)
        c: int = screen.getch()
        if c == ord("\n"):
            running = False

def station_screen (screen: Any, player: Player):
    """The departure board of the player's current station"""
    running = True
    cursor = 0
    rows, cols = screen.getmaxyx()
    while running: # 39
        hour = time.localtime().tm_hour
        minute = time.localtime().tm_min
        sec = time.localtime().tm_sec
        time_str = get_time_string(hour, minute)
        time_str_sec = get_time_string_seocnds(hour, minute, sec)

        if player.get_current_station not in player.get_visited_stations(): # TODO
            visited_stations = player.get_visited_stations()
            visited_stations.append(player.get_current_station())
            player.set_visited_stations(visited_stations)
            player.set_points(player.get_points() + 60)
            discovered_station(screen, player.get_current_station())

        service_data = player.get_service_data()
        network_data = player.get_network_data()
        station_list:list[str] = []
        for station in service_data["stations"].keys():
            if station not in station_list:
                station_list.append(station)
        if "stations" in network_data:
            for station in network_data["stations"].keys():
                if station not in station_list:
                    station_list.append(station)
        if not player.get_visited_all_stations() and len(player.get_visited_stations()) == len(station_list):
            # 25% of all points awarded for exploring stations
            disc_points:int = int(len(station_list) * 60 * 1.25)
            player.set_points(player.get_points() + disc_points)
            player.set_visited_all_stations(True)
            discovered_all_stations(screen, disc_points)

        station_departures = {}

        if player.get_target_station() == "":
            player.set_target_station(list(service_data["stations"].keys())[random.randint(0, len(list(service_data["stations"].keys())) - 1)]) # TODO

        for service in service_data["stations"][player.get_current_station()]: # TODO
            departures = get_station_departures(service, service_data["services"][service], player.get_current_station()) # TODO
            combine_departures(station_departures, departures)

        station_departures = sort_departures(time_str, station_departures)
        for dep in station_departures.items():
            dep[1].sort()

        screen.clear()
        screen.addstr(0, 0, time_str_sec)
        display_opts(player, screen)
        screen.addstr(1, 0, player.get_current_station() + " (" + player.get_target_station() + ")")

        menu_items = 0
        deps = False
        station_announcement: str = ""
        col = 0

        longest = 0
        for departure in station_departures.items():
            for i in range(0, len(departure[1])):
                length = len(departure[1][i]) + 15
                longest = max(longest, length)

        total_cols = int(cols / longest) - 1

        for departure in station_departures:
            screen.addstr(3 + menu_items, (col * longest), departure)
            for i in range (0, len(station_departures[departure])):
                if departure == time_str:
                    deps = True
                if departure == time_str and cursor == i:
                    screen.addstr(3 + menu_items, 7 + (col * longest), station_departures[departure][i], curses.A_STANDOUT)
                else:
                    screen.addstr(3 + menu_items, 7 + (col * longest), station_departures[departure][i])
                if departure == time_str:
                    station_announcement += get_station_announcement_base(player.get_language()).replace("SERVICE", station_departures[departure][i].split("(")[0]).replace("DEST", station_departures[departure][i].split("(")[1].replace(")", ""))
                if menu_items >= rows - 4:
                    col += 1
                    menu_items = 0
                if col > total_cols:
                    break
                menu_items += 1
            if menu_items >= rows - 4:
                col += 1
                menu_items = 0
            if col > total_cols:
                break

        if deps:
            if not player.get_announcement():
                create_announcement_and_play(player, station_announcement, time_str, player.get_language(), player.get_accent())
            else:
                beep(player, time_str)

        c = screen.getch() # 18
        if time_str not in station_departures:
            cursor = 0
        handle_opts(player, c)
        if c == ord("q") or c == ord("Q"):
            running = False
        elif c == curses.KEY_DOWN and time_str in station_departures and cursor < len(station_departures[time_str]) - 1:
            cursor += 1
        elif c == curses.KEY_UP and cursor > 0:
            cursor -= 1
        elif c == curses.KEY_LEFT:
            running = False
        elif (c == ord("\n") or player.get_random_route()) and time_str in station_departures:
            if player.get_random_route():
                player.save_game()
            service_name = station_departures[time_str][cursor]
            direction = service_name.split(" (")[-1].replace(")", "")
            service_name = service_name.split(" (")[0]
            service_desc = service_data["services"][service_name] # TODO
            service_sequence = generate_service_times(service_desc, player.get_current_station(), direction, time_str) # TODO
            new_station = display_service(screen, service_sequence, service_name, direction, player.get_target_station(), player) # TODO
            times = None
            if direction == service_desc["destination"]: # TODO
                times = service_desc["schedule"] # TODO
            else:
                times = get_reversed_schedule(service_data)
            player.set_points(player.get_points() + get_travel_time(times, player.get_current_station(), new_station)) # TODO
            player.set_current_station(new_station)
        if player.get_current_station() == player.get_target_station():
            player.set_points(player.get_points() + 60)
            player.set_target_station("")
        screen.refresh()
        time.sleep(0.1)

def buy_new_route (screen: Any, player: Player, services: Any):
    """diplays the routes that the user can purchace"""
    rows = screen.getmaxyx()[0]
    rows -= 5
    route_list = list(services.keys())
    cursor = 0
    running = True
    while running:
        menu = []
        if len(route_list) > rows:
            menu = route_list[:rows]
        else:
            menu = route_list
        if "Back" not in menu:
            menu.append("Back")
        screen.clear()
        screen.addstr(0, 0, "Points : " + str(player.get_points())) # TODO
        for i in range (0, len(menu)):
            if menu[i] != "Back":
                screen.addstr(i + 2, 0, menu[i] + " (" + str(services[route_list[i]]) + ")", curses.A_STANDOUT if cursor == i else curses.A_NORMAL)
            else:
                screen.addstr(i + 2, 0, menu[i], curses.A_STANDOUT if cursor == i else curses.A_NORMAL)
        c = screen.getch()
        if c == curses.KEY_DOWN and cursor < len(menu) - 1:
            cursor += 1
        elif c == curses.KEY_UP and cursor > 0:
            cursor -= 1
        elif c == ord("\n"):
            if menu[cursor] == "Back":
                running = False
            else:
                if player.get_points() >= services[route_list[cursor]]: # TODO
                    player.set_points(player.get_points() - services[route_list[cursor]])
                    add_route(screen, player, route_list[cursor])
                    del services[route_list[cursor]]
                    del route_list[cursor]
        screen.refresh()
        time.sleep(0.01)

def buy_new_departures (screen: Any, player: Player, departures: Any, service: str):
    """Allows a player to buy a new departure for a route they own, and adds it to the timetable"""
    cursor = 0
    running = True
    total_cost = 0
    rows = screen.getmaxyx()[0]
    rows -= 4
    page = 0
    service_data: Any = player.get_service_data()
    for item in service_data["services"][service]["schedule"]: # TODO
        total_cost += service_data["services"][service]["schedule"][item] # TODO
    total_cost *= 2
    while running:
        pages = int((len(departures) / (rows)) - 1) + 1
        if page > pages:
            page = pages
        menu = []
        max_index = (page * rows) + rows
        if max_index >= len(departures):
            max_index = len(departures)
        menu = departures[int(page * rows) : max_index]
        screen.clear()
        screen.addstr(0, 0, "Points            : " + str(player.get_points()))
        screen.addstr(1, 0, "Cost              : " + str(total_cost))
        screen.addstr(2, 0, "Departures to buy : " + str(len(departures)))
        for i in range (0, len(menu)):
            if cursor == i:
                screen.addstr(i + 4, 0, menu[i], curses.A_STANDOUT)
            else:
                screen.addstr(i + 4, 0, menu[i])
        c = screen.getch()
        if c == curses.KEY_DOWN and cursor < len(menu) - 1:
            cursor += 1
        elif c == curses.KEY_UP and cursor > 0:
            cursor -= 1
        elif c == curses.KEY_LEFT and page == 0:
            running = False
        elif c == curses.KEY_LEFT and page > 0:
            page -= 1
            cursor = 0
        elif c == curses.KEY_RIGHT and page < pages:
            page += 1
            cursor = 0
        elif c == ord("\n"):
            if player.get_points() >= total_cost:
                player.set_points(player.get_points() - total_cost)
                service_data["services"][service]["departures"].append(departures[cursor + (page * rows)]) # TODO
                service_data["services"][service]["departures"].sort() # TODO
                del departures[cursor + (page * rows)]
                player.set_service_data(service_data)
        screen.refresh()
        time.sleep(0.01)

def buy_new_departure_services (screen: Any, player: Player, services: Any): # TODO
    """A menu displaying the services for which a player can buy a departure"""
    running = True
    while running:
        menu = list(services.keys())
        menu_with_costs: list[str] = []
        for item in menu:
            cost = 0
            service = player.get_service_data()["services"][item] # TODO
            for leg in service["schedule"]: # TODO
                cost += service["schedule"][leg] # TODO
            cost *= 2
            menu_with_costs.append(item + " (" + str(cost) + ")")
        menu.append("Back")
        menu_with_costs.append("Back")
        result = menu[menu_with_costs.index(display_menu(screen, menu_with_costs))]
        if result == "Back":
            running = False
        else:
            buy_new_departures(screen, player, services[result], result)

def store (screen: Any, player: Player):
    """The main page of the store"""
    new_routes: Any = {}
    new_departures: Any = {}
    service_data = player.get_service_data()
    network_data = player.get_network_data()
    if len(network_data) > 0 and "services" in network_data: # TODO
        routes = list(network_data["services"].keys()) # TODO
        for route in routes:
            total_cost = 0
            for item in network_data["services"][route]: # TODO
                total_cost += network_data["services"][route][item] # TODO
            total_cost *= 2
            new_routes[route] = total_cost
    for route in service_data["services"]: # TODO
        offset = service_data["services"][route]["time-offset"] # TODO
        departures = service_data["services"][route]["departures"] # TODO
        avail: list[str] = []
        for i in range (0, 24):
            for j in range (0, 12):
                time_str = get_time_string(i, offset + (j * 5))
                if time_str not in departures:
                    avail.append(time_str)
        if len(avail) > 0:
            new_departures[route] = avail
    menu: list[str] = []
    if len(new_routes) > 0:
        menu.append("New routes (" + str(len(new_routes)) + ")" )
    if len(new_departures) > 0:
        menu.append("New departures (" + str(len(new_departures)) + " routes)")
    menu.append("Back")

    running = True
    while running:
        result = display_menu(screen, menu)
        if result == "Back":
            running = False
        if "New routes" in result:
            buy_new_route(screen, player, new_routes)
        if "New departures" in result:
            buy_new_departure_services(screen, player, new_departures)

def create_all_services (player: Player):
    """Only used for level testing, creates all services and departures"""
    network_data: Any = player.get_network_data()
    service_list = list(network_data["services"].keys())
    service_data: Any = player.get_service_data()

    service_data["services"] = {} # TODO
    service_data["stations"] = {} # TODO

    for service_name in service_list:
        service_data["services"][service_name] = {} # TODO
        service_data["services"][service_name]["schedule"] = network_data["services"][service_name] # TODO
        service = network_data["services"][service_name] # TODO
        service_data["services"][service_name]["origin"] = list(service.keys())[0].split(" - ")[0] # TODO
        service_data["services"][service_name]["destination"] = list(service.keys())[-1].split(" - ")[1] # TODO
        schedule = list(service.keys())
        stations: list[str] = []

        for i in range (0, len(schedule)):
            schedule_item = schedule[i].split(" - ")
            stations.append(schedule_item[0])
            stations.append(schedule_item[1])

        # add stations into player data
        for station in stations:
            if station not in list(service_data["stations"].keys()): # TODO
                service_data["stations"][station] = [] # TODO
            if service_name not in service_data["stations"][station]: # TODO
                service_data["stations"][station].append(service_name) # TODO
        time_offset = random.randint(0, 5)
        service_data["services"][service_name]["time-offset"] = time_offset # TODO
        service_data["services"][service_name]["departures"] = [] # TODO

        for hours in range (0, 24):
            for minutes in range (time_offset, 60, 5):
                service_data["services"][service_name]["departures"].append(get_time_string(hours, minutes)) # TODO

        del network_data["services"][service_name] # TODO
        if len(network_data["services"]) == 0: # TODO
            del network_data["services"] # TODO
        for station in stations:
            if station in network_data["stations"]: # TODO
                if service_name in network_data["stations"][station]: # TODO
                    del network_data["stations"][station][network_data["stations"][station].index(service_name)] # TODO
        for station in stations:
            if station in list(network_data["stations"].keys()): # TODO
                if len(network_data["stations"][station]) == 0: # TODO
                    del network_data["stations"][station] # TODO
        if len(network_data["stations"]) == 0: # TODO
            del network_data["stations"] # TODO
        if len(network_data) == 0:
            network_data = None
    player.set_service_data(service_data)
    player.set_network_data(network_data)

def main (screen: Any):
    """Allows the player to start a new game, or load one from the save file"""
    pygame.init() # pylint: disable=no-member
    curses.curs_set(False)
    screen.nodelay(True)
    player = Player()

    new_game = display_menu(screen, ["New Game", "Load Game", "Test"])
    if new_game == "Load Game":
        player.load_game()
    else:
        level = level_select(screen)
        player.set_network_data(load_json_file(level))
        player_data = player.get_json_data()
        if new_game == "New Game":
            create_initial_timetable(player, screen)
        elif new_game == "Test":
            create_all_services(player)
        player.load_json(player_data)
        player.set_current_station(list(player.get_service_data()["stations"].keys())[random.randint(0, len(list(player.get_service_data()["stations"].keys())) - 1)]) # TODO

    running = True
    while running:
        menu = ["Station", "Work", "Store", "Stats", "Save", "Quit"]
        choice = display_menu(screen, menu)
        if choice == "Station":
            station_screen(screen, player)
        elif choice == "Work":
            work(screen, player)
        elif choice == "Store":
            store(screen, player)
        elif choice == "Stats":
            display_stats(screen, player)
        elif choice == "Save":
            player.save_game()
        elif choice == "Quit":
            running = False
            time.sleep(0.01)

wrapper(main) # 134

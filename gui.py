import curses
import json
import random
import time
import pygame
import re

from curses import wrapper
from urllib import request
from gtts import gTTS
from pydub import AudioSegment
from pydub.utils import ratio_to_db

last_beep = ""
route_announcements = None
ran = False
scilence = False
announcements = False

def is_connected ():
    try:
        request.urlopen("https://www.google.com", timeout=1)
        return True
    except:
        return False

def create_announcement_and_play (announcement, time_str):
    global last_beep
    if scilence or last_beep == time_str:
        return
    elif not is_connected():
        beep(time_str)
        return
    try:
        text_to_speech = gTTS(text=announcement, lang='en', tld="ca", slow=False)
        text_to_speech.save("announce.mp3")
        sound1 = AudioSegment.from_mp3("./arrival-chime.mp3")
        sound2 = AudioSegment.from_mp3("./announce.mp3")
        sound3 = sound1.append(sound2)
        sound3.export("chime-announce.mp3", format="mp3")
        pygame.mixer.music.load("./chime-announce.mp3")
        pygame.mixer.music.play(1)
    except Exception:
        beep(time_str)
    last_beep = time_str

def save_debug_data (data):
    file = open("log.txt", "w")
    file.write(data)
    file.close()

def num_to_weekday (day):
    if day == 0:
        return "mon"
    elif day == 1:
        return "tue"
    elif day == 2:
        return "wed"
    elif day == 3:
        return "thu"
    elif day == 4:
        return "fri"
    elif day == 5:
        return "sat"
    elif day == 6:
        return "sun"

def get_time_string (hours, minutes):
    string = ""
    if hours < 10:
        string += "0"
    string += str(hours) + ":"
    if minutes < 10:
        string += "0"
    string += str(minutes)
    return string

def beep (current_time):
    global last_beep
    global scilence
    if last_beep != current_time and not scilence:
        pygame.mixer.music.load("./arrival-chime.mp3")
        pygame.mixer.music.play(1)
        last_beep = current_time

def display_opts (screen):
    global ran
    global scilence
    global announcements
    if ran:
        screen.addstr(0, 8, "R")
    if scilence:
        screen.addstr(0, 9, "S")
    if announcements:
        screen.addstr(0, 10, "A")

def display_service (screen, service, service_name, direction, destination):
    global ran
    global scilence
    global announcements
    global last_beep
    global route_announcements
    running = True
    new_station = ""
    delete_first = False
    rows, cols = screen.getmaxyx()
    chime = ""
    while running:
        announcement = "Now arriving at, "
        route_announcement = "This is, " + service_name + ", to," + direction + ", stopping at, "
        hour = time.localtime().tm_hour
        minute = time.localtime().tm_min
        time_str = get_time_string(hour, minute)
        screen.clear()
        screen.addstr(0, 0, time_str)
        display_opts(screen)
        screen.addstr(1, 0, destination)
        screen.addstr(2, 0, service_name + " (" + direction + ")")
        menu_items = 0
        for i in range (0, len(list(service.keys()))):
            if time_str == list(service.keys())[i]:
                screen.addstr(4 + i, 0, list(service.keys())[i] + "   " + service[list(service.keys())[i]], curses.A_STANDOUT)
                announcement += service[list(service.keys())[i]]
                route_announcements = None
            else:
                screen.addstr(4 + i, 0, list(service.keys())[i] + "   " + service[list(service.keys())[i]])
            if menu_items >= rows - 7:
                break
            menu_items += 1
        c = screen.getch()
        if c == ord("\n") and time_str in service:
            new_station = service[time_str]
            running = False
        if c == ord("r") or c == ord("R"):
            ran = not ran
        if c == ord("s") or c == ord("S"):
            scilence = not scilence
        if c == ord("A") or c == ord("a"):
            announcements = not announcements
        if ran and time_str in service and service[time_str] == destination:
            new_station = service[time_str]
            running = False
        first = list(service.keys())[0]
        if first == time_str:
            delete_first = True
        if first == time_str:
            if not announcements:
                create_announcement_and_play(announcement, time_str)
            else:
                beep(time_str)
            last_beep = time_str
        if delete_first and time_str != first:
            if len(service) == 1:
                new_station = service[list(service.keys())[0]]
            del service[first]
            delete_first = False
        if len(list(service.keys())) == 0:
            running = False
        if route_announcements == None and last_beep != time_str:
            length = len(list(service.keys()))
            for i in range (0, length):
                route_announcement += service[list(service.keys())[i]] + ", "
                if i == length - 2:
                    route_announcement += "and, "
            create_announcement_and_play(route_announcement, time_str)
            route_announcements = time_str
        screen.refresh()
        time.sleep(0.01)
    return new_station

def level_select (screen):
    file = open("levels.json", "r")
    levels = json.loads(file.read())
    level_list = list(levels.keys())
    file.close()
    cursor = 0
    running = True
    result = ""
    while running:
        screen.clear()
        for i in range (0, len(level_list)):
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

def new_or_load (screen):
    cursor = 0
    running = True
    menu = ["New game", "Load game"]
    result = ""
    while running:
        screen.clear()
        for i in range (0, len(menu)):
            if i == cursor:
                screen.addstr(i, 0, menu[i], curses.A_STANDOUT)
            else:
                screen.addstr(i, 0, menu[i])
        c = screen.getch()
        if c == curses.KEY_UP and cursor > 0:
            cursor -= 1
        elif c == curses.KEY_DOWN and cursor < 1:
            cursor += 1
        elif c == ord("\n"):
            result = menu[cursor]
            running = False
    return result

def create_initial_timetable (player_data):
    service_data = player_data["network-data"]
    service_list = list(service_data["services"].keys())
    service_name = service_list[random.randint(0, len(service_list) - 1)]
    player_data["service-data"]["services"] = {}
    player_data["service-data"]["services"][service_name] = {}
    player_data["service-data"]["services"][service_name]["schedule"] = service_data["services"][service_name]
    player_data["service-data"]["stations"] = {}
    service = service_data["services"][service_name]
    player_data["service-data"]["services"][service_name]["origin"] = list(service.keys())[0].split(" - ")[0]
    player_data["service-data"]["services"][service_name]["destination"] = list(service.keys())[-1].split(" - ")[1]
    schedule = list(service.keys())
    stations = []

    for i in range (0, len(schedule)):
        schedule_item = schedule[i].split(" - ")
        stations.append(schedule_item[0])
        stations.append(schedule_item[1])

    # add stations into player data
    for station in stations:
        if station not in list(player_data["service-data"]["stations"].keys()):
            player_data["service-data"]["stations"][station] = []
        if service_name not in player_data["service-data"]["stations"][station]:
            player_data["service-data"]["stations"][station].append(service_name)

    hours = time.localtime().tm_hour
    minutes = time.localtime().tm_min
    minutes += 5
    if minutes >= 60:
        minutes -= 60
        hours += 1
    if hours >= 24:
        hours -= 24
    time_offset = minutes % 5
    player_data["service-data"]["services"][service_name]["time-offset"] = time_offset
    player_data["service-data"]["services"][service_name]["departures"] = []

    player_data["service-data"]["services"][service_name]["departures"].append(get_time_string(hours, minutes))
    del player_data["network-data"]["services"][service_name]
    if len(player_data["network-data"]["services"]) == 0:
        del player_data["network-data"]["services"]
    for station in stations:
        if station in player_data["network-data"]["stations"]:
            if service_name in player_data["network-data"]["stations"][station]:
                del player_data["network-data"]["stations"][station][player_data["network-data"]["stations"][station].index(service_name)]
    for station in stations:
        if station in list(player_data["network-data"]["stations"].keys()):
            if len(player_data["network-data"]["stations"][station]) == 0:
                del player_data["network-data"]["stations"][station]
    if len(player_data["network-data"]["stations"]) == 0:
        del player_data["network-data"]["stations"]
    if len(player_data["network-data"]) == 0:
        del player_data["network-data"]
    return player_data

def load_game ():
    file = open("save.json", "r")
    data = json.loads(file.read())
    file.close()
    return data

def get_reversed_schedule (service):
    reversed_schedule = {}
    for i in range (len(list(service["schedule"].keys())) - 1, -1, -1):
        reversed_element = ""
        element = list(service["schedule"].keys())[i]
        element = element.split(" - ")
        reversed_element = element[1] + " - " + element[0]
        reversed_schedule[reversed_element] = service["schedule"][list(service["schedule"].keys())[i]]
    return reversed_schedule

def get_station_departures (service_name, service, station):
    departures = {}
    if station == service["destination"]:
        for departure in service["departures"]:
            if departure not in departures:
                departures[departure] = []
            departures[departure].append(service_name + " (" + service["origin"] + ")")
    elif station == service["origin"]:
        for departure in service["departures"]:
            if departure not in departures:
                departures[departure] = []
            departures[departure].append(service_name + " (" + service["destination"] + ")")
    else:

        # Forward direction
        for departure in service["departures"]:
            total_time = 0
            for stop in service["schedule"]:
                total_time += service["schedule"][stop]
                if stop.split(" - ")[1] == station:
                    break
            minute = int(departure.split(":")[1]) + total_time
            hours = int(departure.split(":")[0]) + (minute // 60)
            hours = hours % 24
            minute = minute % 60
            time_str = get_time_string(hours, minute)
            if time_str not in departures:
                departures[time_str] = []
            departures[time_str].append(service_name + " (" + service["destination"] + ")")
        
        # Backward direction
        reversed_schedule = get_reversed_schedule(service)
        
        for departure in service["departures"]:
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
            departures[time_str].append(service_name + " (" + service["origin"] + ")")
        
    return departures

def combine_departures (target, source):
    for key in source:
        if key not in target:
            target[key] = []
        for element in source[key]:
            target[key].append(element)
    return target

def sort_departures (current_time, departures):
    index = 0
    keys = list(departures.keys())
    sorted_keys = []
    dic = {}
    for key in keys:
        hour = int(key.split(":")[0])
        minute = int(key.split(":")[1])
        if hour not in dic:
            dic[hour] = []
        dic[hour].append(minute)
    hours =  list(dic.keys())
    hours.sort()
    for hour in hours:
        dic[hour].sort()
        for minute in dic[hour]:
            sorted_keys.append(get_time_string(hour, minute))
    keys = sorted_keys
    for departure in keys:
        current_time_hours = int(current_time.split(":")[0])
        if (current_time_hours == int(departure.split(":")[0]) and int(current_time.split(":")[1]) <= int(departure.split(":")[1])) and index == 0:
            index = keys.index(departure)
        if (int(current_time.split(":")[0]) < int(departure.split(":")[0])) and index == 0:
            index = keys.index(departure)
        if current_time == departure:
            index = keys.index(departure)
            break
    sorted = []
    for i in range (index, len(departures)):
        sorted.append(keys[i])
    for i in range (0, index):
        sorted.append(keys[i])
    sorted_departures = {}
    for element in sorted:
        sorted_departures[element] = departures[element]
    return sorted_departures

def save_game (player_data):
    file = open("save.json", "w")
    file.write(json.dumps(player_data, indent=2))
    file.close()

def generate_service_times (service_data, station_name, direction, current_time):
    sequence = {}
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

def get_travel_time (schedule, start, end):
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

def station (screen, player_data):
    global ran
    global scilence
    global announcements
    chime = ""
    running = True
    cursor = 0
    rows, cols = screen.getmaxyx()
    while running: # 39
        hour = time.localtime().tm_hour
        minute = time.localtime().tm_min
        time_str = get_time_string(hour, minute)
        # time_str = "00:00"
        
        station_departures = {}

        if player_data["target-station"] == "":
            player_data["target-station"] = list(player_data["service-data"]["stations"].keys())[random.randint(0, len(list(player_data["service-data"]["stations"].keys())) - 1)]

        for service in player_data["service-data"]["stations"][player_data["current-station"]]:
            service_data = player_data["service-data"]["services"][service]
            departures = get_station_departures(service, player_data["service-data"]["services"][service], player_data["current-station"])
            combine_departures(station_departures, departures)
        
        station_departures = sort_departures(time_str, station_departures)
        total_menu_items = 0
        # for departure in station_departures:
        #     total_menu_items += len(station_departures[departure])
        # if total_menu_items <= rows - 5:
        #     new_station_departures = {}
        #     keys = list(station_departures.keys())
        #     new_station_departures[keys[-1]] = station_departures[keys[-1]]
        #     for i in range(0, len(keys) - 1):
        #         new_station_departures[keys[i]] = station_departures[keys[i]]
        #     station_departures = new_station_departures

        screen.clear()
        screen.addstr(0, 0, time_str)
        display_opts(screen)
        screen.addstr(1, 0, player_data["current-station"] + " (" + player_data["target-station"] + ")")

        menu_items = 0
        deps = False
        station_announcement = ""
        station_announcement_base = "SERVICE, to, DEST, is now arriving. "
        for departure in station_departures:
            screen.addstr(3 + menu_items, 0, departure)
            for i in range (0, len(station_departures[departure])):
                if departure == time_str:
                    deps = True
                if departure == time_str and cursor == i:
                    screen.addstr(3 + menu_items, 7, station_departures[departure][i], curses.A_STANDOUT)
                else:
                    screen.addstr(3 + menu_items, 7, station_departures[departure][i])
                if departure == time_str:
                    station_announcement += station_announcement_base.replace("SERVICE", station_departures[departure][i].split("(")[0]).replace("DEST", station_departures[departure][i].split("(")[1].replace(")", ""))
                if menu_items >= rows - 4:
                    break
                menu_items += 1
            if menu_items >= rows - 4:
                break
        
        if deps:
            if not announcements:
                create_announcement_and_play(station_announcement, time_str)
            else:
                beep(time_str)

        c = screen.getch() # 18
        if time_str not in station_departures:
            cursor = 0
        if c == ord("q") or c == ord("Q"):
            running = False
        elif c == ord("r") or c == ord("R"):
            ran = not ran
        elif c == ord("s") or c == ord("S"):
            scilence = not scilence
        elif c == curses.KEY_DOWN and time_str in station_departures and cursor < len(station_departures[time_str]) - 1:
            cursor += 1
        elif c == curses.KEY_UP and cursor > 0:
            cursor -= 1
        elif c == curses.KEY_LEFT:
            running = False
        elif (c == ord("\n") or ran) and time_str in station_departures:
            if ran:
                save_game(player_data)
            service_name = station_departures[time_str][cursor]
            direction = service_name.split(" (")[-1].replace(")", "")
            service_name = service_name.split(" (")[0]
            service_data = player_data["service-data"]["services"][service_name]
            service_sequence = generate_service_times(service_data, player_data["current-station"], direction, time_str)
            new_station = display_service(screen, service_sequence, service_name, direction, player_data["target-station"])
            times = None
            if direction == service_data["destination"]:
                times = service_data["schedule"]
            else:
                times = get_reversed_schedule(service_data)
            player_data["points"] += get_travel_time(times, player_data["current-station"], new_station)
            player_data["current-station"] = new_station
        if player_data["current-station"] == player_data["target-station"]:
            player_data["points"] += 60
            player_data["target-station"] = ""
        screen.refresh()
        time.sleep(0.01)
    return player_data

def add_route (player_data, service_name):
    service_data = player_data["network-data"]
    service = service_data["services"][service_name]
    player_data["service-data"]["services"][service_name] = {}
    player_data["service-data"]["services"][service_name]["origin"] = list(service.keys())[0].split(" - ")[0]
    player_data["service-data"]["services"][service_name]["destination"] = list(service.keys())[-1].split(" - ")[1]
    player_data["service-data"]["services"][service_name]["schedule"] = player_data["network-data"]["services"][service_name]
    schedule = list(service.keys())
    stations = []

    for i in range (0, len(schedule)):
        schedule_item = schedule[i].split(" - ")
        stations.append(schedule_item[0])
        stations.append(schedule_item[1])

    # add stations into player data
    for station in stations:
        if station not in list(player_data["service-data"]["stations"].keys()):
            player_data["service-data"]["stations"][station] = []
        if service_name not in player_data["service-data"]["stations"][station]:
            player_data["service-data"]["stations"][station].append(service_name)

    hours = time.localtime().tm_hour
    minutes = time.localtime().tm_min
    minutes += 5
    if minutes >= 60:
        minutes -= 60
        hours += 1
    if hours >= 24:
        hours -= 24

    time_offset = minutes % 5
    player_data["service-data"]["services"][service_name]["time-offset"] = time_offset
    player_data["service-data"]["services"][service_name]["departures"] = []

    player_data["service-data"]["services"][service_name]["departures"].append(get_time_string(hours, minutes))
    del player_data["network-data"]["services"][service_name]
    if len(player_data["network-data"]["services"]) == 0:
        del player_data["network-data"]["services"]
    for station in stations:
        if station in player_data["network-data"]["stations"]:
            if service_name in player_data["network-data"]["stations"][station]:
                del player_data["network-data"]["stations"][station][player_data["network-data"]["stations"][station].index(service_name)]
    for station in stations:
        if station in list(player_data["network-data"]["stations"].keys()):
            if len(player_data["network-data"]["stations"][station]) == 0:
                del player_data["network-data"]["stations"][station]
    return player_data

def buy_new_route (screen, player_data, services):
    route_list = list(services.keys())
    cursor = 0
    running = True
    while running:
        menu = []
        if len(route_list) > 10:
            menu = route_list[:9]
        else:
            menu = route_list
        if "Back" not in menu:
            menu.append("Back")
        screen.clear()
        screen.addstr(0, 0, "Points : " + str(player_data["points"]))
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
                if player_data["points"] >= services[route_list[cursor]]:
                    player_data["points"] -= services[route_list[cursor]]
                    player_data = add_route(player_data, route_list[cursor])
                    del services[route_list[cursor]]
                    del route_list[cursor]
        screen.refresh()
        time.sleep(0.01)
    return player_data
        
        
        

def buy_new_departures (screen, player_data, departures, service):
    cursor = 0
    running = True
    total_cost = 0
    rows, cols = screen.getmaxyx()
    rows -= 3
    page = 0
    for item in player_data["service-data"]["services"][service]["schedule"]:
        total_cost += player_data["service-data"]["services"][service]["schedule"][item]
    total_cost *= 2
    while running:
        pages = int((len(departures) / (rows)) - 1) + 1
        if page > pages:
            page = pages
        menu = []
        max_index = (page * rows) + rows
        if max_index >= len(departures):
            max_index = len(departures) - 1
        menu = departures[int(page * rows) : max_index]
        screen.clear()
        screen.addstr(0, 0, "Points : " + str(player_data["points"]))
        screen.addstr(1, 0, "Cost   : " + str(total_cost))
        for i in range (0, len(menu)):
            if cursor == i:
                screen.addstr(i + 3, 0, menu[i], curses.A_STANDOUT)
            else:
                screen.addstr(i + 3, 0, menu[i])
        c = screen.getch()
        if c == curses.KEY_DOWN and cursor < len(menu) - 1:
            cursor += 1
        elif c == curses.KEY_UP and cursor > 0:
            cursor -= 1
        elif c == curses.KEY_LEFT and page == 0:
            running = False
        elif c == curses.KEY_LEFT and page > 0:
            page -= 1
        elif c == curses.KEY_RIGHT and page < pages:
            page += 1
        elif c == ord("\n"):
            if player_data["points"] >= total_cost:
                player_data["points"] -= total_cost
                player_data["service-data"]["services"][service]["departures"].append(departures[cursor + (page * rows)])
                del departures[cursor + (page * rows)]
                cursor = 0
        screen.refresh()
        time.sleep(0.01)
    return player_data

def buy_new_departure_services (screen, player_data, services):
    cursor = 0
    running = True
    while running:
        menu = list(services.keys())
        menu.append("Back")
        screen.clear()
        for i in range (0, len(menu)):
            if menu[i] != "Back":
                screen.addstr(i, 0, menu[i] + " (" + str(len(services[menu[i]])) + ")" , curses.A_STANDOUT if cursor == i else curses.A_NORMAL)
            else:
                screen.addstr(i, 0, menu[i], curses.A_STANDOUT if cursor == i else curses.A_NORMAL)
        c = screen.getch()
        if c == curses.KEY_DOWN and cursor < len(menu) - 1:
            cursor += 1
        elif c == curses.KEY_UP and cursor > 0:
            cursor -= 1
        elif c == ord("\n"):
            if cursor == len(menu) - 1:
                running = False
            else:
                player_data = buy_new_departures(screen, player_data, services[menu[cursor]], menu[cursor])
            cursor = 0
        screen.refresh()
        time.sleep(0.01)
    return player_data

def store (screen, player_data):
    new_routes = {}
    new_departures = {}
    if "network-data" in player_data and len(player_data["network-data"]) > 0 and "services" in player_data["network-data"]:
        routes = list(player_data["network-data"]["services"].keys())
        for route in routes:
            total_cost = 0
            for item in player_data["network-data"]["services"][route]:
                total_cost += player_data["network-data"]["services"][route][item]
            total_cost *= 2
            new_routes[route] = total_cost
    for route in player_data["service-data"]["services"]:
        save_debug_data(json.dumps(player_data, indent=2))
        offset = player_data["service-data"]["services"][route]["time-offset"]
        departures = player_data["service-data"]["services"][route]["departures"]
        avail = []
        for i in range (0, 24):
            for j in range (0, 12):
                time_str = get_time_string(i, offset + (j * 5))
                if time_str not in departures:
                    avail.append(time_str)
        if len(avail) > 0:
            new_departures[route] = avail
    menu = []
    if len(new_routes) > 0:
        menu.append("New routes (" + str(len(new_routes)) + ")" )
    if len(new_departures) > 0:
        menu.append("New departures (" + str(len(new_departures)) + " routes)")
    menu.append("Back")

    running = True
    cursor = 0
    while running:
        screen.clear()
        screen.addstr(0, 0, "Points : " + str(player_data["points"]))
        for i in range (0, len(menu)):
            if cursor == i:
                screen.addstr(i + 2, 0, menu[i], curses.A_STANDOUT)
            else:
                screen.addstr(i + 2, 0, menu[i])
        c = screen.getch()
        if c == curses.KEY_DOWN and cursor < len(menu) - 1:
            cursor += 1
        elif c == curses.KEY_UP and cursor > 0:
            cursor -= 1
        elif c == ord("\n"):
            if menu[cursor] == "Back":
                running = False
            if "New routes" in menu[cursor]:
                player_data = buy_new_route(screen, player_data, new_routes)
            if "New departures" in menu[cursor]:
                player_data = buy_new_departure_services(screen, player_data, new_departures)
        screen.refresh()
        time.sleep(0.01)
    return player_data

def work (screen, player_data):
    running = True
    worked = time.time()
    while running:
        screen.clear()
        screen.addstr(0, 0, get_time_string(time.localtime().tm_hour, time.localtime().tm_min))
        screen.addstr(2, 0, "Points : " + str(player_data["points"]))
        screen.addstr(4, 0, "Back", curses.A_STANDOUT)
        if (((time.time() - worked) / 3600) * 27.25) > 1:
            worked = time.time()
            player_data["points"] += 1
        screen.refresh()
        c = screen.getch()
        if c == ord("\n"):
            running = False
        time.sleep(0.01)
    return player_data

def main (screen):
    pygame.init()
    curses.curs_set(False)
    screen.nodelay(True)

    player_data = {}
    player_data["points"] = 0
    player_data["network-data"] = {}
    player_data["service-data"] = {}
    player_data["target-station"] = ""

    new_game = new_or_load(screen)
    if new_game == "New game":
        level = level_select(screen)
        file = open(level, "r")
        player_data["network-data"] = json.loads(file.read())
        file.close()
        player_data = create_initial_timetable(player_data)
        player_data["current-station"] = list(player_data["service-data"]["stations"].keys())[random.randint(0, len(list(player_data["service-data"]["stations"].keys())) - 1)]
    elif new_game == "Load game":
        player_data = load_game()

    menu = ["Station", "Work", "Store", "Save", "Quit"]
    running = True
    cursor = 0
    while running:
        screen.clear()
        for i in range (0, len(menu)):
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
        elif c == ord("\n"):
            if menu[cursor] == "Station":
                player_data = station(screen, player_data)
            elif menu[cursor] == "Work":
                player_data = work(screen, player_data)
            elif menu[cursor] == "Store":
                player_data = store(screen, player_data)
            elif menu[cursor] == "Save":
                save_game(player_data)
            elif menu[cursor] == "Quit":
                running = False
        time.sleep(0.01)

wrapper(main)
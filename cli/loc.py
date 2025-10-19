"""Localization module"""

import json

# com.au (Australian)
# co.uk (United Kingdom)
# us (United States)

data:dict[str,dict[str,str]] = {}
with open("announcements.json", "r", encoding="UTF-8") as file:
    data = json.loads(file.read())

def get_station_arrival(lang: str) -> str:
    """returns the base station announcement text for the given language"""
    text:str = ""
    if lang in data["station-arrival"]:
        text = data["station-arrival"][lang]
    return text

def get_route_progress(lang: str) -> str:
    """returns the base route announcement text for the given language"""
    text:str = ""
    if lang in data["route-progress"]:
        text = data["route-progress"][lang]
    return text

def get_train_arrival(lang: str) -> str:
    """returns the base announcement text for the given language"""
    text:str = ""
    if lang in data["train-arrival"]:
        text = data["train-arrival"][lang]
    return text

def get_and_text(lang: str) -> str:
    """returns the 'and' text for the given language"""
    text:str = ""
    if lang in data["and"]:
        text = data["and"][lang]
    return text

# if l == "af": # Afrikaans
#     pass
# if l == "ar": # Arabic
#     pass
# if l == "bg": # Bulgarian
#     pass
# if l == "bn": # Bengali
#     pass
# if l == "bs": # Bosnian
#     pass
# if l == "ca": # Catalan
#     pass
# if l == "cs" : # Czech
#     pass
# if l == "da": # Danish
#     pass
# if l == "de": # German
#     station_announcement_base = "Die SERVICE, zum, DEST, kommt jetzt. "
#     route_announcement_base = "SERVICE, zum, DIR, mit Haltestellen, "
#     announcement_base = "Jetzt angekommen bei, "
#     _and = "und, "
# if l == "el": # Greek
#     pass
# if l == "fr": # French
#     # ca (Canada)
#     # fr (France)
#     station_announcement_base = "SERVICE, vers, DEST, est en train d'arriver. "
#     route_announcement_base = "C'est, SERVICE, vers, DIR, avec ârrets à, "
#     announcement_base = "Nous arrivons à, "
#     _and = "et, "

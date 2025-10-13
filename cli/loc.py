"""Localization module"""

def get_station_announcement_base(lang: str) -> str:
    """returns the base station announcement text for the given language"""
    # com.au (Australian)
    # co.uk (United Kingdom)
    # us (United States)
    text:str = ""
    if lang == "en":
        text = "SERVICE, to, DEST, is now arriving. "
    elif lang == "it":
        text = "SERVICE, a, DEST, è in arrivo. "
    return text

def get_route_announcement_base(lang: str) -> str:
    """returns the base route announcement text for the given language"""
    text:str = ""
    if lang == "en":
        text = "This is, SERVICE, to, DIR, stopping at, "
    elif lang == "it":
        text = "Questo treno è, SERVICE, a, DIR, con fermate a, "
    return text

def get_announcement_base(lang: str) -> str:
    """returns the base announcement text for the given language"""
    text:str = ""
    if lang == "en":
        text = "Now arriving at, "
    if lang == "it":
        text = "In arrivo a, "
    return text

def get_and_text(lang: str) -> str:
    """returns the 'and' text for the given language"""
    text:str = ""
    if lang == "en":
        text = "and, "
    elif lang == "it":
        text = "e, "
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

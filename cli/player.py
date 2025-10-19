"""All methods relating to the player class"""

import json
from typing import Any



class ServiceData ():
    """The service data class"""

    def __init__ (self):
        self.service_data: Any = {}
        self.stations: Any = {}

    def get_services (self) -> Any:
        """returns the service data"""
        return self.service_data

    def set_services (self, data: Any):
        """sets the service data"""
        self.service_data = data

    def get_stations (self) -> Any:
        """returns the stations"""
        return self.stations

    def set_stations (self, data: Any):
        """sets the stations"""
        self.stations = data

    def get_json_data (self) -> Any:
        """returns the json of the service data class instance"""
        data: Any = {}
        data["services"] = self.get_services()
        data["stations"] = self.get_stations()
        return data

    def load_json (self, data: Any):
        """loads json into the service data"""
        self.set_services(data["services"])
        self.set_stations(data["stations"])



class Localization ():
    """The localization class"""

    def __init__ (self):
        self.language: str = "en"
        self.accent: str = "ca"

    def get_language (self) -> str:
        """returns the preferred language"""
        return self.language

    def get_accent (self) -> str:
        """returns the preferred accent"""
        return self.accent

    def set_language (self, lang: str):
        """sets the preferred language"""
        self.language = lang

    def set_accent (self, accent: str):
        """sets the preferred accent"""
        self.accent = accent



class Player ():
    """The player class"""

    def __init__ (self):
        self.wage: float = 17.2
        self.points: int = 0
        self.current_station: str = ""
        self.target_station: str = ""
        self.service_data: ServiceData = ServiceData()
        self.network_data: Any = {}
        self.visited_station: list[str] = []
        self.visited_all_stations: bool = False
        self.last_beep: str = ""
        self.announcements: bool = False
        self.silence: bool = False
        self.random_route: bool = False
        self.localization: Localization = Localization()
        self.home: str = ""

    def get_json_data (self) -> Any:
        """returns the json of the player class instance"""
        data : Any = {}
        data["wage"] = self.get_wage()
        data["points"] = self.get_points()
        data["current-station"] = self.get_current_station()
        data["target-station"] = self.get_target_station()
        data["service-data"] = self.get_service_data().get_json_data()
        data["language"] = self.get_localization().get_language()
        data["accent"] = self.get_localization().get_accent()
        data["network-data"] = self.get_network_data()
        data["visited-stations"] = self.get_visited_stations()
        data["visited-all-stations"] = self.get_visited_all_stations()
        data["home"] = self.get_home()
        return data

    def load_game (self):
        """loads player data from a file"""
        with open("save.json", "r", encoding="utf-8") as file:
            file_data = file.read()
            json_data = json.loads(file_data)
            self.load_json(json_data)

    def load_json (self, data : Any):
        """loads json into the player"""
        self.set_wage(data["wage"])
        self.set_points(data["points"])
        self.set_current_station(data["current-station"])
        self.set_target_station(data["target-station"])
        self.get_localization().set_language(data["language"])
        self.get_localization().set_accent(data["accent"])
        self.set_network_data(data["network-data"])
        self.set_visited_stations(data["visited-stations"])
        self.set_visited_all_stations(data["visited-all-stations"])
        service_data = ServiceData()
        service_data.load_json(data["service-data"])
        self.set_service_data(service_data)

    def save_game(self):
        """saves the player data to a file"""
        with open("save.json", "w", encoding="utf-8") as file:
            file.write(json.dumps(self.get_json_data(), indent=2))
            file.close()



    def get_announcement (self) -> bool:
        """returns whether the player has announcements enabled"""
        return self.announcements

    def get_current_station (self) -> str:
        """returns the player's current station"""
        return self.current_station

    def get_last_beep (self) -> str:
        """returns the player's last beep"""
        return self.last_beep

    def get_localization (self) -> Localization:
        """returns the player's localization instance"""
        return self.localization

    def get_network_data (self) -> Any:
        """returns the player's network data"""
        return self.network_data

    def get_points (self) -> int:
        """returns the player's points"""
        return self.points

    def get_random_route (self) -> bool:
        """returns whether the player has random route enabled"""
        return self.random_route

    def get_service_data (self) -> ServiceData:
        """returns the player's service data"""
        return self.service_data

    def get_silence (self) -> bool:
        """returns whether the player has silence enabled"""
        return self.silence

    def get_target_station (self) -> str:
        """returns the player's target station"""
        return self.target_station

    def get_visited_all_stations (self) -> bool:
        """returns whether the player has visited all stations"""
        return self.visited_all_stations

    def get_visited_stations (self) -> list[str]:
        """returns the player's visited stations"""
        return self.visited_station

    def get_wage (self) -> float:
        """returns the player's wage"""
        return self.wage

    def get_home (self) -> str:
        """returns the player's home station"""
        return self.home



    def set_announcement (self, announcements: bool):
        """sets whether the player has announcements enabled"""
        self.announcements = announcements

    def set_current_station (self, station: str):
        """sets the player's current station"""
        self.current_station = station

    def set_last_beep (self, beep: str):
        """sets the player's last beep"""
        self.last_beep = beep

    def set_network_data (self, data: Any):
        """sets the network data"""
        self.network_data = data

    def set_points (self, points: int):
        """sets the player's points"""
        self.points = points

    def set_random_route (self, random: bool):
        """sets whether the player has random route enabled"""
        self.random_route = random

    def set_service_data (self, service_data: Any):
        """sets the player's service data"""
        self.service_data = service_data

    def set_silence (self, silence: bool):
        """sets whether the player has silence enabled"""
        self.silence = silence

    def set_target_station (self, station: str):
        """sets the player's target station"""
        self.target_station = station

    def set_visited_all_stations (self, visited: bool):
        """sets whether the player has visited all stations"""
        self.visited_all_stations = visited

    def set_visited_stations (self, stations: list[str]):
        """sets the player's visited stations"""
        self.visited_station = stations

    def set_wage (self, wage: float):
        """sets the player's wage"""
        self.wage = wage

    def set_home (self, home: str):
        """sets the player's home station"""
        self.home = home

"""All methods relating to the player class"""

import json
from typing import Any

class Player ():
    """The player class"""

    def __init__ (self):
        self.wage: float = 17.2
        self.points: int = 0
        self.current_station: str = ""
        self.target_station: str = ""
        self.service_data: Any = {}
        self.language: str = "en"
        self.accent: str = "ca"
        self.network_data: Any = {}
        self.visited_station: list[str] = []
        self.visited_all_stations: bool = False

    def get_json_data (self) -> Any:
        """returns the json of the player class instance"""
        data : Any = {}
        data["wage"] = self.get_wage()
        data["points"] = self.get_points()
        data["current-station"] = self.get_current_station()
        data["target-station"] = self.get_target_station()
        data["service-data"] = self.get_service_data()
        data["language"] = self.get_language()
        data["accent"] = self.get_accent()
        data["network-data"] = self.get_network_data()
        data["visited-stations"] = self.get_visited_stations()
        data["visited-all-stations"] = self.get_visited_all_stations()
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
        self.set_service_data(data["service-data"])
        self.set_language(data["language"])
        self.set_accent(data["accent"])
        self.set_network_data(data["network-data"])
        self.set_visited_stations(data["visited-stations"])
        self.set_visited_all_stations(data["visited-all-stations"])

    def save_game(self):
        """saves the player data to a file"""
        with open("save.json", "w", encoding="utf-8") as file:
            file.write(json.dumps(self.get_json_data(), indent=2))
            file.close()



    def get_accent (self) -> str:
        """returns the player's prefered accent"""
        return self.accent

    def get_current_station (self) -> str:
        """returns the player's current station"""
        return self.current_station

    def get_language (self) -> str:
        """returns the player's prefered language"""
        return self.language

    def get_network_data (self) -> Any:
        """returns the player's network data"""
        return self.network_data

    def get_points (self) -> int:
        """returns the player's points"""
        return self.points

    def get_service_data (self) -> Any:
        """returns the player's service data"""
        return self.service_data

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



    def set_accent (self, accent: str):
        """sets the player's preferred accent"""
        self.accent = accent

    def set_current_station (self, station: str):
        """sets the player's current station"""
        self.current_station = station

    def set_language (self, lang: str):
        """sets the player's prefered language"""
        self.language = lang

    def set_network_data (self, data: Any):
        """sets the network data"""
        self.network_data = data

    def set_points (self, points: int):
        """sets the player's points"""
        self.points = points

    def set_service_data (self, service_data: Any):
        """sets the player's service data"""
        self.service_data = service_data

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

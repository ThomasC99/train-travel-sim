import unittest
import os
import pygame

from player import *
from loc import *
from utils import *
from cli import *

class Screen ():
    """screen"""

    def __init__ (self):
        self.a = False
        self.r = False
        self.s = False
        self.char_seq = ""

    def addstr (self, x:int, y:int, text:str):
        """addstr"""
        if text == "A":
            self.a = True
        if text == "S":
            self.s = True
        if text == "R":
            self.r = True

    def set_getch_seq (self, seq: str):
        """sets the char seq"""
        self.char_seq = seq

    def getch (self):
        """getch"""
        char = self.char_seq[0]
        self.char_seq = self.char_seq[1:]
        return char

    def getkey (self):
        """get key"""
        return self.getch()

    def nodelay (self, value: bool):
        """nodelay"""
        return

    def clear (self):
        """clear"""
        return

    def refresh (self):
        """refresh"""
        return



class TestPlayer (unittest.TestCase):
    """the test class"""

    def test_create_player (self):
        """test contructor"""
        player = Player ()
        self.assertIsNotNone(player.wage)
        self.assertEqual(player.points, 0)
        self.assertEqual(player.current_station, "")
        self.assertEqual(player.target_station, "")
        self.assertIsNotNone(player.service_data)
        self.assertIsNotNone(player.network_data)
        self.assertTrue(len(player.visited_station) == 0)
        self.assertFalse(player.visited_all_stations)
        self.assertEqual(player.last_beep, "")
        self.assertFalse(player.announcements)
        self.assertFalse(player.silence)
        self.assertFalse(player.random_route)
        self.assertIsNotNone(player.localization)
        self.assertEqual(player.home, "")

    def test_player_announcement (self):
        """setters and getters"""
        player = Player()
        player.set_announcement(True)
        self.assertTrue(player.get_announcement())

    def test_player_silence (self):
        """setter and getter"""
        player = Player()
        player.set_silence(True)
        self.assertTrue(player.get_silence())

    def test_player_random_route (self):
        """setter and getter"""
        player = Player()
        player.set_random_route(True)
        self.assertTrue(player.get_random_route())

    def test_create_localization (self):
        """tests constructor"""
        loc = Localization()
        self.assertIsNotNone(loc.get_language())
        self.assertEqual(loc.get_language(), "en")
        self.assertIsNotNone(loc.get_accent())
        self.assertEqual(loc.get_accent(), "ca")

    def test_localization_language (self):
        """setters and getters"""
        loc = Localization()
        lang = "fr"
        loc.set_language(lang)
        self.assertEqual(loc.get_language(), lang)

    def test_localization_accent (self):
        """setters and getters"""
        loc = Localization()
        accent = "com.us"
        loc.set_accent(accent)
        self.assertEqual(loc.get_accent(), accent)

    def test_create_service_data (self):
        """tests the creation of network data"""
        service_data = ServiceData()
        self.assertIsNotNone(service_data.service_data)
        self.assertIsNotNone(service_data.stations)

    def test_service_data_service_data (self):
        """tests service data's setters and getters"""
        data_s = {"service" : {"schedule" : ["str"]}}
        service_data = ServiceData()
        service_data.set_services(data_s)
        self.assertEqual(data_s, service_data.get_services())

    def test_service_data_stations (self):
        """test setters and getters"""
        data_s = {"station" : ["list"]}
        service_data = ServiceData()
        service_data.set_stations(data_s)
        self.assertEqual(data_s, service_data.get_stations())

    def test_service_data_json (self):
        """test loading and unloading of json"""
        service_data = ServiceData()
        initial: Any = {
            "services" : {
                "service" : {
                    "schedule" : {
                        "1 - 2" : 3
                    },
                    "origin" : "station",
                    "destination" : "station",
                    "time-offset" : 0,
                    "departures" : [
                        "00:00"
                    ]
                }
            },
            "stations" : {
                "station" : [
                    "service"
                ]
            }
        }
        service_data.load_json(initial)
        result = service_data.get_json_data()
        self.assertEqual(initial, result)



class TestCli (unittest.TestCase):
    """Tests cli.py"""

    def test_create_announcement (self):
        """test create announcement"""
        result = create_annoucement("hello, world", "en", "ca")
        self.assertIsNotNone(result)

    def test_create_annoucement_no_accent (self):
        """test create announcement"""
        result = create_annoucement("hello, world", "en", "")
        self.assertIsNotNone(result)

    def test_save_debug_data (self):
        """test debug data"""
        data = "test"
        save_debug_data(data)
        file_data = ""
        with open("log.txt", "r", encoding="UTF-8") as file:
            file_data = file.read()
        os.system("rm log.txt")
        self.assertEqual(data, file_data)

    def test_display_opts (self):
        """tests display opts"""
        player = Player()
        screen = Screen()
        display_opts(player, screen)
        self.assertFalse(screen.a)
        self.assertFalse(screen.s)
        self.assertFalse(screen.r)

    def test_display_opts_announcement (self):
        """tests display opts"""
        player = Player()
        screen = Screen()
        player.set_announcement(True)
        display_opts(player, screen)
        self.assertTrue(screen.a)

    def test_display_opts_silence (self):
        """tests display opts"""
        player = Player()
        screen = Screen()
        player.set_silence(True)
        display_opts(player, screen)
        self.assertTrue(screen.s)

    def test_display_opts_random (self):
        """tests display opts"""
        player = Player()
        screen = Screen()
        player.set_random_route(True)
        display_opts(player, screen)
        self.assertTrue(screen.r)

    def test_handle_opts_r (self):
        """test handle opts"""
        player1 = Player()
        handle_opts(player1, ord("r"))
        self.assertTrue(player1.get_random_route())
        handle_opts(player1, ord("R"))
        self.assertFalse(player1.get_random_route())

    def test_handle_opts_s (self):
        """test handle opts"""
        player = Player()
        handle_opts(player, ord("s"))
        self.assertTrue(player.get_silence())
        handle_opts(player, ord("S"))
        self.assertFalse(player.get_silence())

    def test_handle_opts_a (self):
        """test handle opts"""
        player = Player()
        handle_opts(player, ord("a"))
        self.assertTrue(player.get_announcement())
        handle_opts(player, ord("A"))
        self.assertFalse(player.get_announcement())

    def test_get_time_string_seconds (self):
        """test get time string seconds"""
        result = get_time_string_seocnds(0, 0, 10)
        self.assertEqual(result, "00:00:10")

    def test_get_time_string_seconds_zero (self):
        """test get time stirng seconds"""
        result = get_time_string_seocnds(0, 0, 0)
        self.assertEqual(result, "00:00:00")

    def test_combine_departures_null (self):
        """test 1"""
        dict_1 = {}
        dict_2 = {}
        dict_3 = combine_departures(dict_1, dict_2)
        self.assertIsNotNone(dict_3)
        self.assertEqual(dict_3, dict_1)

    def test_combine_departures_1 (self):
        """test 2"""
        dict_1 = {}
        dict_2 = {"00:00" : ["Ginza Line"]}
        dict_3 = combine_departures(dict_1, dict_2)
        self.assertIsNotNone(dict_3)
        self.assertTrue("00:00" in dict_3)
        self.assertEqual(dict_3["00:00"], dict_2["00:00"])
        self.assertTrue("Ginza Line" in dict_3["00:00"])

    def test_combine_departures_2 (self):
        """test 3"""
        dict_1 = {"00:00" : ["Ginza Line"]}
        dict_2 = {"00:00" : ["Galaxy Line"]}
        dict_3 = combine_departures(dict_1, dict_2)
        self.assertIsNotNone(dict_3)
        self.assertTrue("00:00" in dict_3)
        self.assertTrue("Ginza Line" in dict_3["00:00"])
        self.assertTrue("Galaxy Line" in dict_3["00:00"])

    def test_beep_time (self):
        """time only"""
        player = Player()
        player.set_last_beep("00:00")
        self.assertFalse(beep(player, "00:00"))

    def test_beep_silence (self):
        """silence only"""
        player = Player ()
        player.set_silence(True)
        self.assertFalse(beep(player, "00:00"))

    def test_beep_time_silence (self):
        """time and silence"""
        player = Player()
        player.set_silence(True)
        player.set_last_beep("00:00")
        self.assertFalse(beep(player, "00:00"))

    def test_beep (self):
        """normal"""
        player = Player()
        pygame.mixer.init()
        self.assertTrue(beep(player, "00:00"))

    def test_select_departure_time (self):
        """read function name"""
        screen = Screen()
        screen.set_getch_seq("00:00\n")
        result = select_departure_time(screen)
        self.assertEqual(result, "00:00")



class TestLoc (unittest.TestCase):
    """Tests the Loc class"""

    def test_get_and_text (self):
        """read the funtion name"""
        result = get_and_text("en")
        self.assertEqual(result, "and, ")

    def test_get_and_text_empty_lang (self):
        """read function name"""
        result = get_and_text("")
        self.assertEqual(result, "")

    def test_get_train_arrival (self):
        """read function name"""
        result = get_train_arrival("en")
        self.assertEqual(result, "Now arriving at, ")

    def test_get_train_arrival_empty_lang (self):
        """read function name"""
        result = get_train_arrival("")
        self.assertEqual(result, "")

    def test_get_station_arrival (self):
        """read function name"""
        result = get_station_arrival("en")
        self.assertEqual(result, "SERVICE, to, DEST, is now arriving. ")

    def test_get_station_arrival_empty_lang (self):
        """read function name"""
        result = get_station_arrival("")
        self.assertEqual(result, "")

    def test_get_route_progress (self):
        """read function name"""
        result = get_route_progress("en")
        self.assertEqual(result, "This is, SERVICE, to, DIR, stopping at, ")

    def test_get_route_progress_empty_lang (self):
        """read function name"""
        result = get_route_progress("")
        self.assertEqual(result, "")



class TestUtils (unittest.TestCase):
    """Tests the Utils class"""

    def test_load_json_file (self):
        """read function name"""
        result = load_json_file("save.json")
        self.assertIsNotNone(result)

    def test_points_to_time_str_zero (self):
        """read function name"""
        result = points_to_time_str(0)
        self.assertEqual(result, "0 minutes")

    def test_points_to_time_str_one_min (self):
        """read function name"""
        result = points_to_time_str(1)
        self.assertEqual(result, "1 minute")

    def test_points_to_time_str_minutes (self):
        """read function name"""
        result = points_to_time_str(10)
        self.assertEqual(result, "10 minutes")

    def test_points_to_time_str_hour (self):
        """read function name"""
        result = points_to_time_str(60)
        self.assertEqual(result, "1 hour, 0 minutes")

    def test_points_to_time_str_hours (self):
        """read function name"""
        result = points_to_time_str(122)
        self.assertEqual(result, "2 hours, 2 minutes")

    def test_points_to_time_str_day (self):
        """read function name"""
        result = points_to_time_str(1440)
        self.assertEqual(result, "1 day, 0 minutes")

    def test_points_to_time_str_days (self):
        """read function name"""
        result = points_to_time_str(2880)
        self.assertEqual(result, "2 days, 0 minutes")

    def test_points_to_time_str_week (self):
        """read function name"""
        result = points_to_time_str(10080)
        self.assertEqual(result, "1 week, 0 minutes")

    def test_points_to_time_str_weeks (self):
        """read function name"""
        result = points_to_time_str(20160)
        self.assertEqual(result, "2 weeks, 0 minutes")

    def test_points_to_time_str_month (self):
        """read function name"""
        result = points_to_time_str(43200)
        self.assertEqual(result, "1 month, 0 minutes")

    def test_points_to_time_str_months (self):
        """read function name"""
        result = points_to_time_str(86400)
        self.assertEqual(result, "2 months, 0 minutes")

    def test_points_to_time_str_year (self):
        """read function name"""
        result = points_to_time_str(525960)
        self.assertEqual(result, "1 year, 0 minutes")

    def test_points_to_time_str_years (self):
        """read function name"""
        result = points_to_time_str(1051920)
        self.assertEqual(result, "2 years, 0 minutes")

    def test_is_connected (self):
        """read function name"""
        self.assertTrue(is_connected())

    def test_get_time_str_zero (self):
        """test get time str"""
        result = get_time_string(0, 0)
        self.assertEqual(result, "00:00")

    def test_get_time_str_min (self):
        """test get time str min"""
        result = get_time_string(0, 10)
        self.assertEqual(result, "00:10")

    def test_get_time_str_hours (self):
        """test get time string hours"""
        result = get_time_string(10, 0)
        self.assertEqual(result, "10:00")



if __name__ == "main":
    unittest.main()

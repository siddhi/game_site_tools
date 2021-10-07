import re

import requests
from bs4 import BeautifulSoup


class GamePageParser:
    def _extract_hour(self, element):
        value = re.findall(r"^\d+", str(element.string))
        return int(value[0]) if value else 0

    def get_story_hours(self, page):
        soup = BeautifulSoup(page, features="html.parser")
        base_element = soup.find_all(class_="search_list_tidbit")
        if not base_element:
            # No search hits
            return 0
        return self._extract_hour(base_element[1])


class SiteApi:
    url = "https://howlongtobeat.com/search_results"
    params = {
        "page": 1,
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0"
    }

    def get_page(self, query):
        data = {
            "queryString": query,
            "t": "games",
            "sorthead": "name",
            "sortd": 0,
            "plat": "",
            "detail": "",
            "length_max": "",
            "length_min": "",
            "length_type": "main",
            "v": "",
            "f": "",
            "g": "",
            "randomize": 0
        }
        response = requests.post(self.url, headers=self.headers, data=data, params=self.params)
        return response.content


class HowLongToBeat:
    api = SiteApi()
    parser = GamePageParser()

    def _has_number_in_name(self, name):
        return re.findall(r"\d+", name) != []

    def _convert_to_roman(self, name):
        roman_list = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
        number = int(re.findall(r"\d+", name)[0])
        if number > 10:
            # A large number is generally part of the name, eg: 1701 A.D
            return name
        roman = roman_list[number]
        return re.sub(r"\d+", roman, name)

    def _find_game(self, game_name):
        page = self.api.get_page(game_name)
        return self.parser.get_story_hours(page)

    def find(self, game_name):
        time = self._find_game(game_name)
        if not time and self._has_number_in_name(game_name):
            # Games in a series sometimes have number stored in roman
            # eg: Kings Quest 2 -> Kings Quest II
            new_name = self._convert_to_roman(game_name)
            time = self._find_game(new_name)
        return time

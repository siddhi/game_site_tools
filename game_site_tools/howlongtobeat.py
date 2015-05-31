import re

import requests
from bs4 import BeautifulSoup


class GamePageParser:
    def _extract_hour(self, element):
        value = re.findall(r"^\d+", str(element.string))
        return int(value[0]) if value else 0

    def get_story_hours(self, page):
        soup = BeautifulSoup(page)
        base_element = soup.find_all(class_="gamelist_tidbit")
        if not base_element:
            # No search hits
            return 0
        return self._extract_hour(base_element[1])


class SiteApi:
    url = "http://howlongtobeat.com/search_main.php"
    params = {
        "t": "games",
        "page": 1,
        "sorthead": "name",
        "sortd": "Normal Order",
        "plat": "",
        "detail": 0,
    }

    def get_page(self, query):
        data = {
            "queryString": query,
        }
        response = requests.post(self.url, data=data, params=self.params)
        return response.content


class HowLongToBeat:
    api = SiteApi()
    parser = GamePageParser()

    def _has_number_in_name(self, name):
        return re.findall("\d+", name) != []

    def _convert_to_roman(self, name):
        roman_list = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
        number = int(re.findall("\d+", name)[0])
        if number > 10:
            # A large number is generally part of the name, eg: 1701 A.D
            return name
        roman = roman_list[number]
        return re.sub("\d+", roman, name)

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

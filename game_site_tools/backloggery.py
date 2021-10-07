from enum import Enum

import requests
from bs4 import BeautifulSoup

class GameStatus(Enum):
    unplayed = "(u)"
    unfinished = "(U)"
    beaten = "(B)"
    completed = "(C)"
    mastered = "(M)"
    null = "(-)"

class GamePageParser:
    def parse_page(self, page_text):
        soup = BeautifulSoup(page_text, features="html.parser")
        games = []
        for game_tag in soup.find_all("section", class_="gamebox"):
            if game_tag.h2:
                name = str(game_tag.h2.b.string).strip()
                platform = str(game_tag.div.b.string).strip()
                status = GameStatus(game_tag.h2.img["alt"])
                game = Game(name, platform, status)
                games.append(game)
        return games


class SiteApi:
    default_search_params = {
        "console": "",
        "rating": "",
        "status": "",
        "unplayed": "",
        "own": "",
        "search": "",
        "comments": "",
        "region": "",
        "region_u": 0,
        "wish": "",
        "alpha": "",
        "temp_sys": "ZZZ",
        "total": 0,
        "aid": 1,
        "ajid": 0,
    }

    def __init__(self, username):
        self.username = username

    def _get_status(self, status):
        status_number_map = {
            GameStatus.unplayed: ("", 1),
            GameStatus.unfinished: (1, 0),
            GameStatus.beaten: (2, ""),
            GameStatus.completed: (3, ""),
            GameStatus.mastered: (4, ""),
            GameStatus.null: (5, ""),
        }
        return status_number_map[status]

    def get_page(self, extra_params={}):
        url = "http://backloggery.com/ajax_moregames.php"
        params = self.default_search_params.copy()
        params.update(extra_params)
        params["user"] = self.username
        if "status" in extra_params:
            status_val, unplayed_val = self._get_status(extra_params["status"])
            params["status"] = status_val
            params["unplayed"] = unplayed_val
        response = requests.get(url, params=params)
        return response.content


class Backloggery:
    NUM_PAGE_RESULTS = 50

    parser = GamePageParser()

    def __init__(self, username):
        self.api = SiteApi(username)

    def _find_page(self, params={}):
        page = self.api.get_page(params)
        return self.parser.parse_page(page)

    def find(self, extra_params={}):
        count = 0
        params = {"ajid": count}
        params.update(extra_params)
        games = []
        has_more = True
        while has_more:
            params["ajid"] = count
            games_page = self._find_page(params)
            games += games_page
            count += len(games_page)
            has_more = len(games_page) == self.NUM_PAGE_RESULTS
        return games


class Game:
    def __init__(self, name, platform, status):
        self.name = name
        self.platform = platform
        self.status = status

    def __eq__(self, obj):
        return (self.name == obj.name and
                self.platform == obj.platform and
                self.status == obj.status)

    def __str__(self):
        return "<{}>".format(self.name)

    def __repr__(self):
        return "<{name} ({platform}): {status}>".format(
            name=self.name,
            platform=self.platform,
            status=self.status)

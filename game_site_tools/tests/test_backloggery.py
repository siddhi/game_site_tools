import unittest
from unittest import mock
from copy import deepcopy

from ..backloggery import Game, GameStatus
from ..backloggery import GamePageParser, SiteApi, Backloggery


class CopyingMock(mock.MagicMock):
    """
    This class makes a copy of the arguments send to mock, instead of storing a reference

    Used in BackloggeryTest where the params to the mock is mutable

    Ref: https://docs.python.org/3/library/unittest.mock-examples.html#coping-with-mutable-arguments
    """
    def __call__(self, *args, **kwargs):
        args = deepcopy(args)
        kwargs = deepcopy(kwargs)
        return super(CopyingMock, self).__call__(*args, **kwargs)


class GamePageParserTest(unittest.TestCase):
    def test_parse_empty_page(self):
        parser = GamePageParser()
        self.assertEqual([], parser.parse_page(""))

    def test_parse_regular_snippet(self):
        parser = GamePageParser()
        page = """
        <section class="gamebox">
            <h2>
                <a href="games.php?user=username&amp;console=3DS&amp;status=2">
                    <img alt="(B)" width="16" height="16" src="images/beaten.gif" />
                </a>
                <b>Art of Balance Touch</b>
            </h2>
            <div class="gamerow"><b>3DS</b></div>
        </section>
        """
        expected = [Game("Art of Balance Touch", "3DS", GameStatus.beaten)]
        self.assertEqual(expected, parser.parse_page(page))

    def test_parse_game_status_unplayed(self):
        parser = GamePageParser()
        page = """
        <section class="gamebox">
            <h2>
                <a href="games.php?user=username&amp;console=3DS&amp;status=1">
                    <img alt="(u)" width="16" height="16" src="images/unplayed.gif" />
                </a>
                <b>Legend of Zelda: A Link Between Worlds</b>
            </h2>
            <div class="gamerow"><b>3DS</b></div>
        </section>
        """
        expected = [Game("Legend of Zelda: A Link Between Worlds", "3DS", GameStatus.unplayed)]
        self.assertEqual(expected, parser.parse_page(page))

    def test_parse_game_status_unfinished(self):
        parser = GamePageParser()
        page = """
        <section class="gamebox">
            <h2>
                <a href="games.php?user=username&amp;console=3DS&amp;status=1">
                    <img alt="(U)" width="16" height="16" src="images/unfinished.gif" />
                </a>
                <b>Etrian Odyssey 4</b>
            </h2>
            <div class="gamerow"><b>3DS</b></div>
        </section>
        """
        expected = [Game("Etrian Odyssey 4", "3DS", GameStatus.unfinished)]
        self.assertEqual(expected, parser.parse_page(page))

    def test_parse_game_status_completed(self):
        parser = GamePageParser()
        page = """
        <section class="gamebox">
            <h2>
                <a href="games.php?user=username&amp;console=3DS&amp;status=1">
                    <img alt="(C)" width="16" height="16" src="images/completed.gif" />
                </a>
                <b>Lost Echo</b>
            </h2>
            <div class="gamerow"><b>iPad</b></div>
        </section>
        """
        expected = [Game("Lost Echo", "iPad", GameStatus.completed)]
        self.assertEqual(expected, parser.parse_page(page))

    def test_parse_game_now_playing(self):
        parser = GamePageParser()
        page = """
        <section class="gamebox nowplaying">
            <img class="npimage" src="images/SP_np.gif" />
            <h2>
                <a href="games.php?user=username&amp;console=iPad&amp;status=1">
                    <img alt="(U)" width="16" height="16" src="images/unfinished.gif" />
                </a>
                <b>Broken Sword 5</b>
            </h2>
            <div class="gamerow"><b>iPad</b></div>
        </section>
        """
        expected = [Game("Broken Sword 5", "iPad", GameStatus.unfinished)]
        self.assertEqual(expected, parser.parse_page(page))

    def test_parse_multiple_games(self):
        parser = GamePageParser()
        page = """
        <section class="system title shadow">Nintendo 3DS</section>
            <section class="gamebox">
                <h2>
                    <a href="games.php?user=username&amp;console=3DS&amp;status=2">
                        <img alt="(B)" width="16" height="16" src="images/beaten.gif" />
                    </a>
                    <b>Donkey Kong Country Returns 3D</b>
                </h2>
                <div class="gamerow"><b>3DS</b></div>
            </section>
            <section class="gamebox">
                <h2>
                    <a href="games.php?user=username&amp;console=3DS&amp;status=2">
                        <img alt="(B)" width="16" height="16" src="images/beaten.gif" />
                    </a>
                    <b>Luigi's Mansion: Dark Moon</b>
                </h2>
                <div class="gamerow"><b>3DS</b></div>
            </section>
        </section>
        <section class="gamebox systemend"></section>
        """
        expected = [Game("Donkey Kong Country Returns 3D", "3DS", GameStatus.beaten),
                    Game("Luigi's Mansion: Dark Moon", "3DS", GameStatus.beaten)]
        self.assertEqual(expected, parser.parse_page(page))


class Contains:
    """
    Unittest matcher that returns True if the sub dict is contained in the main dict
    """
    def __init__(self, sub_dict):
        self.sub_dict = sub_dict

    def __eq__(self, main_dict):
        try:
            for key in self.sub_dict:
                if main_dict[key] != self.sub_dict[key]:
                    return False
        except KeyError:
            # main dict doesn't contain the key from sub dict
            return False
        return True

    def __repr__(self):
        return "<Contains: " + str(self.sub_dict) + ">"


@mock.patch("requests.get")
class SiteApiTest(unittest.TestCase):
    def test_default_page_request(self, mock_request):
        api = SiteApi("username")
        api.get_page()
        default_params = {
            "user": "username",
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
        mock_request.assert_called_with("http://backloggery.com/ajax_moregames.php", params=default_params)

    def test_search_by_text(self, mock_request):
        api = SiteApi("username")
        api.get_page({"search": "zelda"})
        mock_request.assert_called_with(mock.ANY, params=Contains({"search": "zelda"}))

    def test_search_by_status_unplayed(self, mock_request):
        api = SiteApi("username")
        api.get_page({"status": GameStatus.unplayed})
        mock_request.assert_called_with(mock.ANY, params=Contains({"status": "", "unplayed": 1}))

    def test_search_by_status_unfinished(self, mock_request):
        api = SiteApi("username")
        api.get_page({"status": GameStatus.unfinished})
        mock_request.assert_called_with(mock.ANY, params=Contains({"status": 1, "unplayed": 0}))

    def test_search_by_status_beaten(self, mock_request):
        api = SiteApi("username")
        api.get_page({"status": GameStatus.beaten})
        mock_request.assert_called_with(mock.ANY, params=Contains({"status": 2, "unplayed": ""}))

    def test_search_by_status_completed(self, mock_request):
        api = SiteApi("username")
        api.get_page({"status": GameStatus.completed})
        mock_request.assert_called_with(mock.ANY, params=Contains({"status": 3, "unplayed": ""}))

    def test_search_by_status_mastered(self, mock_request):
        api = SiteApi("username")
        api.get_page({"status": GameStatus.mastered})
        mock_request.assert_called_with(mock.ANY, params=Contains({"status": 4, "unplayed": ""}))

    def test_search_by_status_null(self, mock_request):
        api = SiteApi("username")
        api.get_page({"status": GameStatus.null})
        mock_request.assert_called_with(mock.ANY, params=Contains({"status": 5, "unplayed": ""}))

    def test_search_multiple_fields(self, mock_request):
        api = SiteApi("username")
        api.get_page({"status": GameStatus.null, "search": "zelda"})
        mock_request.assert_called_with(mock.ANY, params=Contains({
            "search": "zelda",
            "status": 5,
            "unplayed": ""}))


class BackloggeryTest(unittest.TestCase):
    def setUp(self):
        self.b = Backloggery("username")
        self.b.api = CopyingMock()
        self.b.parser = mock.MagicMock()

    def test_find_empty_page(self):
        self.b.parser.parse_page.return_value = []
        games = self.b.find()
        self.assertEqual(0, len(games))

    def test_find_single_page(self):
        self.b.parser.parse_page.return_value = [Game("game", "WiiU", GameStatus.beaten)]
        games = self.b.find()
        self.b.api.get_page.assert_called_with({"ajid": 0})
        self.assertEqual(1, len(games))

    def test_find_multiple_pages(self):
        self.b.parser.parse_page.side_effect = [
            [Game("game", "WiiU", GameStatus.beaten)] * 50,
            [Game("game", "WiiU", GameStatus.beaten)],
        ]
        games = self.b.find()
        self.b.api.get_page.assert_has_calls([
            mock.call({"ajid": 0}),
            mock.call({"ajid": 50})
        ])
        self.assertEqual(51, len(games))

    def test_find_params_are_passed_on(self):
        self.b.parser.parse_page.return_value = [Game("game", "WiiU", GameStatus.beaten)]
        self.b.find({"search": "zelda"})
        self.b.api.get_page.assert_called_with(Contains({"search": "zelda"}))

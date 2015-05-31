import unittest
from unittest import mock

from ..howlongtobeat import GamePageParser, SiteApi, HowLongToBeat

single_hit_response = """
<li>
    <div class='gamelist_image back_black shadow_box'>
        <a title='Gabriel Knight II: The Beast Within' href='game.php?id=3782'>
            <img style='width:100%;'
              src='http://howlongtobeat.com/gameimages/256px-Gabriel_Knight_The_Beast_Within.jpg' />
        </a>
    </div>
    <div class='gamelist_details shadow_box back_darkish'>
        <h3 class='' style=''>
            <a class='text_yellow' title='Gabriel Knight II: The Beast Within'
              href='game.php?id=3782'>Gabriel Knight II: The Beast Within</a>
        </h3>
        <div class='back_darkish' style='min-height: 40px;padding: 4px 5px;'>
            <div style='display:inline-block;'>
                <div class='gamelist_tidbit'>Main Story</div>
                <div class='gamelist_tidbit time_50'>14 Hours</div>
            </div>
            <div style='display:inline-block;'>
                <div class='gamelist_tidbit'>Main + Extra</div>
                <div class='gamelist_tidbit time_40'>15 Hours</div>
            </div>
            <div style='display:inline-block;'>
                <div class='gamelist_tidbit'>Completionist</div>
                <div class='gamelist_tidbit time_00'>N/A</div>
            </div>
            <div style='display:inline-block;'>
                <div class='gamelist_tidbit'>Combined</div>
                <div class='gamelist_tidbit time_50'>14 Hours</div>
            </div>
        </div>
        <div class='back_dark'>
            <strong class='gamelist_tidbit text_white'>Submit:</strong>
            <a class='gamelist_tidbit text_white' title='Submit Your Time'
              href='submit_add.php?gid=3782'>+ Your Time</a>
        </div>
    </div>
</li>
"""

fractional_hours_response = """
<li>
    <div class='gamelist_image back_black shadow_box'>
        <a title='Space Quest III: The Pirates of Pestulon' href='game.php?id=8865'>
            <img style='width:100%;'
              src='http://howlongtobeat.com/gameimages/256px-Spacequest3.jpg' />
        </a>
    </div>
    <div class='gamelist_details shadow_box back_darkish'>
        <h3 class='' style=''>
            <a class='text_yellow' title='Space Quest III: The Pirates of Pestulon'
              href='game.php?id=8865'>Space Quest III: The Pirates of Pestulon</a>
        </h3>
        <div class='back_darkish' style='min-height: 40px;padding: 4px 5px;'>
            <div style='display:inline-block;'>
                <div class='gamelist_tidbit'>Main Story</div>
                <div class='gamelist_tidbit time_40'>2&#189; Hours</div>
            </div>
            <div style='display:inline-block;'>
                <div class='gamelist_tidbit'>Main + Extra</div>
                <div class='gamelist_tidbit time_00'>N/A</div>
            </div>
            <div style='display:inline-block;'>
                <div class='gamelist_tidbit'>Completionist</div>
                <div class='gamelist_tidbit time_40'>5 Hours</div>
            </div>
            <div style='display:inline-block;'>
                <div class='gamelist_tidbit'>Combined</div>
                <div class='gamelist_tidbit time_40'>3&#189; Hours</div>
            </div>
        </div>
        <div class='back_dark'>
            <strong class='gamelist_tidbit text_white'>Submit:</strong>
            <a class='gamelist_tidbit text_white' title='Submit Your Time'
              href='submit_add.php?gid=8865'>+ Your Time</a>
        </div>
    </div>
</li>
"""

no_hours_available_response = """
<li>
    <div class='gamelist_image back_black shadow_box'>
        <a title='A Mind Forever Voyaging' href='game.php?id=132'>
            <img style='width:100%;'
              src='http://howlongtobeat.com/gameimages/A_Mind_Forever_Voyaging_Coverart.png' />
        </a>
    </div>
    <div class='gamelist_details shadow_box back_darkish'>
        <h3 class='' style=''>
            <a class='text_yellow' title='A Mind Forever Voyaging'
              href='game.php?id=132'>A Mind Forever Voyaging</a>
        </h3>
        <div class='back_darkish' style='min-height: 40px;padding: 4px 5px;'>
            <div style='display:inline-block;'>
                <div class='gamelist_tidbit'>Main Story</div>
                <div class='gamelist_tidbit time_00'>N/A</div>
            </div>
            <div style='display:inline-block;'>
                <div class='gamelist_tidbit'>Main + Extra</div>
                <div class='gamelist_tidbit time_00'>N/A</div>
            </div>
            <div style='display:inline-block;'>
                <div class='gamelist_tidbit'>Completionist</div>
                <div class='gamelist_tidbit time_00'>N/A</div>
            </div>
            <div style='display:inline-block;'>
                <div class='gamelist_tidbit'>Combined</div>
                <div class='gamelist_tidbit time_00'>N/A</div>
            </div>
        </div>
        <div class='back_dark'>
            <strong class='gamelist_tidbit text_white'>Submit:</strong>
            <a class='gamelist_tidbit text_white' title='Submit Your Time'
              href='submit_add.php?gid=132'>+ Your Time</a>
        </div>
    </div>
</li>
"""

no_hits_response = """
<div id='suggestionsList_main' class='gamelist_list'>
    <div class='search_loading back_white shadow_box'>
        No results in <u>games</u>, sorry mate.
    </div>
</div>
<div class='clear'></div>
"""

multiple_hits_response = """
<div id='suggestionsList_main' class='gamelist_list'>
    <div class='search_loading shadow_box back_blue'>We Found 8 Games for "baldurs gate"</div>
    <li>
        <div class='gamelist_image back_black shadow_box'>
            <a title='Baldur's Gate' href='game.php?id=808'>
                <img style='width:100%;'
                  src='http://howlongtobeat.com/gameimages/Baldurs_Gate_box.PNG' />
            </a>
        </div>
        <div class='gamelist_details shadow_box back_white'>
            <h3 class='' style=''>
                <a class='text_blue' title='Baldur's Gate' href='game.php?id=808'>Baldur's Gate</a>
            </h3>
            <div class='back_white' style='min-height: 40px;padding: 4px 5px;'>
                <div style='display:inline-block;'>
                    <div class='gamelist_tidbit'>Main Story</div>
                    <div class='gamelist_tidbit time_60'>45 Hours</div>
                </div>
                <div style='display:inline-block;'>
                    <div class='gamelist_tidbit'>Main + Extra</div>
                    <div class='gamelist_tidbit time_100'>56&#189; Hours</div>
                </div>
                <div style='display:inline-block;'>
                    <div class='gamelist_tidbit'>Completionist</div>
                    <div class='gamelist_tidbit time_60'>107 Hours</div>
                </div>
                <div style='display:inline-block;'>
                    <div class='gamelist_tidbit'>Combined</div>
                    <div class='gamelist_tidbit time_100'>62 Hours</div>
                </div>
            </div>
            <div class='back_dark'>
                <strong class='gamelist_tidbit text_white'>Submit:</strong>
                <a class='gamelist_tidbit text_white' title='Submit Your Time'
                  href='submit_add.php?gid=808'>+ Your Time</a>
            </div>
        </div>
    </li>
    <li>
        <div class='gamelist_image back_black shadow_box'>
            <a title='Baldur's Gate II: Enhanced Edition' href='game.php?id=809'>
                <img style='width:100%;'
                  src='http://howlongtobeat.com/gameimages/baldursgameenhancededition2_292x136.jpg' />
            </a>
        </div>
        <div class='gamelist_details shadow_box back_white'>
            <h3 class='' style=''>
                <a class='text_blue' title='Baldur's Gate II: Enhanced Edition'
                  href='game.php?id=809'>Baldur's Gate II: Enhanced Edition</a>
            </h3>
            <div class='back_white' style='min-height: 40px;padding: 4px 5px;'>
                <div style='display:inline-block;'>
                    <div class='gamelist_tidbit'>Main Story</div>
                    <div class='gamelist_tidbit time_40'>38&#189; Hours</div>
                </div>
                <div style='display:inline-block;'>
                    <div class='gamelist_tidbit'>Main + Extra</div>
                    <div class='gamelist_tidbit time_40'>63 Hours</div>
                </div>
                <div style='display:inline-block;'>
                    <div class='gamelist_tidbit'>Completionist</div>
                    <div class='gamelist_tidbit time_40'>111&#189; Hours</div>
                </div>
                <div style='display:inline-block;'>
                    <div class='gamelist_tidbit'>Combined</div>
                    <div class='gamelist_tidbit time_50'>58&#189; Hours</div>
                </div>
            </div>
            <div class='back_dark'>
                <strong class='gamelist_tidbit text_white'>Submit:</strong>
                <a class='gamelist_tidbit text_white' title='Submit Your Time'
                  href='submit_add.php?gid=809'>+ Your Time</a>
            </div>
        </div>
    </li>
</div>
<div class='clear'></div>
"""


class GamePageParserTest(unittest.TestCase):
    def test_parse_regular_result(self):
        parser = GamePageParser()
        self.assertEqual(14, parser.get_story_hours(single_hit_response))

    def test_ignore_fraction_hours(self):
        """
        We should ignore the fractional amount of hours.

        Sometimes the hour contains fractions, eg: 5 1/2 hours.
        """

        parser = GamePageParser()
        self.assertEqual(2, parser.get_story_hours(fractional_hours_response))

    def test_should_return_zero_if_no_hours_available(self):
        parser = GamePageParser()
        self.assertEqual(0, parser.get_story_hours(no_hours_available_response))

    def test_should_return_zero_if_no_hits(self):
        parser = GamePageParser()
        self.assertEqual(0, parser.get_story_hours(no_hits_response))

    def test_should_return_first_of_multiple_hits(self):
        parser = GamePageParser()
        self.assertEqual(45, parser.get_story_hours(multiple_hits_response))


@mock.patch("requests.post")
class SiteApiTest(unittest.TestCase):
    def test_page_request(self, mock_request):
        api = SiteApi()
        api.get_page("Zork: Grand Inquisitor")
        expected_data = {"queryString": "Zork: Grand Inquisitor"}
        expected_params = {
            "t": "games",
            "page": 1,
            "sorthead": "name",
            "sortd": "Normal Order",
            "plat": "",
            "detail": 0
        }
        mock_request.assert_called_with("http://howlongtobeat.com/search_main.php",
                                        data=expected_data,
                                        params=expected_params)


class HowLongToBeatTest(unittest.TestCase):
    def setUp(self):
        self.h = HowLongToBeat()
        self.h.api = mock.MagicMock()

    def test_find_page(self):
        self.h.api.get_page.return_value = single_hit_response
        self.assertEqual(14, self.h.find("Gabriel Knight II"))

    def test_should_try_roman_if_no_value(self):
        """
        If we get no value when trying a name like Gabriel Knight 2,
        then try again with Gabriel Knight II
        """
        self.h.api.get_page.side_effect = \
            lambda game: single_hit_response if game == "Gabriel Knight II" else no_hits_response
        self.assertEqual(14, self.h.find("Gabriel Knight 2"))
        self.assertEqual(2, self.h.api.get_page.call_count)
        self.h.api.get_page.assert_has_calls([mock.call("Gabriel Knight 2"),
                                              mock.call("Gabriel Knight II")])

    def test_roman_should_return_same_name_if_it_has_no_number(self):
        """
        Some games do not exist in the database, eg: Age of Enigma. Such games
        will fail, but will not have a number in the name. In such cases, we
        should not attempt again with a roman conversion
        """
        self.h.api.get_page.return_value = no_hits_response
        self.assertEqual(0, self.h.find("Age of Enigma"))

# the_odds_api_client.py

import requests


class TheOddsAPIClient:
    """
    Class containing methods for interacting with The Odds API.

    Methods:
        get_events
        get_player_props
        _fetch_data
    """

    SPORT = "basketball_nba"
    PLAYER_PROP_MARKETS = "player_points,player_rebounds,player_assists,player_threes,player_points_rebounds_assists,player_points_rebounds,player_points_assists,player_rebounds_assists,player_field_goals,player_frees_made,player_frees_attempts,player_points_alternate,player_rebounds_alternate,player_assists_alternate,player_threes_alternate,player_points_assists_alternate,player_points_rebounds_alternate,player_rebounds_assists_alternate,player_points_rebounds_assists_alternate"
    # PLAYER_PROP_MARKETS = "player_points_alternate, "
    # PLAYER_PROP_MARKETS = "player_points_alternate,player_rebounds_alternate,player_assists_alternate,player_threes_alternate,player_points_assists_alternate,player_points_rebounds_alternate,player_rebounds_assists_alternate,player_points_rebounds_assists_alternate"
    ODDS_FORMAT = "american"
    DATE_FORMAT = "iso"

    @classmethod
    def get_events(cls, api_key: str):
        """
        Gets event and odds data for upcoming NBA games.

        Args:
            api_key (str) - API key

        Returns:
            (dict or None) - json data object, or None if error
        """
        odds = cls._fetch_data(
            f"https://api.the-odds-api.com/v4/sports/{cls.SPORT}/odds",
            {
                "api_key": api_key,
                "regions": "us",
                "markets": "h2h,spreads,totals",
                "oddsFormat": cls.ODDS_FORMAT,
                "dateFormat": cls.DATE_FORMAT,
            },
        )

        return odds

    @classmethod
    def get_player_props(cls, api_key: str, region: str, event_ids: list[str]):
        """
        Gets player prop data for each event id provided.

        Args:
            api_key (str) - ...
            region (str) - ...

        """
        odds_list = []

        for event_id in event_ids:
            odds = cls._fetch_data(
                f"https://api.the-odds-api.com/v4/sports/{cls.SPORT}/events/{event_id}/odds",
                {
                    "api_key": api_key,
                    "regions": region,
                    "markets": cls.PLAYER_PROP_MARKETS,
                    "oddsFormat": cls.ODDS_FORMAT,
                    "dateFormat": cls.DATE_FORMAT,
                },
            )
            odds_list.append(odds)

        return odds_list

    @staticmethod
    def _fetch_data(url: str, params: dict):
        """
        Helper method to fetch json data from The Odds API.

        Args:
            url (str) - request url
            params (dict) - request params for filtering and stuff

        Returns:
            (dict or None) json object containing whatever data, or None if bad request
        """
        res = requests.get(url, params)

        if res.status_code != 200:
            print(
                f"Failed to get odds: status_code {res.status_code}, response body {res.text}"
            )
            return

        print("Remaining requests", res.headers["x-requests-remaining"])
        print("Used requests", res.headers["x-requests-used"])

        return res.json()

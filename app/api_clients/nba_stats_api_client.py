# nba_stats_api_client.py

import requests


class NBAStatsAPIClient:
    """
    Class containing methods for fetching data from NBA API.

    Methods:
        get_players
        get_team_box_scores
        get_player_box_scores
        get_player_tracking_box_scores
        _fetch_data
    """

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Referer": "https://www.nba.com/",
        "Origin": "https://www.nba.com",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }

    @classmethod
    def get_players(cls, season="2024-25") -> dict | None:
        """
        Fetches all Player Index data.

        Args:
            season (str) - the season year; doesn't really matter here

        Returns:
            json object containing Player Index data, or None in case of error.
        """
        params = {
            "LeagueID": "00",
            "Season": season,
            "Historical": 1,
            "TeamID": 0,
        }

        url = "https://stats.nba.com/stats/playerindex"
        return cls._fetch_data(url, params, "Error fetching Players Index.")

    @classmethod
    def get_team_box_scores(
            cls,
            measure_type: str,
            season: str,
            season_type: str,
            period: int,
            playoff_round=None,
            date_from=None,
            date_to=None,
    ) -> dict | None:
        """
        Fetches Team Box Score data.

        Args:
            measure_type (str) - Base (Traditional), Advanced, Misc, Scoring
            season (str) - season year e.g. 2024-25
            season_type (str) - Pre Season, Regular Season, IST, Play In, or Playoffs
            period (int) - 0 (full game), 1 (1st Quarter), ... , 8 (Overtime 4), ...
            playoff_round (int or None) - None, 1 (Conf. quarter), 2 (Conf. semis), 3 (Conf. finals), 4 (Finals)
            date_from (str or None) - e.g. 10/03/2024
            date_to (str or None) - "

        Returns:
            json object containing Team Box Score data, or None in case of error.
        """
        params = {
            "MeasureType": measure_type,
            "Season": season,
            "SeasonType": season_type,
            "Period": period,
            "PORound": playoff_round,
            "DateFrom": date_from,
            "DateTo": date_to,
            "LastNGames": 0,
            "LeagueID": "00",
            "Month": 0,
            "OpponentTeamID": 0,
            "PerMode": "Totals",
        }

        url = "https://stats.nba.com/stats/teamgamelogs"
        return cls._fetch_data(url, params, "Error fetching Team Box Scores.")

    @classmethod
    def get_player_box_scores(
            cls,
            measure_type: str,
            season: str,
            season_type: str,
            period: int,
            playoff_round=None,
            date_from=None,
            date_to=None,
    ) -> dict | None:
        """
        Fetches Player Box Score data.

        Args:
            measure_type (str) - Base (Traditional), Advanced, Misc, Scoring
            season (str) - season year e.g. 2024-25
            season_type (str) - Pre Season, Regular Season, IST, PlayIn, or Playoffs
            period (int) - 0 (full game), 1 (1st Quarter), ... , 8 (Overtime 4), ...
            playoff_round (int or None) - None, 1 (Conf. quarter), 2 (Conf. semis), 3 (Conf. finals), 4 (Finals)
            date_from (str or None) - e.g. 10/03/2024
            date_to (str or None) - "

        Returns:
            json object containing Player Box Score data, or None in case of error.
        """
        params = {
            "MeasureType": measure_type,
            "Season": season,
            "SeasonType": season_type,
            "Period": period,
            "PORound": playoff_round,
            "DateFrom": date_from,
            "DateTo": date_to,
            "LastNGames": 0,
            "LeagueID": "00",
            "Month": 0,
            "OpponentTeamID": 0,
            "PerMode": "Totals",
        }
        url = "https://stats.nba.com/stats/playergamelogs"
        data = cls._fetch_data(url, params, "Error fetching Players Box Scores.")

        print(
            f"fetched {url} {params['Season']} {params['SeasonType']} {params['Period']} {params['MeasureType']}"
        )
        return data

    @classmethod
    def get_player_tracking_box_scores(
            cls,
            measure_type: str,
            date_from: str,
            date_to: str,
            playoff_round=0,
            season: str = None,
            season_type: str = None,

    ) -> dict | None:
        """
        Fetches Player Box Score data.

        Args: 
            measure_type (str) - Passing or Rebounding
            date_from (str) - e.g. 10/03/2024
            date_to (str) - "
            playoff_round (int) - None, 1 (Conf. quarter), 2 (Conf. semis), 3 (Conf. finals), 4 (Finals)
            season (str or None) - season year e.g. 2024-25
            season_type (str or None) - Pre Season, Regular Season, IST, Play In, or Playoffs

        Returns:
            json object containing Player Box Score data, or None in case of error.
        """
        params = {
            "PtMeasureType": measure_type,
            "Season": season,
            "SeasonType": season_type,
            "PORound": playoff_round,
            "DateFrom": date_from,
            "DateTo": date_to,
            "LastNGames": 0,
            "LeagueID": "00",
            "Month": 0,
            "OpponentTeamID": 0,
            "PerMode": "Totals",
            "PlayerOrTeam": "Player",
            "TeamID": 0
        }

        url = f"https://stats.nba.com/stats/leaguedashptstats"
        data = cls._fetch_data(url, params, "Error fetching Players Tracking Box Scores.")

        return data

    @classmethod
    def _fetch_data(cls, url: str, params: dict, error_message: str) -> dict | None:
        """
        Helper function to send requests.

        Args:
            url (str) - request url
            params (dict) - request params for filtering and stuff
            error_message (str) - error message for logging purposes

        Returns:
            (dict or None) json object containing whatever data, or None if bad request
        """
        try:
            response = requests.get(url, params=params, headers=cls.HEADERS)
            response.raise_for_status()  # Raise an error for bad status codes
            return response.json()
        except requests.RequestException as e:
            print(f"{error_message}: {e}")
            return None

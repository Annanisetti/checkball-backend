# prizepicks_api_client.py

import requests
import pandas as pd


class PrizePicksAPIClient:
    @classmethod
    def get_first_half_props(cls) -> pd.DataFrame:
        return cls._call_endpoint(
            "https://partner-api.prizepicks.com/projections?league_id=84",
            include_new_player_attributes=True,
        )

    @staticmethod
    def _call_endpoint(url, max_level=3, include_new_player_attributes=False):
        """
        source: https://github.com/mada949/PrizePicks-API
        takes:
            - url (str): the API endpoint to call
            - max_level (int): level of json normalizing to apply
            - include_player_attributes (bool): whether to include player object attributes in the returned dataframe
        returns:
            - df (pd.DataFrame): a dataframe of the call response content
        """
        resp = requests.get(url).json()
        data = pd.json_normalize(resp["data"], max_level=max_level)
        try:
            included = pd.json_normalize(resp["included"], max_level=max_level)
        except KeyError:
            return pd.DataFrame()
        if include_new_player_attributes:
            inc_cop = included[included["type"] == "new_player"].copy().dropna(axis=1)
            data = pd.merge(
                data,
                inc_cop,
                how="left",
                left_on=[
                    "relationships.new_player.data.id",
                    "relationships.new_player.data.type",
                ],
                right_on=["id", "type"],
                suffixes=("", "_new_player"),
            )
        return data

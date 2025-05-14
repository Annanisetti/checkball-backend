# the_odds_api_service.py

import uuid
from datetime import datetime
import pytz

from app.api_clients.the_odds_api_client import TheOddsAPIClient
from app.markets import MARKET_STATS_MAPPING
from app.models.odds_api_models import *
from app.services.nba_stats_api_service import NBAStatsAPIService


class TheOddsAPIService:
    """
    Class containing methods to load and process data from The Odds API.

    Methods:
        load_bookmakers
        load_events_and_odds
        load_player_props_and_odds
        _process_events
        _process_player_props
        get_event_by_team_id
        _format_event_time
    """

    @staticmethod
    def load_bookmakers() -> None:
        """Method to load all Bookmakers into db.

        Returns:
            None
        """
        Bookmaker.__table__.drop(db.engine, checkfirst=True)
        Bookmaker.__table__.create(db.engine)

        bookmakers_data = [
            {
                "key": "betonlineag",
                "region": "us",
                "title": "BetOnline.ag",
                "link": "https://www.betonline.ag",
                "image_path": "../static/images/bookmakers/betonlineag.png",
            },
            {
                "key": "betmgm",
                "region": "us",
                "title": "BetMGM",
                "link": "https://www.betmgm.com",
                "image_path": "../static/images/bookmakers/betmgm.png",
            },
            {
                "key": "betrivers",
                "region": "us",
                "title": "BetRivers",
                "link": "https://www.betrivers.com",
                "image_path": "../static/images/bookmakers/betrivers.png",
            },
            {
                "key": "betus",
                "region": "us",
                "title": "BetUS",
                "link": "https://www.betus.com",
                "image_path": "../static/images/bookmakers/betus.png",
            },
            {
                "key": "bovada",
                "region": "us",
                "title": "Bovada",
                "link": "https://www.bovada.lv",
                "image_path": "../static/images/bookmakers/bovada.png",
            },
            {
                "key": "williamhill_us",
                "region": "us",
                "title": "Caesars",
                "link": "https://www.caesars.com",
                "image_path": "../static/images/bookmakers/caesars.png",
            },
            {
                "key": "draftkings",
                "region": "us",
                "title": "DraftKings",
                "link": "https://www.draftkings.com",
                "image_path": "../static/images/bookmakers/draftkings.png",
            },
            {
                "key": "fanatics",
                "region": "us",
                "title": "Fanatics",
                "link": "https://www.fanatics.com",
                "image_path": "../static/images/bookmakers/fanatics.png",
            },
            {
                "key": "fanduel",
                "region": "us",
                "title": "FanDuel",
                "link": "https://www.fanduel.com",
                "image_path": "../static/images/bookmakers/fanduel.png",
            },
            {
                "key": "lowvig",
                "region": "us",
                "title": "LowVig.ag",
                "link": "https://www.lowvig.ag",
                "image_path": "../static/images/bookmakers/lowvig.png",
            },
            {
                "key": "mybookieag",
                "region": "us",
                "title": "MyBookie.ag",
                "link": "https://www.mybookie.ag",
                "image_path": "../static/images/bookmakers/mybookie.png",
            },
            {
                "key": "ballybet",
                "region": "us2",
                "title": "Bally Bet",
                "link": "https://www.ballybet.com",
                "image_path": "../static/images/bookmakers/ballybet.png",
            },
            {
                "key": "betanysports",
                "region": "us2",
                "title": "BetAnySports",
                "link": "https://www.betanysports.eu",
                "image_path": "../static/images/bookmakers/betanysports.png",
            },
            {
                "key": "betparx",
                "region": "us2",
                "title": "betPARX",
                "link": "https://www.betparx.com",
                "image_path": "../static/images/bookmakers/betparx.png",
            },
            {
                "key": "espnbet",
                "region": "us2",
                "title": "ESPN BET",
                "link": "https://www.espnbet.com",
                "image_path": "../static/images/bookmakers/espnbet.png",
            },
            {
                "key": "fliff",
                "region": "us2",
                "title": "Fliff",
                "link": "https://www.fliff.com",
                "image_path": "../static/images/bookmakers/fliff.png",
            },
            {
                "key": "hardrockbet",
                "region": "us2",
                "title": "Hard Rock Bet",
                "link": "https://www.hardrockbet.com",
                "image_path": "../static/images/bookmakers/hardrockbet.png",
            },
            {
                "key": "windcreek",
                "region": "us2",
                "title": "Wind Creek",
                "link": "https://www.windcreek.com",
                "image_path": "../static/images/bookmakers/windcreek.png",
            },
            {
                "key": "prizepicks",
                "region": "us_dfs",
                "title": "PrizePicks",
                "link": "https://www.prizepicks.com/",
                "image_path": "../static/images/bookmakers/prizepicks.png",
            },
            {
                "key": "underdog",
                "region": "us_dfs",
                "title": "Underdog",
                "link": "https://underdogfantasy.com/",
                "image_path": "../static/images/bookmakers/underdog.png",
            },
        ]

        for bookmaker_data in bookmakers_data:
            bookmaker = Bookmaker(
                key=bookmaker_data["key"],
                region=bookmaker_data["region"],
                title=bookmaker_data["title"],
                link=bookmaker_data["link"],
                image_path=bookmaker_data["image_path"],
            )
            db.session.add(bookmaker)

        db.session.commit()

    @classmethod
    def load_events_and_odds(cls, api_key: str):
        """Method to fetch events odds from The Odds API and load into db.

        Args:
            api_key (str) - The Odds API key for auth

        Returns:
            None
        """
        TheOddsAPIEvent.__table__.drop(db.engine, checkfirst=True)
        TheOddsAPIEvent.__table__.create(db.engine)

        MoneylineOdds.__table__.drop(db.engine, checkfirst=True)
        MoneylineOdds.__table__.create(db.engine)

        PointsSpreadOdds.__table__.drop(db.engine, checkfirst=True)
        PointsSpreadOdds.__table__.create(db.engine)

        TotalPointsOdds.__table__.drop(db.engine, checkfirst=True)
        TotalPointsOdds.__table__.create(db.engine)

        # Fetch and process events data

        events_json = TheOddsAPIClient.get_events(api_key)
        processed_events_and_odds = cls._process_events(events_json)

        processed_events = processed_events_and_odds["events"]
        processed_moneyline_odds = processed_events_and_odds["moneyline_odds"]
        processed_spread_odds = processed_events_and_odds["spread_odds"]
        processed_totals_odds = processed_events_and_odds["totals_odds"]

        # Inserting Events

        for event in processed_events:
            db.session.add(
                TheOddsAPIEvent(
                    id=event["id"],
                    start_time=event["start_time"],
                    formatted_start_time=event["formatted_start_time"],
                    home_team_id=event["home_team_id"],
                    away_team_id=event["away_team_id"],
                )
            )

        # Inserting MoneylineOdds

        for moneyline_odds in processed_moneyline_odds:
            db.session.add(
                MoneylineOdds(
                    event_id=moneyline_odds["event_id"],
                    bookmaker_key=moneyline_odds["bookmaker_key"],
                    home_team_odds=moneyline_odds["home_team_odds"],
                    away_team_odds=moneyline_odds["away_team_odds"],
                )
            )

        # Inserting PointsSpreadOdds

        for spread_odds in processed_spread_odds:
            db.session.add(
                PointsSpreadOdds(
                    event_id=spread_odds["event_id"],
                    bookmaker_key=spread_odds["bookmaker_key"],
                    home_team_line=spread_odds["home_team_line"],
                    home_team_odds=spread_odds["home_team_odds"],
                    away_team_line=spread_odds["away_team_line"],
                    away_team_odds=spread_odds["away_team_odds"],
                )
            )

        # Inserting TotalPointsOdds

        for total_points_odds in processed_totals_odds:
            db.session.add(
                TotalPointsOdds(
                    event_id=total_points_odds["event_id"],
                    bookmaker_key=total_points_odds["bookmaker_key"],
                    line=total_points_odds["line"],
                    over_odds=total_points_odds["over_odds"],
                    under_odds=total_points_odds["under_odds"],
                )
            )

        # Commit the changes to the database
        db.session.commit()

    @classmethod
    def load_player_props_and_odds(cls, api_key: str) -> None:
        """
        Method to load processed player props and odds into db.

        Args:
            api_key (str) - The Odds API key for auth

        Returns:
            None
        """
        PlayerProp.__table__.drop(db.engine, checkfirst=True)
        PlayerProp.__table__.create(db.engine)

        PlayerPropOdds.__table__.drop(db.engine, checkfirst=True)
        PlayerPropOdds.__table__.create(db.engine)

        event_ids = [event.id for event in TheOddsAPIEvent.query.all()]

        # us_player_props_json = TheOddsAPIClient.get_player_props(
        #     api_key, "us", event_ids
        # )
        # us2_player_props_json = TheOddsAPIClient.get_player_props(
        #     api_key, "us2", event_ids
        # )
        us_dfs_player_props_json = TheOddsAPIClient.get_player_props(
            api_key, "us_dfs", event_ids
        )

        processed_player_props_and_odds = cls._process_player_props(
            # [us_player_props_json, us2_player_props_json, us_dfs_player_props_json]
            [us_dfs_player_props_json]
        )

        processed_player_props = processed_player_props_and_odds["player_props"]
        processed_player_props_odds = processed_player_props_and_odds[
            "player_props_odds"
        ]

        db.session.bulk_insert_mappings(PlayerProp, processed_player_props)
        db.session.bulk_insert_mappings(PlayerPropOdds, processed_player_props_odds)

        # Commit the session to save everything to the database
        db.session.commit()

    @classmethod
    def _process_events(cls, events_json: list[dict]) -> dict:
        """
        Helper method to process events and odds data.

        Args:
            events_json (list[dict]) - list of json objects, where each contains data for an event

        Returns:
            (dict) - dict containing lists of events, moneyline odds, spread odds, and totals odds
        """
        events_list = []

        moneyline_odds_list = []
        spread_odds_list = []
        totals_odds_list = []

        for event_json in events_json:
            event_id = event_json["id"]

            home_team = event_json["home_team"]
            away_team = event_json["away_team"]

            start_time = datetime.strptime(
                event_json["commence_time"], "%Y-%m-%dT%H:%M:%SZ"
            )

            event = {
                "id": event_id,
                "start_time": start_time,
                "formatted_start_time": cls._format_event_time(start_time),
                "home_team_id": NBAStatsAPIService.get_team_id(team_name=home_team),
                "away_team_id": NBAStatsAPIService.get_team_id(team_name=away_team),
            }

            events_list.append(event)

            for bookmaker in event_json["bookmakers"]:
                bookmaker_key = bookmaker["key"]

                for market in bookmaker["markets"]:
                    market_key = market["key"]

                    if market_key == "h2h":
                        money_line_odds = {
                            "event_id": event_id,
                            "bookmaker_key": bookmaker_key,
                        }

                        for outcome in market["outcomes"]:
                            price = outcome["price"]

                            if outcome["name"] == home_team:
                                money_line_odds["home_team_odds"] = price
                                continue

                            if outcome["name"] == away_team:
                                money_line_odds["away_team_odds"] = price
                                continue

                        moneyline_odds_list.append(money_line_odds)
                        continue

                    if market_key == "spreads":
                        spread_odds = {
                            "event_id": event_id,
                            "bookmaker_key": bookmaker_key,
                        }

                        for outcome in market["outcomes"]:
                            price = outcome["price"]
                            point = outcome["point"]

                            if outcome["name"] == home_team:
                                spread_odds["home_team_line"] = point
                                spread_odds["home_team_odds"] = price
                                continue

                            if outcome["name"] == away_team:
                                spread_odds["away_team_line"] = point
                                spread_odds["away_team_odds"] = price
                                continue

                        spread_odds_list.append(spread_odds)
                        continue

                    if market_key == "totals":
                        totals_odds = {
                            "event_id": event_id,
                            "bookmaker_key": bookmaker_key,
                            "line": market["outcomes"][0]["point"],
                        }

                        for outcome in market["outcomes"]:
                            price = outcome["price"]

                            if outcome["name"] == "Over":
                                totals_odds["over_odds"] = price
                                continue

                            if outcome["name"] == "Under":
                                totals_odds["under_odds"] = price
                                continue

                        totals_odds_list.append(totals_odds)
                        continue

        return {
            "events": events_list,
            "moneyline_odds": moneyline_odds_list,
            "spread_odds": spread_odds_list,
            "totals_odds": totals_odds_list,
        }

    @classmethod
    def _process_player_props(cls, player_props_json_list: list[list[dict]]) -> dict:
        """"""
        player_props_dict = {}
        player_props_odds_list = []

        for player_props_json in player_props_json_list:
            for event_json in player_props_json:
                event_id = event_json["id"]
                event = TheOddsAPIEvent.query.filter_by(id=event_id).first()

                home_team_id = event.home_team_id
                away_team_id = event.away_team_id

                for bookmaker in event_json["bookmakers"]:
                    bookmaker_key = bookmaker["key"]

                    for market in bookmaker["markets"]:
                        market_key = market["key"]

                        for outcome in market["outcomes"]:
                            description = outcome["description"]
                            name = outcome["name"]
                            point = outcome["point"]
                            price = outcome["price"]

                            player_ids = NBAStatsAPIService.get_player_ids(description)

                            if len(player_ids) != 1:
                                continue

                            player_id = player_ids[0]

                            player_team_id = NBAStatsAPIService.get_player_team_id(player_id)
                            opponent_team_id = None

                            if player_team_id == home_team_id:
                                opponent_team_id = away_team_id
                            elif player_team_id == away_team_id:
                                opponent_team_id = home_team_id
                            else:
                                print("Problem")
                                continue

                            player_prop_key = (
                                event_id,
                                player_id,
                                opponent_team_id,
                                point,
                                market_key,
                                "alternate" in market_key,
                            )

                            if player_prop_key not in player_props_dict:
                                player_props_dict[player_prop_key] = uuid.uuid4().hex

                            player_prop_id = player_props_dict[player_prop_key]

                            player_prop_odds = {
                                "player_prop_id": player_prop_id,
                                "bookmaker_key": bookmaker_key,
                                "outcome": name,
                                "odds": price,
                            }

                            player_props_odds_list.append(player_prop_odds)

        player_props = []

        for key, player_prop_id in player_props_dict.items():
            event_id, player_id, opponent_team_id, line, market_key, alt = key

            # Calculate stats (last 5, 10, 20, 30 games, season, head-to-head, etc.)
            last_5_hr_stats = NBAStatsAPIService.calculate_last_n_games_hit_rate_stats(
                player_id, MARKET_STATS_MAPPING[market_key], line, 5
            )

            last_5_hits = last_5_hr_stats["hits"]
            last_5_avg = last_5_hr_stats["average"]

            last_10_hr_stats = NBAStatsAPIService.calculate_last_n_games_hit_rate_stats(
                player_id, MARKET_STATS_MAPPING[market_key], line, 10
            )

            last_10_hits = last_10_hr_stats["hits"]
            last_10_avg = last_10_hr_stats["average"]

            last_20_hr_stats = NBAStatsAPIService.calculate_last_n_games_hit_rate_stats(
                player_id, MARKET_STATS_MAPPING[market_key], line, 20
            )

            last_20_hits = last_20_hr_stats["hits"]
            last_20_avg = last_20_hr_stats["average"]

            last_30_hr_stats = NBAStatsAPIService.calculate_last_n_games_hit_rate_stats(
                player_id, MARKET_STATS_MAPPING[market_key], line, 30
            )

            last_30_hits = last_30_hr_stats["hits"]
            last_30_avg = last_30_hr_stats["average"]

            season_hr_stats = NBAStatsAPIService.calculate_season_hit_rate_stats(
                player_id, MARKET_STATS_MAPPING[market_key], line
            )

            season_games = season_hr_stats["games"]
            season_hits = season_hr_stats["hits"]
            season_avg = season_hr_stats["average"]

            h2h_hr_stats = NBAStatsAPIService.calculate_h2h_hit_rate_stats(
                player_id,
                MARKET_STATS_MAPPING[market_key],
                line,
                opponent_team_id,
            )

            h2h_games = h2h_hr_stats["games"]
            h2h_hits = h2h_hr_stats["hits"]
            h2h_avg = h2h_hr_stats["average"]

            hot_streak = NBAStatsAPIService.calculate_hot_streak(
                player_id, MARKET_STATS_MAPPING[market_key], line
            )

            # Create a dictionary for each player prop record
            player_prop_data = {
                "id": player_prop_id,  # Assuming this comes from player_props_dict
                "event_id": event_id,
                "player_id": player_id,
                "opponent_team_id": opponent_team_id,
                "market": market_key,
                "line": line,
                "alternate": alt,
                "last_five_games_hits": last_5_hits,
                "last_five_games_hit_rate": (
                    last_5_hits / 5 if last_5_hits is not None else None
                ),
                "last_five_games_average": last_5_avg,
                "last_ten_games_hits": last_10_hits,
                "last_ten_games_hit_rate": (
                    last_10_hits / 10 if last_10_hits is not None else None
                ),
                "last_ten_games_average": last_10_avg,
                "last_twenty_games_hits": last_20_hits,
                "last_twenty_games_hit_rate": (
                    last_20_hits / 20 if last_20_hits is not None else None
                ),
                "last_twenty_games_average": last_20_avg,
                "last_thirty_games_hits": last_30_hits,
                "last_thirty_games_hit_rate": (
                    last_30_hits / 30 if last_30_hits is not None else None
                ),
                "last_thirty_games_average": last_30_avg,
                "season_games": season_games,
                "season_hits": season_hits,
                "season_hit_rate": (
                    season_hits / season_games if season_hits is not None else None
                ),
                "season_average": season_avg,
                "head_to_head_matchups": h2h_games,
                "head_to_head_hits": h2h_hits,
                "head_to_head_hit_rate": (
                    h2h_hits / h2h_games if h2h_hits is not None else None
                ),
                "head_to_head_average": h2h_avg,
                "hot_streak": hot_streak,
            }

            # Append the dictionary to bulk_data
            player_props.append(player_prop_data)

        return {
            "player_props": player_props,
            "player_props_odds": player_props_odds_list,
        }

    @staticmethod
    def get_event_by_team_id(team_id: int):
        event = (
            db.session.query(TheOddsAPIEvent)
            .filter(
                (TheOddsAPIEvent.home_team_id == team_id)
                | (TheOddsAPIEvent.away_team_id == team_id)
            )
            .first()
        )  # Use first() to get only one result, or None if not found

        # Return the event's id if found, otherwise return None
        if event:
            return event.id

        return None

    @staticmethod
    def _format_event_time(event_start_time_str):
        # Step 1: Parse the string into a datetime object
        event_time_utc = datetime.strptime(
            str(event_start_time_str), "%Y-%m-%d %H:%M:%S"
        )

        # Step 2: Convert it to the US Eastern Time Zone (EST/EDT)
        eastern_tz = pytz.timezone("US/Eastern")
        event_time_est = event_time_utc.replace(tzinfo=pytz.utc).astimezone(eastern_tz)

        # Step 3: Format the datetime object into a readable string (e.g., "Fri 8:00 PM EST")
        return event_time_est.strftime("%a %I:%M %p %Z")

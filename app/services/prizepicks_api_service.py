# prizepicks_api_service.py

import uuid

from app.api_clients.prizepicks_api_client import PrizePicksAPIClient
from app.markets import MARKET_STATS_MAPPING
from app.models.odds_api_models import *
from app.services.nba_stats_api_service import NBAStatsAPIService
from app.services.the_odds_api_service import TheOddsAPIService


class PrizePicksAPIService:
    @staticmethod
    def load_player_props():
        """Function to fetch, process, and load the data from prizepicks api."""
        player_props_df = PrizePicksAPIClient.get_first_half_props()

        if player_props_df.empty:
            return

        props = []
        odds = []

        for index, row in player_props_df.iterrows():
            print(index)
            player_ids = NBAStatsAPIService.get_player_ids(row["attributes.name"])
            if len(player_ids) != 1:
                continue

            player_id = player_ids[0]

            opponent_team_abbr = row["attributes.description"].split(" ")[0]
            opponent_team_id = NBAStatsAPIService.get_team_id(abbr=opponent_team_abbr)

            event_id = TheOddsAPIService.get_event_by_team_id(opponent_team_id)

            market_key = f"1H {row["attributes.stat_type"]}"
            line = row["attributes.line_score"]

            # Last 5 games
            l5_hr_stats_over = NBAStatsAPIService.calculate_last_n_games_hit_rate_stats(
                player_id, MARKET_STATS_MAPPING[market_key], "Over", line, 5
            )

            l5_hits_over = l5_hr_stats_over["hits"]
            l5_avg_over = l5_hr_stats_over["average"]

            l5_hr_stats_under = (
                NBAStatsAPIService.calculate_last_n_games_hit_rate_stats(
                    player_id, MARKET_STATS_MAPPING[market_key], "Under", line, 5
                )
            )

            l5_hits_under = l5_hr_stats_under["hits"]
            l5_avg_under = l5_hr_stats_under["average"]

            # Last 10 games
            l10_hr_stats_over = (
                NBAStatsAPIService.calculate_last_n_games_hit_rate_stats(
                    player_id, MARKET_STATS_MAPPING[market_key], "Over", line, 10
                )
            )

            l10_hits_over = l10_hr_stats_over["hits"]
            l10_avg_over = l10_hr_stats_over["average"]

            l10_hr_stats_under = (
                NBAStatsAPIService.calculate_last_n_games_hit_rate_stats(
                    player_id, MARKET_STATS_MAPPING[market_key], "Under", line, 10
                )
            )

            l10_hits_under = l10_hr_stats_under["hits"]
            l10_avg_under = l10_hr_stats_under["average"]

            # Last 20 games
            l20_hr_stats_over = (
                NBAStatsAPIService.calculate_last_n_games_hit_rate_stats(
                    player_id, MARKET_STATS_MAPPING[market_key], "Over", line, 20
                )
            )

            l20_hits_over = l20_hr_stats_over["hits"]
            l20_avg_over = l20_hr_stats_over["average"]

            l20_hr_stats_under = (
                NBAStatsAPIService.calculate_last_n_games_hit_rate_stats(
                    player_id, MARKET_STATS_MAPPING[market_key], "Under", line, 20
                )
            )

            l20_hits_under = l20_hr_stats_under["hits"]
            l20_avg_under = l20_hr_stats_under["average"]

            # Last 30 games
            l30_hr_stats_over = (
                NBAStatsAPIService.calculate_last_n_games_hit_rate_stats(
                    player_id, MARKET_STATS_MAPPING[market_key], "Over", line, 30
                )
            )

            l30_hits_over = l30_hr_stats_over["hits"]
            l30_avg_over = l30_hr_stats_over["average"]

            l30_hr_stats_under = (
                NBAStatsAPIService.calculate_last_n_games_hit_rate_stats(
                    player_id, MARKET_STATS_MAPPING[market_key], "Under", line, 30
                )
            )

            l30_hits_under = l30_hr_stats_under["hits"]
            l30_avg_under = l30_hr_stats_under["average"]

            # Head-to-Head "Over" stats
            h2h_over_stats = NBAStatsAPIService.calculate_h2h_hit_rate_stats(
                player_id,
                MARKET_STATS_MAPPING[market_key],
                "Over",
                line,
                opponent_team_id,
            )

            h2h_over_games = h2h_over_stats["games"]
            h2h_over_hits = h2h_over_stats["hits"]
            h2h_over_avg = h2h_over_stats["average"]

            # Head-to-Head "Under" stats
            h2h_under_stats = NBAStatsAPIService.calculate_h2h_hit_rate_stats(
                player_id,
                MARKET_STATS_MAPPING[market_key],
                "Under",
                line,
                opponent_team_id,
            )

            h2h_under_games = h2h_under_stats["games"]
            h2h_under_hits = h2h_under_stats["hits"]
            h2h_under_avg = h2h_under_stats["average"]

            # Season "Over" stats
            season_over_stats = NBAStatsAPIService.calculate_season_hit_rate_stats(
                player_id, MARKET_STATS_MAPPING[market_key], "Over", line
            )

            season_over_games = season_over_stats["games"]
            season_over_hits = season_over_stats["hits"]
            season_over_avg = season_over_stats["average"]

            # Season "Under" stats
            season_under_stats = NBAStatsAPIService.calculate_season_hit_rate_stats(
                player_id, MARKET_STATS_MAPPING[market_key], "Under", line
            )

            season_under_games = season_under_stats["games"]
            season_under_hits = season_under_stats["hits"]
            season_under_avg = season_under_stats["average"]

            # Hot streak "Over" stats
            hot_streak_over = NBAStatsAPIService.calculate_hot_streak(
                player_id, MARKET_STATS_MAPPING[market_key], "Over", line
            )

            # Hot streak "Under" stats
            hot_streak_under = NBAStatsAPIService.calculate_hot_streak(
                player_id, MARKET_STATS_MAPPING[market_key], "Under", line
            )

            player_prop_over = {
                "id": uuid.uuid4().hex,
                "event_id": event_id,
                "player_id": player_id,
                "opponent_team_id": opponent_team_id,
                "market": market_key,
                "outcome": "Over",
                "line": line,
                "alternate": False,
                "last_five_games_hits": l5_hits_over,  # Assuming these variables are already computed
                "last_five_games_hit_rate": (
                    l5_hits_over / 5 if l5_hits_over is not None else None
                ),
                "last_five_games_average": l5_avg_over,
                "last_ten_games_hits": l10_hits_over,
                "last_ten_games_hit_rate": (
                    l10_hits_over / 10 if l10_hits_over is not None else None
                ),
                "last_ten_games_average": l10_avg_over,
                "last_twenty_games_hits": l20_hits_over,
                "last_twenty_games_hit_rate": (
                    l20_hits_over / 20 if l20_hits_over is not None else None
                ),
                "last_twenty_games_average": l20_avg_over,
                "last_thirty_games_hits": l30_hits_over,
                "last_thirty_games_hit_rate": (
                    l30_hits_over / 30 if l30_hits_over is not None else None
                ),
                "last_thirty_games_average": l30_avg_over,
                "season_games": season_over_games,
                "season_hits": season_over_hits,
                "season_hit_rate": (
                    season_over_hits / season_over_games
                    if season_over_hits is not None
                    else None
                ),
                "season_average": season_over_avg,
                "head_to_head_matchups": h2h_over_games,
                "head_to_head_hits": h2h_over_hits,
                "head_to_head_hit_rate": (
                    h2h_over_hits / h2h_over_games
                    if h2h_over_hits is not None
                    else None
                ),
                "head_to_head_average": h2h_over_avg,
                "hot_streak": hot_streak_over,
            }

            # Player prop for "Under"
            player_prop_under = {
                "id": uuid.uuid4().hex,
                "event_id": event_id,
                "player_id": player_id,
                "opponent_team_id": opponent_team_id,
                "market": market_key,
                "outcome": "Under",
                "line": line,
                "alternate": False,
                "last_five_games_hits": l5_hits_under,  # Assuming these variables are already computed
                "last_five_games_hit_rate": (
                    l5_hits_under / 5 if l5_hits_under is not None else None
                ),
                "last_five_games_average": l5_avg_under,
                "last_ten_games_hits": l10_hits_under,
                "last_ten_games_hit_rate": (
                    l10_hits_under / 10 if l10_hits_under is not None else None
                ),
                "last_ten_games_average": l10_avg_under,
                "last_twenty_games_hits": l20_hits_under,
                "last_twenty_games_hit_rate": (
                    l20_hits_under / 20 if l20_hits_under is not None else None
                ),
                "last_twenty_games_average": l20_avg_under,
                "last_thirty_games_hits": l30_hits_under,
                "last_thirty_games_hit_rate": (
                    l30_hits_under / 30 if l30_hits_under is not None else None
                ),
                "last_thirty_games_average": l30_avg_under,
                "season_games": season_under_games,
                "season_hits": season_under_hits,
                "season_hit_rate": (
                    season_under_hits / season_under_games
                    if season_under_hits is not None
                    else None
                ),
                "season_average": season_under_avg,
                "head_to_head_matchups": h2h_under_games,
                "head_to_head_hits": h2h_under_hits,
                "head_to_head_hit_rate": (
                    h2h_under_hits / h2h_under_games
                    if h2h_under_hits is not None
                    else None
                ),
                "head_to_head_average": h2h_under_avg,
                "hot_streak": hot_streak_under,
            }

            props.append(player_prop_over)
            props.append(player_prop_under)

            odds.append(
                {
                    "player_prop_id": player_prop_over["id"],
                    "bookmaker_key": "prizepicks",
                    "odds": -137,
                }
            )
            odds.append(
                {
                    "player_prop_id": player_prop_under["id"],
                    "bookmaker_key": "prizepicks",
                    "odds": -137,
                }
            )

        for prop in props:
            player_prop = PlayerProp(
                id=prop["id"],
                event_id=prop["event_id"],
                player_id=prop["player_id"],
                opponent_team_id=prop["opponent_team_id"],
                market=prop["market"],
                outcome=prop["outcome"],
                line=prop["line"],
                alternate=prop["alternate"],
                last_five_games_hits=prop.get("last_five_games_hits"),
                last_five_games_hit_rate=prop.get("last_five_games_hit_rate"),
                last_five_games_average=prop.get("last_five_games_average"),
                last_ten_games_hits=prop.get("last_ten_games_hits"),
                last_ten_games_hit_rate=prop.get("last_ten_games_hit_rate"),
                last_ten_games_average=prop.get("last_ten_games_average"),
                last_twenty_games_hits=prop.get("last_twenty_games_hits"),
                last_twenty_games_hit_rate=prop.get("last_twenty_games_hit_rate"),
                last_twenty_games_average=prop.get("last_twenty_games_average"),
                last_thirty_games_hits=prop.get("last_thirty_games_hits"),
                last_thirty_games_hit_rate=prop.get("last_thirty_games_hit_rate"),
                last_thirty_games_average=prop.get("last_thirty_games_average"),
                season_games=prop.get("season_games"),
                season_hits=prop.get("season_hits"),
                season_hit_rate=prop.get("season_hit_rate"),
                season_average=prop.get("season_average"),
                head_to_head_matchups=prop.get("head_to_head_matchups"),
                head_to_head_hits=prop.get("head_to_head_hits"),
                head_to_head_hit_rate=prop.get("head_to_head_hit_rate"),
                head_to_head_average=prop.get("head_to_head_average"),
                hot_streak=prop.get("hot_streak"),
            )

            db.session.add(player_prop)

            # Load odds into the PlayerPropOdds table
        for odd in odds:
            player_prop_odds = PlayerPropOdds(
                player_prop_id=odd["player_prop_id"],
                bookmaker_key=odd["bookmaker_key"],
                odds=odd["odds"],
            )
            db.session.add(player_prop_odds)

            # Commit all the changes to the database
        db.session.commit()

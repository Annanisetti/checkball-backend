# nba_stats_api_service.py

from datetime import datetime, timedelta
from statistics import mean
import Levenshtein
import pandas as pd

from app.models.nba_models import *
from app.api_clients.nba_stats_api_client import NBAStatsAPIClient


class NBAStatsAPIService:
    """
    Class containing methods for loading and fetching NBA data from db.

    Methods:
        load_teams
        load_players

        load_team_box_scores
        load_player_box_scores

        update_team_box_scores
        update_player_box_scores

        get_team_id

        get_player_ids
        get_player_team_id

        calculate_last_n_games_hit_rate_stats
        calculate_h2h_hit_rate_stats
        calculate_season_hit_rate_stats
        calculate_hot_streak
    """

    TEAMS_DATA = [
        {
            "id": 1610612737,
            "name": "Atlanta Hawks",
            "abbreviation": "ATL",
        },
        {
            "id": 1610612738,
            "name": "Boston Celtics",
            "abbreviation": "BOS",
        },
        {
            "id": 1610612751,
            "name": "Brooklyn Nets",
            "abbreviation": "BKN",
        },
        {
            "id": 1610612766,
            "name": "Charlotte Hornets",
            "abbreviation": "CHA",
        },
        {
            "id": 1610612741,
            "name": "Chicago Bulls",
            "abbreviation": "CHI",
        },
        {
            "id": 1610612739,
            "name": "Cleveland Cavaliers",
            "abbreviation": "CLE",
        },
        {
            "id": 1610612742,
            "name": "Dallas Mavericks",
            "abbreviation": "DAL",
        },
        {
            "id": 1610612743,
            "name": "Denver Nuggets",
            "abbreviation": "DEN",
        },
        {
            "id": 1610612765,
            "name": "Detroit Pistons",
            "abbreviation": "DET",
        },
        {
            "id": 1610612744,
            "name": "Golden State Warriors",
            "abbreviation": "GSW",
        },
        {
            "id": 1610612745,
            "name": "Houston Rockets",
            "abbreviation": "HOU",
        },
        {
            "id": 1610612754,
            "name": "Indiana Pacers",
            "abbreviation": "IND",
        },
        {
            "id": 1610612746,
            "name": "Los Angeles Clippers",
            "abbreviation": "LAC",
        },
        {
            "id": 1610612747,
            "name": "Los Angeles Lakers",
            "abbreviation": "LAL",
        },
        {
            "id": 1610612763,
            "name": "Memphis Grizzlies",
            "abbreviation": "MEM",
        },
        {
            "id": 1610612748,
            "name": "Miami Heat",
            "abbreviation": "MIA",
        },
        {
            "id": 1610612749,
            "name": "Milwaukee Bucks",
            "abbreviation": "MIL",
        },
        {
            "id": 1610612750,
            "name": "Minnesota Timberwolves",
            "abbreviation": "MIN",
        },
        {
            "id": 1610612740,
            "name": "New Orleans Pelicans",
            "abbreviation": "NOP",
        },
        {
            "id": 1610612752,
            "name": "New York Knicks",
            "abbreviation": "NYK",
        },
        {
            "id": 1610612760,
            "name": "Oklahoma City Thunder",
            "abbreviation": "OKC",
        },
        {
            "id": 1610612753,
            "name": "Orlando Magic",
            "abbreviation": "ORL",
        },
        {
            "id": 1610612755,
            "name": "Philadelphia 76ers",
            "abbreviation": "PHI",
        },
        {
            "id": 1610612756,
            "name": "Phoenix Suns",
            "abbreviation": "PHX",
        },
        {
            "id": 1610612757,
            "name": "Portland Trail Blazers",
            "abbreviation": "POR",
        },
        {
            "id": 1610612758,
            "name": "Sacramento Kings",
            "abbreviation": "SAC",
        },
        {
            "id": 1610612759,
            "name": "San Antonio Spurs",
            "abbreviation": "SAS",
        },
        {
            "id": 1610612761,
            "name": "Toronto Raptors",
            "abbreviation": "TOR",
        },
        {
            "id": 1610612762,
            "name": "Utah Jazz",
            "abbreviation": "UTA",
        },
        {
            "id": 1610612764,
            "name": "Washington Wizards",
            "abbreviation": "WAS",
        },
    ]

    SEASON_TYPES = ["Regular Season", "IST", "PlayIn", "Playoffs"]
    current_season = "2024-25"
    current_season_type_idx = 2

    player_box_scores_traditional = None

    @classmethod
    def load_teams(cls) -> None:
        """Method to load all NBA teams into Team table."""
        Team.__table__.drop(db.engine, checkfirst=True)
        Team.__table__.create(db.engine)

        for team_data in cls.TEAMS_DATA:
            team = Team(
                id=team_data["id"],
                name=team_data["name"],
                abbreviation=team_data["abbreviation"],
            )
            db.session.add(team)

        db.session.commit()

        print("Finished Loading Teams")

    @staticmethod
    def load_players() -> None:
        """Method to load Players Index data into Player table."""
        Player.__table__.drop(db.engine, checkfirst=True)
        Player.__table__.create(db.engine)

        # Fetch data from the NBA API
        json_data = NBAStatsAPIClient.get_players()

        # Get headers and rows
        headers = json_data["resultSets"][0]["headers"]
        rows = json_data["resultSets"][0]["rowSet"]

        # Map header names to their indices
        indices = {header: i for i, header in enumerate(headers)}

        # Prepare bulk insert data
        players_bulk_data = []

        for row in rows:
            full_name = f"{row[indices['PLAYER_FIRST_NAME']]} {row[indices['PLAYER_LAST_NAME']]}"

            player_data = {
                "id": row[indices["PERSON_ID"]],
                "last_name": row[indices["PLAYER_LAST_NAME"]],
                "first_name": row[indices["PLAYER_FIRST_NAME"]],
                "full_name": full_name,
                "team_id": row[indices["TEAM_ID"]],
                "jersey_number": row[indices["JERSEY_NUMBER"]],
                "position": row[indices["POSITION"]],
                "height": row[indices["HEIGHT"]],
                "weight": row[indices["WEIGHT"]],
                "college": row[indices["COLLEGE"]],
                "country": row[indices["COUNTRY"]],
                "draft_year": row[indices["DRAFT_YEAR"]],
                "draft_round": row[indices["DRAFT_ROUND"]],
                "draft_number": row[indices["DRAFT_NUMBER"]],
                "on_roster": False if row[indices["ROSTER_STATUS"]] is None else True,
            }

            players_bulk_data.append(player_data)

        # Bulk insert the player data
        db.session.bulk_insert_mappings(Player, players_bulk_data)
        db.session.commit()

        print("Finished Loading Players")

    @classmethod
    def load_team_box_scores(cls) -> None:
        """Method to load Team Box Scores into db."""
        TeamBoxScoreTraditional.__table__.drop(db.engine, checkfirst=True)
        TeamBoxScoreTraditional.__table__.create(db.engine)

        TeamBoxScoreAdvanced.__table__.drop(db.engine, checkfirst=True)
        TeamBoxScoreAdvanced.__table__.create(db.engine)

        TeamBoxScoreMiscellaneous.__table__.drop(db.engine, checkfirst=True)
        TeamBoxScoreMiscellaneous.__table__.create(db.engine)

        TeamBoxScoreScoring.__table__.drop(db.engine, checkfirst=True)
        TeamBoxScoreScoring.__table__.create(db.engine)

        for year in range(2023, 2025):
            season = f"{year}-{str(year + 1)[-2:]}"

            for season_type in cls.SEASON_TYPES:
                for period in range(0, 10):
                    if season_type == "Playoffs":
                        playoff_rounds = range(1, 5)
                    else:
                        playoff_rounds = [None]

                    for playoff_round in playoff_rounds:
                        bulk_data = []

                        # Fetch, Process and Load Traditional Team Box Scores
                        trad = NBAStatsAPIClient.get_team_box_scores(
                            "Base", season, season_type, period, playoff_round
                        )

                        if trad is None or len(trad["resultSets"][0]["rowSet"]) == 0:
                            continue

                        trad_headers = trad["resultSets"][0]["headers"]
                        trad_box_scores = trad["resultSets"][0]["rowSet"]

                        trad_indices = {
                            header: i for i, header in enumerate(trad_headers)
                        }

                        for box_score in trad_box_scores:
                            game_date = datetime.strptime(
                                box_score[trad_indices["GAME_DATE"]],
                                "%Y-%m-%dT%H:%M:%S",
                            )
                            matchup = box_score[trad_indices["MATCHUP"]]
                            away_game = "@" in matchup

                            opponent_team_abbr = matchup.split(" ")[-1]
                            opponent_team_id = cls.get_team_id(abbr=opponent_team_abbr)

                            bulk_data.append(
                                TeamBoxScoreTraditional(
                                    season_year=season,
                                    season_type=season_type,
                                    playoff_round=playoff_round,
                                    team_id=box_score[trad_indices["TEAM_ID"]],
                                    opponent_team_id=opponent_team_id,
                                    game_id=box_score[trad_indices["GAME_ID"]],
                                    game_date=game_date,
                                    away_game=away_game,
                                    win_loss=box_score[trad_indices["WL"]],
                                    period=period,
                                    minutes_played=box_score[trad_indices["MIN"]],
                                    field_goals_made=box_score[trad_indices["FGM"]],
                                    field_goals_attempted=box_score[
                                        trad_indices["FGA"]
                                    ],
                                    field_goal_percentage=box_score[
                                        trad_indices["FG_PCT"]
                                    ],
                                    three_point_field_goals_made=box_score[
                                        trad_indices["FG3M"]
                                    ],
                                    three_point_field_goals_attempted=box_score[
                                        trad_indices["FG3A"]
                                    ],
                                    three_point_field_goal_percentage=box_score[
                                        trad_indices["FG3_PCT"]
                                    ],
                                    free_throws_made=box_score[trad_indices["FTM"]],
                                    free_throws_attempted=box_score[
                                        trad_indices["FTA"]
                                    ],
                                    free_throw_percentage=box_score[
                                        trad_indices["FT_PCT"]
                                    ],
                                    offensive_rebounds=box_score[trad_indices["OREB"]],
                                    defensive_rebounds=box_score[trad_indices["DREB"]],
                                    rebounds=box_score[trad_indices["REB"]],
                                    assists=box_score[trad_indices["AST"]],
                                    turnovers=box_score[trad_indices["TOV"]],
                                    steals=box_score[trad_indices["STL"]],
                                    blocks=box_score[trad_indices["BLK"]],
                                    block_attempts=box_score[trad_indices["BLKA"]],
                                    personal_fouls=box_score[trad_indices["PF"]],
                                    personal_fouls_drawn=box_score[trad_indices["PFD"]],
                                    points=box_score[trad_indices["PTS"]],
                                    plus_minus=box_score[trad_indices["PLUS_MINUS"]],
                                )
                            )

                        db.session.bulk_save_objects(bulk_data)
                        db.session.commit()

                        bulk_data.clear()

                        # Advanced Team Box Scores
                        adv = NBAStatsAPIClient.get_team_box_scores(
                            "Advanced", season, season_type, period, playoff_round
                        )

                        if adv is None or len(adv["resultSets"][0]["rowSet"]) == 0:
                            continue

                        adv_headers = adv["resultSets"][0]["headers"]
                        adv_box_scores = adv["resultSets"][0]["rowSet"]

                        adv_indices = {
                            header: i for i, header in enumerate(adv_headers)
                        }

                        for box_score in adv_box_scores:
                            game_date = datetime.strptime(
                                box_score[adv_indices["GAME_DATE"]], "%Y-%m-%dT%H:%M:%S"
                            )
                            matchup = box_score[trad_indices["MATCHUP"]]
                            away_game = "@" in matchup

                            opponent_team_abbr = matchup.split(" ")[-1]
                            opponent_team_id = cls.get_team_id(abbr=opponent_team_abbr)

                            bulk_data.append(
                                TeamBoxScoreAdvanced(
                                    season_year=season,
                                    season_type=season_type,
                                    playoff_round=playoff_round,
                                    team_id=box_score[adv_indices["TEAM_ID"]],
                                    opponent_team_id=opponent_team_id,
                                    game_id=box_score[adv_indices["GAME_ID"]],
                                    game_date=game_date,
                                    away_game=away_game,
                                    win_loss=box_score[adv_indices["WL"]],
                                    period=period,
                                    minutes_played=box_score[adv_indices["MIN"]],
                                    offensive_rating=box_score[
                                        adv_indices["OFF_RATING"]
                                    ],
                                    defensive_rating=box_score[
                                        adv_indices["DEF_RATING"]
                                    ],
                                    net_rating=box_score[adv_indices["NET_RATING"]],
                                    assist_percentage=box_score[adv_indices["AST_PCT"]],
                                    assist_turnover_ratio=box_score[
                                        adv_indices["AST_TO"]
                                    ],
                                    assist_ratio=box_score[adv_indices["AST_RATIO"]],
                                    offensive_rebound_percentage=box_score[
                                        adv_indices["OREB_PCT"]
                                    ],
                                    defensive_rebound_percentage=box_score[
                                        adv_indices["DREB_PCT"]
                                    ],
                                    rebound_percentage=box_score[
                                        adv_indices["REB_PCT"]
                                    ],
                                    turnover_percentage=box_score[
                                        adv_indices["TM_TOV_PCT"]
                                    ],
                                    effective_field_goal_percentage=box_score[
                                        adv_indices["EFG_PCT"]
                                    ],
                                    true_shooting_percentage=box_score[
                                        adv_indices["TS_PCT"]
                                    ],
                                    pace=box_score[adv_indices["PACE"]],
                                    player_impact_estimate=box_score[
                                        adv_indices["PIE"]
                                    ],
                                )
                            )

                        db.session.bulk_save_objects(bulk_data)
                        db.session.commit()

                        bulk_data.clear()

                        # Misc Team Box Scores
                        misc = NBAStatsAPIClient.get_team_box_scores(
                            "Misc", season, season_type, period, playoff_round
                        )

                        if misc is None or len(misc["resultSets"][0]["rowSet"]) == 0:
                            continue

                        misc_headers = misc["resultSets"][0]["headers"]
                        misc_box_scores = misc["resultSets"][0]["rowSet"]

                        misc_indices = {
                            header: i for i, header in enumerate(misc_headers)
                        }

                        for box_score in misc_box_scores:
                            game_date = datetime.strptime(
                                box_score[misc_indices["GAME_DATE"]],
                                "%Y-%m-%dT%H:%M:%S",
                            )
                            matchup = box_score[misc_indices["MATCHUP"]]
                            away_game = "@" in matchup

                            opponent_team_abbr = matchup.split(" ")[-1]
                            opponent_team_id = cls.get_team_id(abbr=opponent_team_abbr)

                            bulk_data.append(
                                TeamBoxScoreMiscellaneous(
                                    season_year=season,
                                    season_type=season_type,
                                    playoff_round=playoff_round,
                                    team_id=box_score[misc_indices["TEAM_ID"]],
                                    opponent_team_id=opponent_team_id,
                                    game_id=box_score[misc_indices["GAME_ID"]],
                                    game_date=game_date,
                                    away_game=away_game,
                                    win_loss=box_score[misc_indices["WL"]],
                                    period=period,
                                    minutes_played=box_score[misc_indices["MIN"]],
                                    points_off_turnovers=box_score[
                                        misc_indices["PTS_OFF_TOV"]
                                    ],
                                    second_chance_points=box_score[
                                        misc_indices["PTS_2ND_CHANCE"]
                                    ],
                                    fast_break_points=box_score[misc_indices["PTS_FB"]],
                                    points_in_paint=box_score[
                                        misc_indices["PTS_PAINT"]
                                    ],
                                )
                            )

                        db.session.bulk_save_objects(bulk_data)
                        db.session.commit()

                        bulk_data.clear()

                        # Scoring Team Box Scores
                        scoring = NBAStatsAPIClient.get_team_box_scores(
                            "Scoring", season, season_type, period, playoff_round
                        )

                        if (
                            scoring is None
                            or len(scoring["resultSets"][0]["rowSet"]) == 0
                        ):
                            continue

                        scoring_headers = scoring["resultSets"][0]["headers"]
                        scoring_box_scores = scoring["resultSets"][0]["rowSet"]

                        scoring_indices = {
                            header: i for i, header in enumerate(scoring_headers)
                        }

                        for box_score in scoring_box_scores:
                            game_date = datetime.strptime(
                                box_score[misc_indices["GAME_DATE"]],
                                "%Y-%m-%dT%H:%M:%S",
                            )
                            matchup = box_score[scoring_indices["MATCHUP"]]
                            away_game = "@" in matchup

                            opponent_team_abbr = matchup.split(" ")[-1]
                            opponent_team_id = cls.get_team_id(abbr=opponent_team_abbr)

                            bulk_data.append(
                                TeamBoxScoreScoring(
                                    season_year=season,
                                    season_type=season_type,
                                    playoff_round=playoff_round,
                                    team_id=box_score[scoring_indices["TEAM_ID"]],
                                    opponent_team_id=opponent_team_id,
                                    game_id=box_score[scoring_indices["GAME_ID"]],
                                    game_date=game_date,
                                    away_game=away_game,
                                    win_loss=box_score[scoring_indices["WL"]],
                                    period=period,
                                    minutes_played=box_score[scoring_indices["MIN"]],
                                    percent_field_goals_attempted_two_pointers=box_score[
                                        scoring_indices["PCT_FGA_2PT"]
                                    ],
                                    percent_field_goals_attempted_three_pointers=box_score[
                                        scoring_indices["PCT_FGA_3PT"]
                                    ],
                                    percent_points_two_pointers=box_score[
                                        scoring_indices["PCT_PTS_2PT"]
                                    ],
                                    percent_points_mid_range=box_score[
                                        scoring_indices["PCT_PTS_2PT_MR"]
                                    ],
                                    percent_points_three_pointers=box_score[
                                        scoring_indices["PCT_PTS_3PT"]
                                    ],
                                    percent_points_fast_break=box_score[
                                        scoring_indices["PCT_PTS_FB"]
                                    ],
                                    percent_points_free_throws=box_score[
                                        scoring_indices["PCT_PTS_FT"]
                                    ],
                                    percent_points_off_turnovers=box_score[
                                        scoring_indices["PCT_PTS_OFF_TOV"]
                                    ],
                                    percent_points_in_paint=box_score[
                                        scoring_indices["PCT_PTS_PAINT"]
                                    ],
                                    percent_two_point_field_goals_made_assisted=box_score[
                                        scoring_indices["PCT_AST_2PM"]
                                    ],
                                    percent_two_point_field_goals_made_unassisted=box_score[
                                        scoring_indices["PCT_UAST_2PM"]
                                    ],
                                    percent_three_point_field_goals_made_assisted=box_score[
                                        scoring_indices["PCT_AST_3PM"]
                                    ],
                                    percent_three_point_field_goals_made_unassisted=box_score[
                                        scoring_indices["PCT_UAST_3PM"]
                                    ],
                                    percent_field_goals_made_assisted=box_score[
                                        scoring_indices["PCT_AST_FGM"]
                                    ],
                                    percent_field_goals_made_unassisted=box_score[
                                        scoring_indices["PCT_UAST_FGM"]
                                    ],
                                )
                            )

                        db.session.bulk_save_objects(bulk_data)
                        db.session.commit()

                        bulk_data.clear()

    @classmethod
    def _process_player_box_scores(cls, measure_type: str, season: str, season_type: str, period: int,
                                   playoff_round: int, date_from=None):
        bulk_data = []
        
        box_scores = NBAStatsAPIClient.get_player_box_scores(
            measure_type, season, season_type, period, playoff_round, date_from
        )

        if box_scores is None or len(box_scores["resultSets"][0]["rowSet"]) == 0:
            return bulk_data

        headers = box_scores["resultSets"][0]["headers"]
        rows = box_scores["resultSets"][0]["rowSet"]

        indices = {
            header: i for i, header in enumerate(headers)
        }

        for box_score in rows:
            game_date = datetime.strptime(
                box_score[indices["GAME_DATE"]],
                "%Y-%m-%dT%H:%M:%S",
            ).strftime("%m/%d/%Y")
            matchup = box_score[indices["MATCHUP"]]
            away_game = "@" in matchup

            opponent_team_abbr = matchup.split(" ")[-1]
            opponent_team_id = cls.get_team_id(abbr=opponent_team_abbr)

            if measure_type == "Base":
                bulk_data.append(
                    PlayerBoxScoreTraditional(
                        season_year=season,
                        season_type=season_type,
                        playoff_round=playoff_round,
                        player_id=box_score[indices["PLAYER_ID"]],
                        team_id=box_score[indices["TEAM_ID"]],
                        opponent_team_id=opponent_team_id,
                        game_id=box_score[indices["GAME_ID"]],
                        game_date=game_date,
                        away_game=away_game,
                        win_loss=box_score[indices["WL"]],
                        period=period,
                        minutes_played=box_score[indices["MIN"]],
                        field_goals_made=box_score[indices["FGM"]],
                        field_goals_attempted=box_score[
                            indices["FGA"]
                        ],
                        field_goal_percentage=box_score[
                            indices["FG_PCT"]
                        ],
                        three_point_field_goals_made=box_score[
                            indices["FG3M"]
                        ],
                        three_point_field_goals_attempted=box_score[
                            indices["FG3A"]
                        ],
                        three_point_field_goal_percentage=box_score[
                            indices["FG3_PCT"]
                        ],
                        free_throws_made=box_score[indices["FTM"]],
                        free_throws_attempted=box_score[
                            indices["FTA"]
                        ],
                        free_throw_percentage=box_score[
                            indices["FT_PCT"]
                        ],
                        offensive_rebounds=box_score[indices["OREB"]],
                        defensive_rebounds=box_score[indices["DREB"]],
                        rebounds=box_score[indices["REB"]],
                        assists=box_score[indices["AST"]],
                        turnovers=box_score[indices["TOV"]],
                        steals=box_score[indices["STL"]],
                        blocks=box_score[indices["BLK"]],
                        block_attempts=box_score[indices["BLKA"]],
                        personal_fouls=box_score[indices["PF"]],
                        personal_fouls_drawn=box_score[indices["PFD"]],
                        points=box_score[indices["PTS"]],
                        plus_minus=box_score[indices["PLUS_MINUS"]],
                        nba_fantasy_points=box_score[
                            indices["NBA_FANTASY_PTS"]
                        ],
                    )
                )
                continue

            if measure_type == "Advanced":
                bulk_data.append(
                    PlayerBoxScoreAdvanced(
                        season_year=season,
                        season_type=season_type,
                        playoff_round=playoff_round,
                        player_id=box_score[indices["PLAYER_ID"]],
                        team_id=box_score[indices["TEAM_ID"]],
                        opponent_team_id=opponent_team_id,
                        game_id=box_score[indices["GAME_ID"]],
                        game_date=game_date,
                        away_game=away_game,
                        win_loss=box_score[indices["WL"]],
                        period=period,
                        minutes_played=box_score[indices["MIN"]],
                        offensive_rating=box_score[
                            indices["OFF_RATING"]
                        ],
                        defensive_rating=box_score[
                            indices["DEF_RATING"]
                        ],
                        net_rating=box_score[indices["NET_RATING"]],
                        assist_percentage=box_score[indices["AST_PCT"]],
                        assist_turnover_ratio=box_score[
                            indices["AST_TO"]
                        ],
                        assist_ratio=box_score[indices["AST_RATIO"]],
                        offensive_rebound_percentage=box_score[
                            indices["OREB_PCT"]
                        ],
                        defensive_rebound_percentage=box_score[
                            indices["DREB_PCT"]
                        ],
                        rebound_percentage=box_score[
                            indices["REB_PCT"]
                        ],
                        turnover_ratio=box_score[indices["TM_TOV_PCT"]],
                        effective_field_goal_percentage=box_score[
                            indices["EFG_PCT"]
                        ],
                        true_shooting_percentage=box_score[
                            indices["TS_PCT"]
                        ],
                        usage_percentage=box_score[indices["USG_PCT"]],
                        pace=box_score[indices["PACE"]],
                        player_impact_estimate=box_score[
                            indices["PIE"]
                        ],
                    )
                )
                continue

            if measure_type == "Misc":
                bulk_data.append(
                    PlayerBoxScoreMiscellaneous(
                        season_year=season,
                        season_type=season_type,
                        playoff_round=playoff_round,
                        player_id=box_score[indices["PLAYER_ID"]],
                        team_id=box_score[indices["TEAM_ID"]],
                        opponent_team_id=opponent_team_id,
                        game_id=box_score[indices["GAME_ID"]],
                        game_date=game_date,
                        away_game=away_game,
                        win_loss=box_score[indices["WL"]],
                        period=period,
                        minutes_played=box_score[indices["MIN"]],
                        points_off_turnovers=box_score[
                            indices["PTS_OFF_TOV"]
                        ],
                        second_chance_points=box_score[
                            indices["PTS_2ND_CHANCE"]
                        ],
                        fast_break_points=box_score[indices["PTS_FB"]],
                        points_in_paint=box_score[
                            indices["PTS_PAINT"]
                        ],
                        opponent_points_off_turnovers=box_score[
                            indices["OPP_PTS_OFF_TOV"]
                        ],
                        opponent_second_chance_points=box_score[
                            indices["OPP_PTS_2ND_CHANCE"]
                        ],
                        opponent_fast_break_points=box_score[
                            indices["OPP_PTS_FB"]
                        ],
                        opponent_points_in_paint=box_score[
                            indices["OPP_PTS_PAINT"]
                        ],
                    )
                )
                continue

            if measure_type == "Scoring":
                bulk_data.append(
                    PlayerBoxScoreScoring(
                        season_year=season,
                        season_type=season_type,
                        playoff_round=playoff_round,
                        player_id=box_score[indices["PLAYER_ID"]],
                        team_id=box_score[indices["TEAM_ID"]],
                        opponent_team_id=opponent_team_id,
                        game_id=box_score[indices["GAME_ID"]],
                        game_date=game_date,
                        away_game=away_game,
                        win_loss=box_score[indices["WL"]],
                        period=period,
                        minutes_played=box_score[indices["MIN"]],
                        percent_field_goals_attempted_two_pointers=box_score[
                            indices["PCT_FGA_2PT"]
                        ],
                        percent_field_goals_attempted_three_pointers=box_score[
                            indices["PCT_FGA_3PT"]
                        ],
                        percent_points_two_pointers=box_score[
                            indices["PCT_PTS_2PT"]
                        ],
                        percent_points_mid_range=box_score[
                            indices["PCT_PTS_2PT_MR"]
                        ],
                        percent_points_three_pointers=box_score[
                            indices["PCT_PTS_3PT"]
                        ],
                        percent_points_fast_break=box_score[
                            indices["PCT_PTS_FB"]
                        ],
                        percent_points_free_throws=box_score[
                            indices["PCT_PTS_FT"]
                        ],
                        percent_points_off_turnovers=box_score[
                            indices["PCT_PTS_OFF_TOV"]
                        ],
                        percent_points_in_paint=box_score[
                            indices["PCT_PTS_PAINT"]
                        ],
                        percent_two_point_field_goals_made_assisted=box_score[
                            indices["PCT_AST_2PM"]
                        ],
                        percent_two_point_field_goals_made_unassisted=box_score[
                            indices["PCT_UAST_2PM"]
                        ],
                        percent_three_point_field_goals_made_assisted=box_score[
                            indices["PCT_AST_3PM"]
                        ],
                        percent_three_point_field_goals_made_unassisted=box_score[
                            indices["PCT_UAST_3PM"]
                        ],
                        percent_field_goals_made_assisted=box_score[
                            indices["PCT_AST_FGM"]
                        ],
                        percent_field_goals_made_unassisted=box_score[
                            indices["PCT_UAST_FGM"]
                        ],
                    ))
                continue

        return bulk_data

    @classmethod
    def load_player_box_scores(cls) -> None:
        """Method to load Player Box Scores into db."""
        PlayerBoxScoreTraditional.__table__.drop(db.engine, checkfirst=True)
        PlayerBoxScoreTraditional.__table__.create(db.engine)

        PlayerBoxScoreAdvanced.__table__.drop(db.engine, checkfirst=True)
        PlayerBoxScoreAdvanced.__table__.create(db.engine)

        PlayerBoxScoreMiscellaneous.__table__.drop(db.engine, checkfirst=True)
        PlayerBoxScoreMiscellaneous.__table__.create(db.engine)

        PlayerBoxScoreScoring.__table__.drop(db.engine, checkfirst=True)
        PlayerBoxScoreScoring.__table__.create(db.engine)

        for year in range(2023, 2025):
            season = f"{year}-{str(year + 1)[-2:]}"

            for season_type in cls.SEASON_TYPES:
                for period in range(0, 10):
                    if season_type == "Playoffs":
                        playoff_rounds = range(1, 5)
                    else:
                        playoff_rounds = [None]

                    for playoff_round in playoff_rounds:
                        trad_box_scores = cls._process_player_box_scores("Base", season, season_type, period, playoff_round)

                        db.session.bulk_save_objects(trad_box_scores)
                        db.session.commit()

                        # adv_box_scores = cls._process_player_box_scores("Advanced", season, season_type, period,
                        #                                                  playoff_round)
                        #
                        # db.session.bulk_save_objects(adv_box_scores)
                        # db.session.commit()
                        #
                        # misc_box_scores = cls._process_player_box_scores("Misc", season, season_type, period,
                        #                                                  playoff_round)
                        #
                        # db.session.bulk_save_objects(misc_box_scores)
                        # db.session.commit()
                        #
                        # scoring_box_scores = cls._process_player_box_scores("Scoring", season, season_type, period,
                        #                                                  playoff_round)
                        #
                        # db.session.bulk_save_objects(scoring_box_scores)
                        # db.session.commit()

                        # Offensive Rebounding

                print(f"finished loading player box scores for {season} {season_type}")

    @classmethod
    def load_player_tracking_box_scores(cls):
        PlayerBoxScoreRebounding.__table__.drop(db.engine, checkfirst=True)
        PlayerBoxScoreRebounding.__table__.create(db.engine)
        
        PlayerBoxScorePassing.__table__.drop(db.engine, checkfirst=True)
        PlayerBoxScorePassing.__table__.create(db.engine)
        
        start_date = datetime.strptime("10/29/2013", "%m/%d/%Y")
        end_date = datetime.today()
        time_difference = timedelta(days=1)

        current_date = start_date
        
        while current_date <= end_date:
            current_date_formatted = current_date.strftime("%m/%d/%Y")
            passing_box_scores = NBAStatsAPIClient.get_player_tracking_box_scores(measure_type="Passing", date_from=current_date, date_to=current_date)
            rebounding_box_scores = NBAStatsAPIClient.get_player_tracking_box_scores(measure_type="Rebounding", date_from=current_date, date_to=current_date)

            if rebounding_box_scores is not None and len(rebounding_box_scores["resultSets"][0]["rowSet"]) != 0:
                headers = rebounding_box_scores["resultSets"][0]["headers"]
                rows = rebounding_box_scores["resultSets"][0]["rowSet"]

                indices = {
                    header: i for i, header in enumerate(headers)
                }

                for box_score in rows:
                    db.session.add(PlayerBoxScoreRebounding(
                        player_id=box_score[indices["PLAYER_ID"]],
                        game_date=current_date_formatted,
                        
                        # Defensive Rebounds
                        contested_defensive_rebounds=box_score[indices["DREB_CONTEST"]],
                        contested_defensive_rebound_percentage=box_score[indices["DREB_CONTEST_PCT"]],
                        defensive_rebound_chances=box_score[indices["DREB_CHANCES"]],
                        defensive_rebound_chance_percentage=box_score[indices["DREB_CHANCE_PCT"]],
                        deferred_defensive_rebound_chances=box_score[indices["DREB_CHANCE_DEFER"]],
                        adjusted_defensive_rebound_chance_percentage=box_score[indices["DREB_CHANCE_PCT_ADJ"]],
                        average_defensive_rebound_distance=box_score[indices["AVG_DREB_DIST"]],
                        
                        # Offensive Rebounds
                        contested_offensive_rebounds=box_score[indices["OREB_CONTEST"]],
                        contested_offensive_rebound_percentage=box_score[indices["OREB_CONTEST_PCT"]],
                        offensive_rebound_chances=box_score[indices["OREB_CHANCES"]],
                        offensive_rebound_chance_percentage=box_score[indices["OREB_CHANCE_PCT"]],
                        deferred_offensive_rebound_chances=box_score[indices["OREB_CHANCE_DEFER"]],
                        adjusted_offensive_rebound_chance_percentage=box_score[indices["OREB_CHANCE_PCT_ADJ"]],
                        average_offensive_rebound_distance=box_score[indices["AVG_OREB_DIST"]]
                    ))
                    
                db.session.commit()
            
            if passing_box_scores is not None and len(passing_box_scores["resultSets"][0]["rowSet"]) != 0:
                headers = passing_box_scores["resultSets"][0]["headers"]
                rows = passing_box_scores["resultSets"][0]["rowSet"]

                indices = {
                    header: i for i, header in enumerate(headers)
                }

                for box_score in rows:
                    db.session.add(PlayerBoxScorePassing(
                        player_id=box_score[indices["PLAYER_ID"]],
                        game_date=current_date_formatted,
                        passes_made=box_score[indices["PASSES_MADE"]],
                        passes_received=box_score[indices["PASSES_RECEIVED"]],
                        ft_assists=box_score[indices["FT_AST"]],
                        secondary_assists=box_score[indices["SECONDARY_AST"]],
                        potential_assists=box_score[indices["POTENTIAL_AST"]],
                        assist_points_created=box_score[indices["AST_PTS_CREATED"]],
                        assist_to_pass_percentage=box_score[indices["AST_TO_PASS_PCT"]],
                        adjusted_assist_to_pass_percentage=box_score[indices["AST_TO_PASS_PCT_ADJ"]]
                    ))
                    
                db.session.commit()
            
            print("done withi", current_date)
                
            current_date += timedelta(days=1)

    @classmethod
    def initialize_box_scores_df(cls):
        """Function for to load relevant player box scores into pandas df for player props hr calculations."""
        query = PlayerBoxScoreTraditional.query.all()

        # Convert the list of objects into a list of dictionaries
        data = [
            {
                "id": record.id,
                "season_year": record.season_year,
                "season_type": record.season_type,
                "playoff_round": record.playoff_round,
                "player_id": record.player_id,
                "team_id": record.team_id,
                "opponent_team_id": record.opponent_team_id,
                "game_id": record.game_id,
                "game_date": record.game_date,
                "away_game": record.away_game,
                "win_loss": record.win_loss,
                "period": record.period,
                "minutes_played": record.minutes_played,
                "field_goals_made": record.field_goals_made,
                "field_goals_attempted": record.field_goals_attempted,
                "field_goal_percentage": record.field_goal_percentage,
                "three_point_field_goals_made": record.three_point_field_goals_made,
                "three_point_field_goals_attempted": record.three_point_field_goals_attempted,
                "three_point_field_goal_percentage": record.three_point_field_goal_percentage,
                "free_throws_made": record.free_throws_made,
                "free_throws_attempted": record.free_throws_attempted,
                "free_throw_percentage": record.free_throw_percentage,
                "offensive_rebounds": record.offensive_rebounds,
                "defensive_rebounds": record.defensive_rebounds,
                "rebounds": record.rebounds,
                "assists": record.assists,
                "steals": record.steals,
                "blocks": record.blocks,
                "block_attempts": record.block_attempts,
                "turnovers": record.turnovers,
                "personal_fouls": record.personal_fouls,
                "personal_fouls_drawn": record.personal_fouls_drawn,
                "points": record.points,
                "plus_minus": record.plus_minus,
                "nba_fantasy_points": record.nba_fantasy_points,
            }
            for record in query
        ]

        # Load the list of dictionaries into a pandas DataFrame
        cls.player_box_scores_traditional = pd.DataFrame(data)

    @classmethod
    def update_team_box_scores(cls):
        pass

    @classmethod
    def update_player_box_scores(cls):
        pass

    @staticmethod
    def get_team_id(team_name=None, abbr=None) -> int:
        """
        Get ID of team with given name or abbreviation.

        Args:
            team_name (str) - name of team
            abbr (str) - 3 letter team abbreviation e.g. LAL, GSW, BOS

        Returns:
            (int) id of team
        """
        if team_name:
            team = Team.query.filter_by(name=team_name).first()
            return team.id

        if abbr:
            team = Team.query.filter_by(abbreviation=abbr).first()
            return team.id

    @staticmethod
    def get_player_ids(player_name: str, active=True) -> list[int]:
        """
        Method to get ID of player with given name. If no exact match, we select player with the
        closest name calculated via Levenshtein distance.

        Args:
            player_name (str) - name of player
            active (bool) - if this player is currently on a team roster

        Returns:
            (list[int]) - list containing ids of players with given name
        """
        # Get all players that match the full name exactly
        if active:
            players = (
                db.session.query(Player)
                .filter_by(full_name=player_name, on_roster=True)
                .all()
            )
        else:
            players = db.session.query(Player).filter_by(full_name=player_name).all()

        if len(players) == 1:
            return [players[0].id]

        if len(players) > 1:
            return [
                player.id for player in players
            ]  # more than one player with given name

        # If no exact match, find the closest player using Levenshtein distance
        if active:
            all_players = (
                db.session.query(Player.id, Player.full_name)
                .filter(Player.on_roster == True)
                .all()
            )
        else:
            all_players = db.session.query(Player.id, Player.full_name).all()

        closest_player = min(
            all_players, key=lambda p: Levenshtein.distance(player_name, p.full_name)
        )
        return [closest_player[0]]

    @staticmethod
    def get_player_team_id(player_id: int) -> int:
        player = db.session.query(Player).filter_by(id=player_id).first()
        return player.team_id

    @classmethod
    def calculate_last_n_games_hit_rate_stats(
        cls, player_id: int, market_stats: dict, line: float, n: int
    ) -> dict:
        """
        Method to calculate hit rate of a player prop over last n games.

        Args:
            player_id (int) - id of player
            market_stats (dict) - contains stat categories relevant to market
            line (float) - threshold
            n (int) - last n games

        Returns:
            (dict) - containing number of times the player has hit this line in the last n games,
                as well as average; None if player has not played n games.
        """
        player_games_df = cls.player_box_scores_traditional[
            (cls.player_box_scores_traditional["player_id"] == player_id)
            & (cls.player_box_scores_traditional["period"] == 0)
        ]

        # Sort by game_date descending and select the last n games
        player_games_df = player_games_df.sort_values(
            by="game_date", ascending=False
        ).head(n)

        # If the player has played fewer than n games, return None
        if len(player_games_df) < n:
            return {"hits": None, "average": None}

        hits = 0
        totals_list = []

        # Iterate over the filtered games to calculate totals
        for _, game in player_games_df.iterrows():
            total = 0

            # Loop over market_stats (key = period, value = list of stat categories)
            for period, stat_categories in market_stats:
                if period == 0:
                    # Add the stats for the full game (period 0)
                    for stat in stat_categories:
                        total += game[stat]
                else:
                    # Add the stats for specific periods
                    period_box_score = cls.player_box_scores_traditional[
                        (cls.player_box_scores_traditional["player_id"] == player_id)
                        & (
                            cls.player_box_scores_traditional["game_id"]
                            == game["game_id"]
                        )
                        & (cls.player_box_scores_traditional["period"] == period)
                    ]

                    if not period_box_score.empty:
                        for stat in stat_categories:
                            total += period_box_score.iloc[0][stat]

            totals_list.append(total)

            # Check if the outcome matches
            if total > line:
                hits += 1

        return {"hits": hits, "average": mean(totals_list)}

    @classmethod
    def calculate_h2h_hit_rate_stats(
        cls,
        player_id: int,
        market_stats: dict,
        line: float,
        opponent_team_id: int,
    ) -> dict:
        """
        Calculate hit rate of a player prop against a particular opponent team using pandas DataFrame.

        Args:
            player_id (int) - id of player
            market_stats (dict) - contains stat categories relevant to market
            line (float) - threshold
            opponent_team_id (int) - id of opponent team

        Returns:
            (dict) - containing number of times the player has hit this line against opponent,
                     as well as the average; None if the player has not played any games against the opponent.
        """
        # Filter DataFrame for games against the specific opponent where period == 0 (full game stats)
        h2h_games_df = cls.player_box_scores_traditional[
            (cls.player_box_scores_traditional["player_id"] == player_id)
            & (
                cls.player_box_scores_traditional["opponent_team_id"]
                == opponent_team_id
            )
            & (cls.player_box_scores_traditional["period"] == 0)
        ].sort_values(by="game_date", ascending=False)

        # If there are no games, return the appropriate values
        if h2h_games_df.empty:
            return {"games": 0, "hits": None, "average": None}

        hits = 0
        totals_list = []

        # Iterate over the filtered games to calculate totals
        for _, game in h2h_games_df.iterrows():
            total = 0

            # Loop through each period and stat category in market_stats
            for period, stat_categories in market_stats:
                if period == 0:
                    # For the full game (period 0), add the stats from the game row
                    for stat in stat_categories:
                        total += game[stat]
                else:
                    # For specific periods, filter the DataFrame for the same game and period
                    period_box_score = cls.player_box_scores_traditional[
                        (cls.player_box_scores_traditional["player_id"] == player_id)
                        & (
                            cls.player_box_scores_traditional["game_id"]
                            == game["game_id"]
                        )
                        & (cls.player_box_scores_traditional["period"] == period)
                    ]

                    if not period_box_score.empty:
                        for stat in stat_categories:
                            total += period_box_score.iloc[0][stat]

            totals_list.append(total)

            if total > line:
                hits += 1

        return {"games": len(h2h_games_df), "hits": hits, "average": mean(totals_list)}

    @classmethod
    def calculate_season_hit_rate_stats(
        cls,
        player_id: int,
        market_stats: dict,
        line: float,
    ) -> dict:
        """
        Calculate hit rate of a player prop for the current season using pandas DataFrame.

        Args:
            player_id (int) - id of player
            market_stats (dict) - contains stat categories relevant to market
            line (float) - threshold

        Returns:
            (dict) - containing number of times the player has hit this line this season,
                     as well as the average; None if the player has not played any games.
        """
        # Filter DataFrame for games in the current season (period = 0 for full-game stats)
        season_games_df = cls.player_box_scores_traditional[
            (cls.player_box_scores_traditional["player_id"] == player_id)
            & (cls.player_box_scores_traditional["season_year"] == cls.current_season)
            & (cls.player_box_scores_traditional["period"] == 0)
        ].sort_values(by="game_date", ascending=False)

        # If no games are found for the player this season, return appropriate values
        if season_games_df.empty:
            return {"games": 0, "hits": None, "average": None}

        hits = 0
        totals_list = []

        # Iterate through the filtered games to calculate totals
        for _, game in season_games_df.iterrows():
            total = 0

            # Loop through the periods and stat categories in market_stats
            for period, stat_categories in market_stats:
                if period == 0:
                    # For full game (period = 0), directly sum the relevant stats
                    for stat in stat_categories:
                        total += game[stat]
                else:
                    # For specific periods, filter DataFrame for the same game and period
                    period_box_score = cls.player_box_scores_traditional[
                        (cls.player_box_scores_traditional["player_id"] == player_id)
                        & (
                            cls.player_box_scores_traditional["game_id"]
                            == game["game_id"]
                        )
                        & (cls.player_box_scores_traditional["period"] == period)
                    ]

                    if not period_box_score.empty:
                        for stat in stat_categories:
                            total += period_box_score.iloc[0][stat]

            totals_list.append(total)

            # Check if the total exceeds or is below the line based on the outcome (Over/Under)
            if total > line:
                hits += 1

        return {
            "games": len(season_games_df),
            "hits": hits,
            "average": mean(totals_list),
        }

    @classmethod
    def calculate_hot_streak(
        cls,
        player_id: int,
        market_stats: dict,
        line: float,
    ) -> int | None:
        """
        Calculate hot streak of a player prop using pandas DataFrame.

        Args:
            player_id (int) - id of player
            market_stats (dict) - contains stat categories relevant to market
            line (float) - threshold

        Returns:
            (int) - the hot streak, or None if no games played
        """
        # Filter the DataFrame for the player's games where period == 0 (full game stats)
        games_df = cls.player_box_scores_traditional[
            (cls.player_box_scores_traditional["player_id"] == player_id)
            & (cls.player_box_scores_traditional["period"] == 0)
        ].sort_values(by="game_date", ascending=False)

        # If no games are found, return None
        if games_df.empty:
            return None

        hot_streak = 0

        # Iterate through the filtered games to calculate totals and check streak
        for _, game in games_df.iterrows():
            total = 0

            # Loop through the periods and stat categories in market_stats
            for period, stat_categories in market_stats:
                if period == 0:
                    # For the full game, sum the relevant stats
                    for stat in stat_categories:
                        total += game[stat]
                else:
                    # For specific periods, filter the DataFrame for the same game and period
                    period_box_score = cls.player_box_scores_traditional[
                        (cls.player_box_scores_traditional["player_id"] == player_id)
                        & (
                            cls.player_box_scores_traditional["game_id"]
                            == game["game_id"]
                        )
                        & (cls.player_box_scores_traditional["period"] == period)
                    ]

                    if not period_box_score.empty:
                        for stat in stat_categories:
                            total += period_box_score.iloc[0][stat]

            # Check if the total is over or under the line, and update the streak
            if total > line:
                hot_streak += 1
            else:
                break  # Streak is broken

        return hot_streak

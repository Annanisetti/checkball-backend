# routes.py
from datetime import datetime

import pytz
from flask import Blueprint, render_template, request, current_app, jsonify
from sqlalchemy import func, and_
from sqlalchemy.orm import aliased

from app.models.nba_models import *
from app.models.odds_api_models import *
from app.services.nba_stats_api_service import NBAStatsAPIService
from app.services.prizepicks_api_service import PrizePicksAPIService
from app.services.the_odds_api_service import TheOddsAPIService


main = Blueprint("main", __name__)

MARKET_KEY_STATS_MAPPING = {
    "player_points": "PTS",
    "player_points_q1": "Q1 PTS",
    "player_rebounds": "REB",
    "player_rebounds_q1": "Q1 REB",
    "player_assists": "AST",
    "player_assists_q1": "Q1 AST",
    "player_threes": "3PM",
    "player_blocks": "BLK",
    "player_steals": "STL",
    "player_blocks_steals": "BLK+STL",
    "player_turnovers": "TO",
    "player_points_rebounds_assists": "PTS+REB+AST",
    "player_points_rebounds": "PTS+REB",
    "player_points_assists": "PTS+AST",
    "player_rebounds_assists": "REB+AST",
    "player_field_goals": "FGM",
    "player_frees_made": "FTM",
    "player_frees_attempts": "FTA",
    "player_points_alternate": "ALT PTS",
    "player_rebounds_alternate": "ALT REB",
    "player_assists_alternate": "ALT AST",
    "player_blocks_alternate": "ALT BLK",
    "player_steals_alternate": "ALT STL",
    "player_turnovers_alternate": "ALT TO",
    "player_threes_alternate": "ALT 3PM",
    "player_points_assists_alternate": "ALT PTS+AST",
    "player_points_rebounds_alternate": "ALT PTS+REB",
    "player_rebounds_assists_alternate": "ALT REB+AST",
    "player_points_rebounds_assists_alternate": "ALT PTS+REB+AST",
    "1H Points": "1H PTS",
    "1H Pts+Rebs+Asts": "1H PTS+REB+AST",
    "1H Fantasy Score": "1H FPTS",
}



@main.route("/")
def home():
    return render_template("home.html")

@main.route("/test")
def test():
    NBAStatsAPIService.load_player_tracking_box_scores()


@main.route("/nba-player-props")
def nba_player_props():
    setup = False
    if setup:
        NBAStatsAPIService.load_teams()
        NBAStatsAPIService.load_players()
        NBAStatsAPIService.load_player_box_scores()
        #
        print("Finished loading nba stuff")
        odds_api_key = current_app.config["ODDS_API_KEY"]

        NBAStatsAPIService.initialize_box_scores_df()

        TheOddsAPIService.load_bookmakers()
        TheOddsAPIService.load_events_and_odds(odds_api_key)
        TheOddsAPIService.load_player_props_and_odds(odds_api_key)

    # Get the selected game from query parameters
    selected_game_id = request.args.get('game_id')
    away_team = aliased(Team)

    
    # Get all available games for the dropdown
    available_games = (
        db.session.query(
            TheOddsAPIEvent.id,
            Team.abbreviation.label("home_team_abbr"),
            away_team.abbreviation.label("away_team_abbr"),
            TheOddsAPIEvent.formatted_start_time
        )
        .join(Team, Team.id == TheOddsAPIEvent.home_team_id)
        .join(away_team, away_team.id == TheOddsAPIEvent.away_team_id)
        .order_by(TheOddsAPIEvent.formatted_start_time)
        .all()
    )

    prizepicks_bookmaker_key = "prizepicks"

    # Base query
    query = (
        db.session.query(
            PlayerProp,
            TheOddsAPIEvent,
            Player,
            Team.abbreviation.label("home_team_abbr"),
            away_team.abbreviation.label("away_team_abbr"),
        )
        .join(Player, PlayerProp.player_id == Player.id)
        .join(TheOddsAPIEvent, TheOddsAPIEvent.id == PlayerProp.event_id)
        .join(Team, Team.id == TheOddsAPIEvent.home_team_id)
        .join(away_team, away_team.id == TheOddsAPIEvent.away_team_id)
        .join(PlayerPropOdds, PlayerProp.id == PlayerPropOdds.player_prop_id)
        .filter(PlayerPropOdds.bookmaker_key == prizepicks_bookmaker_key)
    )

    # Add game filter if a game is selected
    if selected_game_id:
        query = query.filter(TheOddsAPIEvent.id == selected_game_id)

    # Order by hot streak
    query = query.order_by(PlayerProp.hot_streak.desc())
    
    prop_data = query.all()

    # If no props are found
    if not prop_data:
        return jsonify({"error": "No player props found"}), 404

    # Render the template and pass player props, market mapping, and available games
    return render_template(
        "nba_player_props.html",
        player_props=prop_data,
        market_key_stats_mapping=MARKET_KEY_STATS_MAPPING,
        available_games=available_games,
        selected_game_id=selected_game_id,
        int=int,
    )

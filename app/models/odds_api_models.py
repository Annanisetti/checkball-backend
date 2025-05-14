# odds_api_models.py

from app.extensions import db


class Bookmaker(db.Model):
    key = db.Column(db.String, primary_key=True)
    region = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    link = db.Column(db.String, nullable=False)
    image_path = db.Column(db.String, nullable=False)


class TheOddsAPIEvent(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    formatted_start_time = db.Column(db.String, nullable=False)
    home_team_id = db.Column(db.Integer, nullable=False)
    away_team_id = db.Column(db.Integer, nullable=False)


class MoneylineOdds(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(
        db.String(32), db.ForeignKey("the_odds_api_event.id"), nullable=False
    )
    bookmaker_key = db.Column(db.String, db.ForeignKey("bookmaker.key"), nullable=False)
    home_team_odds = db.Column(db.Integer, nullable=False)
    away_team_odds = db.Column(db.Integer, nullable=False)


class PointsSpreadOdds(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(
        db.String(32), db.ForeignKey("the_odds_api_event.id"), nullable=False
    )
    bookmaker_key = db.Column(db.String, db.ForeignKey("bookmaker.key"), nullable=False)
    home_team_line = db.Column(db.Float, nullable=False)
    home_team_odds = db.Column(db.Integer, nullable=False)
    away_team_line = db.Column(db.Float, nullable=False)
    away_team_odds = db.Column(db.Integer, nullable=False)


class TotalPointsOdds(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(
        db.String(32), db.ForeignKey("the_odds_api_event.id"), nullable=False
    )
    bookmaker_key = db.Column(db.String, db.ForeignKey("bookmaker.key"), nullable=False)
    line = db.Column(db.Float, nullable=False)
    over_odds = db.Column(db.Integer, nullable=False)
    under_odds = db.Column(db.Integer, nullable=False)


class PlayerProp(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    event_id = db.Column(
        db.String(32), db.ForeignKey("the_odds_api_event.id"), nullable=False
    )
    player_id = db.Column(db.Integer, db.ForeignKey("player.id"), nullable=False)
    opponent_team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)
    market = db.Column(db.String, nullable=False)
    line = db.Column(db.Float, nullable=False)
    alternate = db.Column(db.Boolean, nullable=False)
    last_five_games_hits = db.Column(db.Integer)
    last_five_games_hit_rate = db.Column(db.Float)
    last_five_games_average = db.Column(db.Float)
    last_ten_games_hits = db.Column(db.Integer)
    last_ten_games_hit_rate = db.Column(db.Float)
    last_ten_games_average = db.Column(db.Float)
    last_twenty_games_hits = db.Column(db.Integer)
    last_twenty_games_hit_rate = db.Column(db.Float)
    last_twenty_games_average = db.Column(db.Float)
    last_thirty_games_hits = db.Column(db.Integer)
    last_thirty_games_hit_rate = db.Column(db.Float)
    last_thirty_games_average = db.Column(db.Float)
    season_games = db.Column(db.Integer)
    season_hits = db.Column(db.Integer)
    season_hit_rate = db.Column(db.Float)
    season_average = db.Column(db.Float)
    head_to_head_matchups = db.Column(db.Integer)
    head_to_head_hits = db.Column(db.Integer)
    head_to_head_hit_rate = db.Column(db.Float)
    head_to_head_average = db.Column(db.Float)
    hot_streak = db.Column(db.Integer)


class PlayerPropOdds(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    player_prop_id = db.Column(
        db.String(32), db.ForeignKey("player_prop.id"), nullable=False
    )
    bookmaker_key = db.Column(db.String, db.ForeignKey("bookmaker.key"), nullable=False)
    outcome = db.Column(db.String, nullable=False)
    odds = db.Column(db.Integer, nullable=False)

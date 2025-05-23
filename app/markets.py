# markets.py

MARKET_STATS_MAPPING = {
    "player_points": [(0, ["points"])],
    "player_points_q1": [(1, ["points"])],
    "player_rebounds": [(0, ["rebounds"])],
    "player_rebounds_q1": [(1, ["rebounds"])],
    "player_assists": [(0, ["assists"])],
    "player_assists_q1": [(1, ["assists"])],
    "player_threes": [(0, ["three_point_field_goals_made"])],
    "player_blocks": [(0, ["blocks"])],
    "player_steals": [(0, ["steals"])],
    "player_blocks_steals": [(0, ["blocks", "steals"])],
    "player_turnovers": [(0, ["turnovers"])],
    "player_points_rebounds_assists": [(0, ["points", "rebounds", "assists"])],
    "player_points_rebounds": [(0, ["points", "rebounds"])],
    "player_points_assists": [(0, ["points", "assists"])],
    "player_rebounds_assists": [(0, ["rebounds", "assists"])],
    "player_field_goals": [(0, ["field_goals_made"])],
    "player_frees_made": [(0, ["free_throws_made"])],
    "player_frees_attempts": [(0, ["free_throws_attempted"])],
    "player_points_alternate": [(0, ["points"])],
    "player_rebounds_alternate": [(0, ["rebounds"])],
    "player_assists_alternate": [(0, ["assists"])],
    "player_blocks_alternate": [(0, ["blocks"])],
    "player_steals_alternate": [(0, ["steals"])],
    "player_turnovers_alternate": [(0, ["turnovers"])],
    "player_threes_alternate": [(0, ["three_point_field_goals_made"])],
    "player_points_assists_alternate": [(0, ["points", "assists"])],
    "player_points_rebounds_alternate": [(0, ["points", "rebounds"])],
    "player_rebounds_assists_alternate": [(0, ["rebounds", "assists"])],
    "player_points_rebounds_assists_alternate": [
        (0, ["points", "rebounds", "assists"])
    ],
    "1H Points": [(1, ["points"]), (2, ["points"])],
    "1H Pts+Rebs+Asts": [
        (1, ["points", "rebounds", "assists"]),
        (2, ["points", "rebounds", "assists"]),
    ],
    "1H Fantasy Score": [(1, ["nba_fantasy_points"]), (2, ["nba_fantasy_points"])],
}

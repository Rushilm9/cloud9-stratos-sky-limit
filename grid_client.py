import os
import requests
from dotenv import load_dotenv
from collections import defaultdict

# ==================================================
# CONFIGURATION & LOAD ENV
# ==================================================
load_dotenv()
GRID_API_KEY = os.getenv("GRID_API_KEY")

CENTRAL_DATA_URL = "https://api-op.grid.gg/central-data/graphql"
SERIES_STATE_URL = "https://api-op.grid.gg/live-data-feed/series-state/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": GRID_API_KEY
}


# ==================================================
# CORE POST HELPER
# ==================================================
def post(url, query, variables=None):
    try:
        response = requests.post(
            url,
            json={"query": query, "variables": variables},
            headers=HEADERS,
            timeout=60
        )
        response.raise_for_status()
        res_json = response.json()
        
        if "errors" in res_json:
            pass # Silent handling for production speed
            
        return res_json
    except Exception as e:
        return {"errors": [{"message": str(e)}]}

def ensure_data(res):
    if not res: return None
    return res.get("data")

# ==================================================
# 1️⃣ DISCOVERY & SCANNING
# ==================================================
def fetch_recent_tournaments(limit=50):
    """Fetches the most recent tournaments to scan for teams."""
    QUERY = """
    query GetRecentTournaments($limit: Int!) {
      tournaments(first: $limit) {
        edges {
          node { id name }
        }
      }
    }
    """
    res = post(CENTRAL_DATA_URL, QUERY, {"limit": min(limit, 50)})
    data = ensure_data(res)
    if not data: return []
    return [{"id": t["node"]["id"], "name": t["node"]["name"]} for t in data["tournaments"]["edges"]]

def fetch_tournaments_safe():
    """Stable tournament fetch for the UI browser."""
    return fetch_recent_tournaments(limit=50), None

def discover_teams_from_tournament_list(tournament_ids):
    """Fetches all teams competing in a provided list of tournament IDs."""
    if not tournament_ids: return []
    
    query = """
    query GetTeamsFromTournaments($tournamentIds: [ID!]) {
      allSeries(first: 50, filter: { tournament: { id: { in: $tournamentIds }, includeChildren: { equals: true } } }) {
        edges { 
          node { 
            teams { 
              baseInfo { id name } 
            } 
            tournament { name }
          } 
        } 
      }
    }
    """
    res = post(CENTRAL_DATA_URL, query, {"tournamentIds": [str(tid) for tid in tournament_ids]})
    data = ensure_data(res)
    if not data: return []
    
    teams = {} 
    for s in data["allSeries"]["edges"]:
        t_context = s["node"]["tournament"]["name"]
        if s["node"]["teams"]:
            for t in s["node"]["teams"]:
                if t.get("baseInfo"):
                    name = t["baseInfo"]["name"]
                    tid = t["baseInfo"]["id"]
                    if name not in teams:
                        teams[name] = {"id": tid, "tournaments": {t_context}}
                    else:
                        teams[name]["tournaments"].add(t_context)
    
    result = []
    for name, info in teams.items():
        tournaments_str = ", ".join(list(info["tournaments"])[:2])
        display_name = f"{name} ({tournaments_str}...)" if len(info["tournaments"]) > 2 else f"{name} ({tournaments_str})"
        result.append({
            "name": name, 
            "display": display_name,
            "id": info["id"]
        })
        
    return sorted(result, key=lambda x: x["name"])

def discover_teams_from_tournament(tournament_id):
    """Fetches all teams competing in a specific tournament ID."""
    query = """
    query GetTeams($tournamentId: [ID!]) {
      allSeries(first: 50, filter: { tournament: { id: { in: $tournamentId }, includeChildren: { equals: true } } }) {
        edges { 
          node { 
            teams { 
              baseInfo { id name } 
            } 
          } 
        } 
      }
    }
    """
    res = post(CENTRAL_DATA_URL, query, {"tournamentId": [str(tournament_id)]})
    data = ensure_data(res)
    if not data: return []
    
    teams = {} 
    for s in data["allSeries"]["edges"]:
        if s["node"]["teams"]:
            for t in s["node"]["teams"]:
                if t.get("baseInfo"):
                    teams[t["baseInfo"]["name"]] = t["baseInfo"]["id"]
    
    result = [{"name": name, "id": teams[name]} for name in sorted(list(teams.keys()))]
    return result

def fetch_series_info_for_team(team_id, tournament_id=None, limit=20):
    """Fetches series IDs and Tournament names for a team."""
    filter_vars = {
        "teamIds": { "in": [str(team_id)] },
        "types": "ESPORTS"
    }
    if tournament_id:
        filter_vars["tournament"] = { "id": { "in": [str(tournament_id)] }, "includeChildren": { "equals": True } }
        
    query = """
    query AllSeries($filter: SeriesFilter!, $limit: Int!) {
      allSeries(
        first: $limit, 
        filter: $filter, 
        orderBy: StartTimeScheduled, 
        orderDirection: DESC
      ) {
        edges { 
          node { 
            id 
            tournament { name }
            startTimeScheduled
          } 
        }
      }
    }
    """
    res = post(CENTRAL_DATA_URL, query, {
        "filter": filter_vars,
        "limit": limit
    })
    data = ensure_data(res)
    if not data: return []
    return [
        {
            "id": s["node"]["id"], 
            "tournament": s["node"]["tournament"]["name"],
            "date": s["node"]["startTimeScheduled"][:10] if s["node"]["startTimeScheduled"] else "Unknown"
        } 
        for s in data["allSeries"]["edges"]
    ]

# ==================================================
# 2️⃣ ENHANCED DATA COLLECTION
# ==================================================
QUERY_SERIES_STATE_DEEP = """
query SeriesState($seriesId: ID!) {
  seriesState(id: $seriesId) {
    version
    teams { name won }
    games {
      sequenceNumber
      map { name }
      teams {
        name won side score
        ... on GameTeamStateLol {
          kills deaths netWorth money
          players { name kills deaths killAssistsGiven netWorth }
        }
        ... on GameTeamStateCs2 {
          kills deaths netWorth money
          players { name kills deaths killAssistsGiven netWorth }
        }
        ... on GameTeamStateValorant {
          kills deaths netWorth money
          players { name kills deaths killAssistsGiven netWorth }
        }
        ... on GameTeamStateDefault {
          kills deaths netWorth
          players { name kills deaths killAssistsGiven netWorth }
        }
      }
    }
  }
}
"""

def collect_team_data(target_team_name, series_info_list, max_matches=10):
    collected = []
    player_data = defaultdict(lambda: {"k": 0, "d": 0, "a": 0, "nw": 0, "games": 0})
    tournament_stats = defaultdict(lambda: {"w": 0, "l": 0})
    losses = []
    wins = []
    
    for s_info in series_info_list[:max_matches]:
        sid = s_info["id"]
        t_name = s_info["tournament"]
        
        res = post(SERIES_STATE_URL, QUERY_SERIES_STATE_DEEP, {"seriesId": str(sid)})
        data = res.get("data")
        if not data or not data.get("seriesState"):
            continue
            
        state = data["seriesState"]
        
        matching_team = next((t for t in state["teams"] if target_team_name.lower() in t["name"].lower() or t["name"].lower() in target_team_name.lower()), None)
        
        if matching_team:
            actual_name = matching_team["name"]
            our_series_win = matching_team["won"]
            opponent = next((t["name"] for t in state["teams"] if t["name"] != actual_name), "Unknown")
            
            if our_series_win:
                tournament_stats[t_name]["w"] += 1
                wins.append({"opponent": opponent, "tournament": t_name})
            else:
                tournament_stats[t_name]["l"] += 1
                losses.append({"opponent": opponent, "tournament": t_name})

            summary = {
                "series_id": sid,
                "tournament": t_name,
                "opponent": opponent,
                "series_win": our_series_win,
                "date": s_info.get("date", "N/A"),
                "game_stats": [],
                "key_player": "N/A"
            }
            
            series_players = defaultdict(lambda: {"k": 0, "d": 0, "a": 0})
            
            for game in state.get("games", []):
                our_stat = next((t for t in game.get("teams", []) if t["name"] == actual_name), None)
                opp_stat = next((t for t in game.get("teams", []) if t["name"] != actual_name), None)
                
                if our_stat:
                    summary["game_stats"].append({
                        "map": game.get("map", {}).get("name", "Unknown") if game.get("map") else "Unknown",
                        "won": our_stat.get("won", False),
                        "side": our_stat.get("side", "Unknown"),
                        "score": f"{our_stat.get('score', 0)}-{opp_stat.get('score', 0) if opp_stat else 0}",
                        "kills": our_stat.get("kills"),
                        "deaths": our_stat.get("deaths"),
                        "net_worth": our_stat.get("netWorth")
                    })
                    
                    for p in our_stat.get("players", []):
                        p_name = p.get("name")
                        if p_name:
                            player_data[p_name]["k"] += (p.get("kills") or 0)
                            player_data[p_name]["d"] += (p.get("deaths") or 0)
                            player_data[p_name]["a"] += (p.get("killAssistsGiven") or 0)
                            player_data[p_name]["nw"] += (p.get("netWorth") or 0)
                            player_data[p_name]["games"] += 1
                            series_players[p_name]["k"] += (p.get("kills") or 0)
                            series_players[p_name]["d"] += (p.get("deaths") or 0)
                            series_players[p_name]["a"] += (p.get("killAssistsGiven") or 0)
            
            if series_players:
                best_p = max(series_players.keys(), key=lambda p: (series_players[p]["k"] + series_players[p]["a"]) / (series_players[p]["d"] if series_players[p]["d"] > 0 else 1))
                summary["key_player"] = best_p
            
            collected.append(summary)
    
    refined_players = []
    for p, s in player_data.items():
        if s["games"] > 0:
            kda = round((s["k"] + s["a"]) / s["d"] if s["d"] > 0 else (s["k"] + s["a"]), 2)
            avg_kills = round(s["k"] / s["games"], 2)
            avg_deaths = round(s["d"] / s["games"], 2)
            
            refined_players.append({
                "name": p,
                "avg_kda": kda,
                "avg_kills": avg_kills,
                "avg_deaths": avg_deaths,
                "avg_networth": int(s["nw"] / s["games"]),
                "participation": s["games"]
            })
    
    top_players = sorted(refined_players, key=lambda x: x["avg_kda"], reverse=True)[:5]
    for p in top_players:
        p["impact_score"] = round((p["avg_kda"] * 5) + (p["avg_networth"] / 2000), 1)
        
    map_wins = sum(1 for s in collected for g in s["game_stats"] if g["won"])
    total_maps = sum(len(s["game_stats"]) for s in collected)

    return {
        "series": collected,
        "top_players": top_players,
        "losses": losses,
        "wins": wins,
        "tournament_summary": dict(tournament_stats),
        "total_series": len(collected),
        "map_win_rate": round((map_wins/total_maps)*100, 1) if total_maps > 0 else 0,
        "total_maps": total_maps
    }

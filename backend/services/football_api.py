import requests


class RateLimitError(Exception):
    pass


class FootballAPI:
    BASE_URL = "https://v3.football.api-sports.io"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {"x-apisports-key": api_key}

    def _get(self, path: str, params: dict) -> dict:
        response = requests.get(
            f"{self.BASE_URL}{path}",
            headers=self.headers,
            params=params,
        )
        data = response.json()

        errors = data.get("errors", {})
        if isinstance(errors, dict):
            if errors.get("ratelimit"):
                raise RateLimitError("API-Football rate limit reached")
            if errors.get("plan"):
                raise RateLimitError(f"API-Football plan restriction: {errors['plan']}")

        return data

    def search_teams(self, query: str) -> list[dict]:
        data = self._get("/teams", {"search": query})
        return [
            {
                "id":   item["team"]["id"],
                "name": item["team"]["name"],
                "logo": item["team"]["logo"],
            }
            for item in data.get("response", [])
        ]

    def get_team_fixtures(self, team_id: int, season: int = 2024) -> list[dict]:
        data = self._get("/fixtures", {"team": team_id, "season": season})
        fixtures = [
            {
                "fixture_id": item["fixture"]["id"],
                "date":       item["fixture"]["date"],
                "home_team":  item["teams"]["home"]["name"],
                "away_team":  item["teams"]["away"]["name"],
            }
            for item in data.get("response", [])
        ]
        fixtures.sort(key=lambda x: x["date"])
        return fixtures[-10:]

    def get_fixture_lineups(self, fixture_id: int) -> list[dict]:
        data = self._get("/fixtures/lineups", {"fixture": fixture_id})
        lineups = data.get("response", [])

        if lineups:
            return self._normalize_lineups(lineups)

        # Lineups not published yet — fall back to full squad rosters
        fixture_data = self._get("/fixtures", {"id": fixture_id})
        fixture_resp = fixture_data.get("response", [])
        if not fixture_resp:
            return []

        teams = fixture_resp[0]["teams"]
        home_id = teams["home"]["id"]
        away_id = teams["away"]["id"]

        players = []
        for team_id, side in [(home_id, "home"), (away_id, "away")]:
            squad_data = self._get("/players/squads", {"team": team_id})
            squad_resp = squad_data.get("response", [])
            if not squad_resp:
                continue
            for player in squad_resp[0].get("players", []):
                number = player.get("number")
                name = player.get("name")
                if number and name:
                    players.append({
                        "number": int(number),
                        "name":   str(name).strip(),
                        "side":   side,
                    })
        return players

    def _normalize_lineups(self, lineups: list) -> list[dict]:
        players = []
        for team_entry in lineups:
            side = "home" if team_entry.get("team", {}).get("id") == lineups[0]["team"]["id"] else "away"
            for player in team_entry.get("startXI", []):
                p = player.get("player", {})
                if p.get("number") and p.get("name"):
                    players.append({
                        "number": int(p["number"]),
                        "name":   str(p["name"]).strip(),
                        "side":   side,
                    })
        return players

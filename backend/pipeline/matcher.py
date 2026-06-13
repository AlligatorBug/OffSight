# matcher.py: what's their name?
# provide a csv file matching name to number

import pandas as pd
import requests


class PlayerMatcher:
    def __init__(self):
        """
        Initializes the PlayerMatcher with an empty lookup table.
        Populate it by calling either:
            - load_from_csv()   for manual squad CSV uploads
            - load_from_api()   for automatic squad fetching (coming soon)
        """
        # { jersey_number: player_name }
        # e.g. { 10: "Lionel Messi", 7: "Cristiano Ronaldo" }
        self.squad = {}

    def load_from_csv(self, csv_path: str):
        """
        Loads squad data from a CSV file uploaded by the user.

        Expected CSV format:
            number, name, position, team
            10, Lionel Messi, Forward, Home
            7, Cristiano Ronaldo, Forward, Away

        Args:
            csv_path: Path to the squad CSV file.
        """
        df = pd.read_csv(csv_path)

        # Normalize column names — strip whitespace, lowercase
        df.columns = df.columns.str.strip().str.lower()

        if "number" not in df.columns or "name" not in df.columns:
            raise ValueError("CSV must have 'number' and 'name' columns.")

        # Build the lookup table
        self.squad = {
            int(row["number"]): str(row["name"]).strip()
            for _, row in df.iterrows()
        }

        print(f"Loaded {len(self.squad)} players from CSV.")
        print(self.squad)

    def load_from_api(self, home_team_id: int, away_team_id: int, api_key: str):
        """
        Fetches squad data automatically from API-Football.
        Replaces the need for a manual CSV upload.

        Args:
            home_team_id: API-Football team ID for the home side.
            away_team_id: API-Football team ID for the away side.
            api_key:      Your API-Football key.
        """
        self.squad = {}

        for team_id in [home_team_id, away_team_id]:
            url = "https://v3.football.api-sports.io/players/squads"
            headers = {"x-apisports-key": api_key}
            params  = {"team": team_id}

            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            if not data.get("response"):
                print(f"No data returned for team ID {team_id}")
                continue

            players = data["response"][0]["players"]

            for player in players:
                number = player.get("number")
                name   = player.get("name")

                if number and name:
                    self.squad[int(number)] = str(name).strip()

        print(f"Loaded {len(self.squad)} players from API.")
        print(self.squad)

    def get_name(self, jersey_number):
        """
        Looks up a player's name by their jersey number.

        Args:
            jersey_number: Integer jersey number read by OCR.

        Returns:
            Player name as a string, or None if not found.
        """
        if jersey_number is None:
            return None

        return self.squad.get(int(jersey_number), None)

    def match_frame(self, confirmed_numbers: dict):
        """
        Maps a full frame's worth of confirmed jersey numbers to player names.

        Args:
            confirmed_numbers: Dict from ocr.py mapping tracker_id → jersey number
                               e.g. { 1: 10, 2: 7, 3: None }

        Returns:
            Dict mapping tracker_id → player name (or None)
                               e.g. { 1: "Messi", 2: "Ronaldo", 3: None }
        """
        return {
            tracker_id: self.get_name(number)
            for tracker_id, number in confirmed_numbers.items()
        }


if __name__ == "__main__":
    # Test with a CSV
    matcher = PlayerMatcher()

    matcher.load_from_csv("../../data/squads/test_squad.csv")

    # Simulate what OCR would return
    confirmed_numbers = {1: 10, 2: 7, 3: 9, 4: None}

    matched_names = matcher.match_frame(confirmed_numbers)

    print("\nMatched names:")
    for tracker_id, name in matched_names.items():
        print(f"  Player ID {tracker_id} → {name if name else 'Unknown'}")
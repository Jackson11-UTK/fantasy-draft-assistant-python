import requests
import pandas as pd


BASE_URL = (
    "https://lm-api-reads.fantasy.espn.com/"
    "apis/v3/games/ffl/seasons/2026/segments/0/leaguedefaults/1"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "x-fantasy-filter": (
        '{"players":{"filterSlotIds":{"value":[0,2,4,6,16,17]},'
        '"limit":500,"sortDraftRanks":{"sortPriority":100,'
        '"sortAsc":true,"value":"PPR"}}}'
    )
}


def main():
    response = requests.get(
        BASE_URL,
        headers=HEADERS,
        params={"view": "kona_player_info"},
        timeout=30,
    )

    print("Status:", response.status_code)

    response.raise_for_status()

    data = response.json()

    players = data.get("players", [])

    print("Players returned:", len(players))

    rows = []

    for item in players:
        player = item.get("player", {})

        rows.append({
            "espn_id": player.get("id"),
            "player": player.get("fullName"),
            "team_id": player.get("proTeamId"),
            "position_id": player.get("defaultPositionId"),
            "ownership_adp": (
                player
                .get("ownership", {})
                .get("averageDraftPosition")
            ),
        })

    df = pd.DataFrame(rows)

    print("\nFIRST 25:")
    print(df.head(25))

    print("\nADP NON-MISSING:")
    print(df["ownership_adp"].notna().sum())

    df.to_csv(
        "data/raw/espn_adp_2026.csv",
        index=False
    )


if __name__ == "__main__":
    main()
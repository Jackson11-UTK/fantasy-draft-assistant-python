from pathlib import Path

from src.data_sources import (
    fetch_projections,
    save_json,
)


RAW_DIR = Path("data/raw")


def main():

    positions = ["QB", "RB", "WR", "TE"]

    for position in positions:

        print(f"\nPulling {position} projections...")

        data = fetch_projections(position)

        print("Season:", data.get("season"))
        print("Position:", data.get("positions"))
        print("Reported count:", data.get("count"))

        players = data.get("players", [])

        print("Players actually returned:", len(players))

        if players:
            print("First player:", players[0].get("name"))

            stats = players[0].get("stats", {})

            if stats:
                print(
                    "Available stats:",
                    list(stats.keys())
                )

        save_json(
            data,
            RAW_DIR / f"fantasypros_{position.lower()}_projections.json"
        )

    print("\n---------------------------")
    print("DATA PULL COMPLETE")
    print("---------------------------")


if __name__ == "__main__":
    main()
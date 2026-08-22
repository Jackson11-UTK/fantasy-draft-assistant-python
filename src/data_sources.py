import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

BASE_URL = "https://api.fantasypros.com/public/v2/json"
API_KEY = os.getenv("FANTASYPROS_API_KEY")


def get_headers():
    if not API_KEY:
        raise RuntimeError(
            "FantasyPros API key not found in .env"
        )

    return {
        "x-api-key": API_KEY
    }


def fetch_projections(position):
    url = f"{BASE_URL}/nfl/2026/projections"

    params = {
        "position": position,
        "week": 0
    }

    response = requests.get(
        url,
        headers=get_headers(),
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def save_json(data, filepath):
    filepath = Path(filepath)

    filepath.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
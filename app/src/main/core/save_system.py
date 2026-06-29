"""
Save/load system for persistent game progress.

Stores coins, upgrades and high score in a JSON file.
When loading, if the file is missing or invalid, default values are returned.
"""

# @generated [partially] ChatGPT : how to save/load json to/from files

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any

SAVE_FILE = Path(__file__).resolve().parent.parent.parent.parent / "runner_save.json"

_DEFAULT_DATA: dict[str, Any] = {
    "coins_bank": 0,
    "upgrades": {
        "shield_duration_level": 0,
    },
    "high_score": 0,
}


def _default_data() -> dict[str, Any]:
    """Return a fresh copy of default save data."""
    return {
        "coins_bank": _DEFAULT_DATA["coins_bank"],
        "high_score": _DEFAULT_DATA["high_score"],
        "upgrades": dict(_DEFAULT_DATA["upgrades"]),
    }


def load_save(filename: Path = SAVE_FILE) -> dict[str, Any]:
    """
    Load saved game data from a JSON file.

    If the file does not exist, is invalid, or contains incorrect data,
    default values are returned instead.
    """
    if not filename.exists():
        return _default_data()

    try:
        raw = filename.read_text(encoding="utf8")
        file_data = json.loads(raw)
    except (OSError, JSONDecodeError, UnicodeDecodeError):
        return _default_data()

    data = _default_data()

    if not isinstance(file_data, dict):
        return data

    if "coins_bank" in file_data:
        try:
            data["coins_bank"] = int(file_data["coins_bank"])
        except (TypeError, ValueError):
            pass

    file_upgrades = file_data.get("upgrades")
    if isinstance(file_upgrades, dict):
        data["upgrades"].update(file_upgrades)

    if "high_score" in file_data:
        try:
            data["high_score"] = int(file_data["high_score"])
        except (TypeError, ValueError):
            pass

    return data


def save_game(
    coins_bank: int,
    upgrades: dict[str, Any],
    high_score: int,
    filename: Path = SAVE_FILE,
) -> None:
    """
    Save current game progress to a JSON file.

    Errors during saving are ignored.
    """
    data = {
        "coins_bank": int(coins_bank),
        "upgrades": dict(upgrades),
        "high_score": int(high_score),
    }

    try:
        filename.write_text(json.dumps(data), encoding="utf8")
    except OSError:
        pass

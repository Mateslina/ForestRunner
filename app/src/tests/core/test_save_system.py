# @generated [all] ChatGPT : generate tests based on class implementation
import json
from pathlib import Path

import pytest

from main.core.save_system import load_save, save_game, _default_data


# ---------------- default data ----------------

def test_default_data_returns_fresh_copy():
    d1 = _default_data()
    d2 = _default_data()

    d1["upgrades"]["shield_duration_level"] = 999
    assert d2["upgrades"]["shield_duration_level"] == 0


# ---------------- load_save ----------------

def test_load_save_returns_default_if_file_missing(tmp_path: Path):
    data = load_save(tmp_path / "missing.json")
    assert data == _default_data()


@pytest.mark.parametrize(
    "content",
    [
        "",       # empty
        "{",      # broken json
        "[]",     # wrong root type
        "123",    # wrong root type
        '"abc"',  # wrong root type
    ],
)
def test_load_save_returns_default_on_invalid_or_wrong_root(save_file: Path, content: str):
    save_file.write_text(content, encoding="utf8")
    data = load_save(save_file)
    assert data == _default_data()


def test_load_save_parses_int_fields_if_possible(save_file: Path):
    save_file.write_text(
        json.dumps({
            "coins_bank": "12",
            "high_score": 34.0,
            "upgrades": {"shield_duration_level": 2},
        }),
        encoding="utf8",
    )

    data = load_save(save_file)
    assert data["coins_bank"] == 12
    assert data["high_score"] == 34
    assert data["upgrades"]["shield_duration_level"] == 2


def test_load_save_ignores_bad_int_fields(save_file: Path):
    save_file.write_text(
        json.dumps({
            "coins_bank": "nope",
            "high_score": None,
            "upgrades": {"shield_duration_level": 5},
        }),
        encoding="utf8",
    )

    data = load_save(save_file)
    defaults = _default_data()

    assert data["coins_bank"] == defaults["coins_bank"]
    assert data["high_score"] == defaults["high_score"]
    assert data["upgrades"]["shield_duration_level"] == 5


def test_load_save_ignores_upgrades_if_not_dict(save_file: Path):
    save_file.write_text(
        json.dumps({
            "coins_bank": 1,
            "high_score": 2,
            "upgrades": ["not", "a", "dict"],
        }),
        encoding="utf8",
    )

    data = load_save(save_file)
    assert data["coins_bank"] == 1
    assert data["high_score"] == 2
    assert data["upgrades"] == _default_data()["upgrades"]


# ---------------- save_game ----------------

def test_save_game_writes_valid_json(save_file: Path):
    save_game(
        coins_bank=10,
        upgrades={"shield_duration_level": 3},
        high_score=999,
        filename=save_file,
    )

    loaded = json.loads(save_file.read_text(encoding="utf8"))
    assert loaded == {
        "coins_bank": 10,
        "upgrades": {"shield_duration_level": 3},
        "high_score": 999,
    }


def test_save_game_ignores_write_errors(monkeypatch, save_file: Path):
    def boom(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(Path, "write_text", boom)

    # should not raise
    save_game(1, {"shield_duration_level": 0}, 2, filename=save_file)

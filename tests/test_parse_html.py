from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from backend.services.scraper import SteamScraper  # noqa: E402

HTML_DIR = Path(__file__).parent / "data_html"


def _read(name: str) -> str:
    return (HTML_DIR / name).read_text(encoding="utf-8")


# --- tests --------------------------------------------------------------
def test_parse_price_meta() -> None:
    html = _read("1145360.html")
    game = SteamScraper._parse_game(html, 1145360)
    assert game.price == "24.50 EUR"
    assert game.metascore == 93
    assert game.name == "Hades"


def test_parse_free_to_play() -> None:
    html = _read("570.html")
    game = SteamScraper._parse_game(html, 570)
    assert game.price == "Free To Play"
    assert game.release_date == "9 Jul, 2013"


def test_parse_elden_ring() -> None:
    html = _read("1245620.html")
    game = SteamScraper._parse_game(html, 1245620)
    assert game.price == "59.99 EUR"
    assert game.release_date == "24 Feb, 2022"
    assert game.metascore == 94
    assert game.name == "ELDEN RING"


def test_parse_oblivion_goty() -> None:
    html = _read("22330.html")
    game = SteamScraper._parse_game(html, 22330)
    assert game.price == "14.99 EUR"
    assert game.release_date == "11 Sep, 2007"
    assert game.metascore == 94
    expected_name = (
        "The Elder Scrolls IV: Oblivion® Game of the Year Edition "
        "(2009)"
    )
    assert game.name == expected_name


def test_parse_oblivion() -> None:
    html = _read("2623190.html")
    game = SteamScraper._parse_game(html, 2623190)
    assert game.price == "54.99 EUR"
    assert game.release_date == "22 Apr, 2025"
    assert game.metascore is None
    assert game.name == "The Elder Scrolls IV: Oblivion Remastered"

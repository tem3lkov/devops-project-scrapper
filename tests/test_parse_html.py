from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.services.scraper import SteamScraper

HTML_DIR = Path(__file__).parent / "data_html"

def _read(name: str) -> str:
    return (HTML_DIR / name).read_text(encoding="utf-8")

# --- tests --------------------------------------------------------------
def test_parse_price_meta():
    html = _read("1145360.html")
    g = SteamScraper._parse_game(html,1145360)
    assert g.price == "24.50 EUR"
    assert g.metascore == 93
    assert g.name == "Hades"

def test_parse_free_to_play():
    html = _read("570.html")
    g = SteamScraper._parse_game(html, 570)
    assert g.price == "Free To Play"
    assert g.release_date == "9 Jul, 2013"

def test_parse_elden_ring():
    html = _read("1245620.html")
    g = SteamScraper._parse_game(html, 1245620)
    assert g.price == "59.99 EUR"
    assert g.release_date == "24 Feb, 2022"
    assert g.metascore == 94
    assert g.name == "ELDEN RING"


def test_parse_oblivion_goty():
    html = _read("22330.html")
    g = SteamScraper._parse_game(html, 22330)
    assert g.price == "14.99 EUR"
    assert g.release_date == "11 Sep, 2007"
    assert g.metascore == 94
    assert g.name == "The Elder Scrolls IV: Oblivion® Game of the Year Edition (2009)"

def test_parse_oblivion():
    html = _read("2623190.html")
    g = SteamScraper._parse_game(html, 2623190)
    assert g.price == "54.99 EUR"
    assert g.release_date == "22 Apr, 2025"
    assert g.metascore == None
    assert g.name == "The Elder Scrolls IV: Oblivion Remastered"

import asyncio
import time

import httpx
from bs4 import BeautifulSoup

from backend.models.game import Game

TOP_URL = "https://steamspy.com/api.php?request=top100in2weeks"
STORE_URL = "https://store.steampowered.com/app/{appid}"


class SteamScraper:
    """Scrape game data from Steam/SteamSpy."""

    def __init__(self, rows: int,
                 parallel: bool = True,
                 concurrency: int = 20) -> None:
        # Clamp user input to a reasonable range
        self.rows = max(1, min(rows, 100))
        self.parallel = parallel
        self.concurrency = max(1, min(concurrency, 50))

        # Limit concurrent requests when parallel mode is used
        self._sem = asyncio.Semaphore(self.concurrency if parallel else 1)

        now = int(time.time())
        self._headers = {"User-Agent": "SteamScraper v1.0"}
        self._cookies = {
            "birthtime": str(now - 30 * 365 * 24 * 3600),
            "lastagecheckage": "1-January-1995",
            "wants_mature_content": "1",
        }

    async def fetch_games(self) -> list[Game]:
        """Fetch top games and then scrape details for each app ID."""
        async with httpx.AsyncClient(
            headers=self._headers,
            cookies=self._cookies,
            follow_redirects=True,
            timeout=20,
        ) as client:
            ids = await self._fetch_top_ids(client)
            tasks = [self._fetch_details(client, appid) for appid in ids]
            return await asyncio.gather(*tasks)

    async def _fetch_top_ids(self, client: httpx.AsyncClient) -> list[int]:
        response = await client.get(TOP_URL)
        response.raise_for_status()
        data = response.json()
        return [int(key) for key in list(data.keys())[: self.rows]]

    async def _fetch_details(
        self,
        client: httpx.AsyncClient,
        appid: int,
    ) -> Game:
        async with self._sem:
            response = await client.get(
                STORE_URL.format(appid=appid),
                params={"l": "english"},
            )
            response.raise_for_status()
            return self._parse_game(response.text, appid)

    @staticmethod
    def _parse_game(html: str, appid: int) -> Game:
        soup = BeautifulSoup(html, "html.parser")

        name = SteamScraper._extract_name(soup)
        release_date = SteamScraper._extract_release_date(soup)
        price = SteamScraper._extract_price(soup)
        metascore = SteamScraper._extract_metascore(soup)

        return Game(
            appid=appid,
            name=name,
            release_date=release_date,
            price=price,
            metascore=metascore,
            url=f"https://store.steampowered.com/app/{appid}",
        )

    @staticmethod
    def _extract_name(soup: BeautifulSoup) -> str | None:
        name_tag = soup.find("div", class_="apphub_AppName")
        return name_tag.text.strip() if name_tag else None

    @staticmethod
    def _extract_release_date(soup: BeautifulSoup) -> str | None:
        release_date_tag = soup.find("div", class_="date")
        return release_date_tag.text.strip() if release_date_tag else None

    @staticmethod
    def _extract_metascore(soup: BeautifulSoup) -> int | None:
        metascore_tag = soup.find("div", class_="score")
        if not metascore_tag:
            return None

        text = metascore_tag.text.strip()
        return int(text) if text.isdigit() else None

    @staticmethod
    def _extract_price(soup: BeautifulSoup) -> str | None:
        """Extract price from meta tags or data-price-final attribute."""
        meta_price = soup.select_one('meta[itemprop="price"]')
        if meta_price and meta_price.get("content"):
            price_val = str(meta_price["content"]).strip().replace(",", ".")
            currency_tag = soup.select_one('meta[itemprop="priceCurrency"]')
            currency = currency_tag.get("content") if currency_tag else "EUR"

            if price_val in {"0", "0.00"}:
                return "Free To Play"

            try:
                value = float(price_val)
            except ValueError:
                return f"{price_val} {currency}"
            return f"{value:.2f} {currency}"

        wrapper = soup.select_one('[data-price-final]')
        if wrapper and str(wrapper["data-price-final"]).isdigit():
            cents = int(str(wrapper["data-price-final"]))
            if cents == 0:
                return "Free To Play"
            return f"{cents / 100:.2f} EUR"

        return None


import asyncio, time, httpx
from bs4 import BeautifulSoup
from backend.models.game import Game

# API to fetch top 100 games in the last 2 weeks
TOP_URL   = "https://steamspy.com/api.php?request=top100in2weeks"

# Steam store URL template
STORE_URL = "https://store.steampowered.com/app/{appid}"

# SteamScraper class to scrape game data from Steam
class SteamScraper:
    def __init__(self, rows: int, parallel: bool = True, concurrency: int = 20):
        self.rows        = max(1, min(rows, 100))   # min 1, max 100 rows
        self.parallel    = parallel # whether to use parallel requests
        self.concurrency = max(1, min(concurrency, 50)) # max 1, max 50 concurrent requests
        self._sem        = asyncio.Semaphore(self.concurrency if parallel else 1) # limit concurrent requests

        # Set up headers to display mature content and look like a "real user"
        now = int(time.time())
        self._headers = {"User-Agent": "SteamScraper v1.0"}
        self._cookies = {
            "birthtime": str(now - 30 * 365 * 24 * 3600),
            "lastagecheckage": "1-January-1995",
            "wants_mature_content": "1",
        }

    # Fetch top 100 games from SteamSpy API and then scrape details from Steam store
    async def fetch_games(self) -> list[Game]:
        async with httpx.AsyncClient(
            headers=self._headers,
            cookies=self._cookies,
            follow_redirects=True,
            timeout=20,
        ) as client:

            ids   = await self._fetch_top_ids(client)
            tasks = [self._fetch_details(client, appid) for appid in ids]

            return await asyncio.gather(*tasks) # Wait for all tasks to complete
    
    # Fetch top game IDs from SteamSpy API
    async def _fetch_top_ids(self, client: httpx.AsyncClient) -> list[int]:
        r = await client.get(TOP_URL)
        r.raise_for_status()
        return [int(k) for k in list(r.json().keys())[: self.rows]]

    # Fetch game details from Steam store
    async def _fetch_details(self, client: httpx.AsyncClient, appid: int) -> Game:
        async with self._sem:  # limit concurrent requests
            r = await client.get(STORE_URL.format(appid=appid), params={"l": "english"}) # request to Steam store
            r.raise_for_status() # raise exception if status code is not 200
            return self._parse_game(r.text, appid)

    # Parse the HTML response to extract game details
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
        if metascore_tag:
            text = metascore_tag.text.strip()
            return int(text) if text.isdigit() else None
        return None


    @staticmethod
    def _extract_price(soup: BeautifulSoup) -> str | None:
        # Check for price in meta tags
        meta_price = soup.select_one('meta[itemprop="price"]')
        if meta_price and meta_price.get("content"):
            price_val = str(meta_price["content"]).strip().replace(",", ".")
            currency  = (soup.select_one('meta[itemprop="priceCurrency"]') or {}).get(
                "content", "EUR"
            )
            if price_val in {"0", "0.00"}:
                return "Free To Play"
            try:
                return f"{float(price_val):.2f} {currency}"
            except ValueError:
                return f"{price_val} {currency}"
            
        # Check for price in data-price-final attribute
        wrapper = soup.select_one('[data-price-final]')
        if wrapper and str(wrapper["data-price-final"]).isdigit():
            cents = int(str(wrapper["data-price-final"]))
            return "Free To Play" if cents == 0 else f"{cents/100:.2f} EUR"

        return None

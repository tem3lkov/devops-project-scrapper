from fastapi import FastAPI, HTTPException, Query

from backend.services.scraper import SteamScraper
from backend.utils.timer import elapsed

# FastAPI is an asynchronous web framework that works with Uvicorn
app = FastAPI(title="Steam HTML Scraper", version="1.0.0")


# / – Main endpoint
@app.get("/")
async def root() -> dict:
    return {
        "message": "Welcome to Steam HTML Scraper API!",
        "description": "This API helps fetch data from the Steam store.",
    }


# /games – Endpoint to fetch game data
@app.get("/games")
async def games(
    rows: int = Query(
        ...,
        ge=1,
        le=100,
        description="How many games to fetch (1–100).",
    ),
    parallel: bool = Query(
        True,
        description="Whether to fetch in parallel or serial mode.",
    ),
    concurrency: int = Query(
        20,
        ge=1,
        le=50,
        description="Maximum number of concurrent requests.",
    ),
) -> dict:
    with elapsed() as timer:
        try:
            scraper = SteamScraper(
                rows=rows,
                parallel=parallel,
                concurrency=concurrency,
            )
            data = await scraper.fetch_games()
        except Exception as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "rows": len(data),
        "parallel": parallel,
        "concurrency": concurrency,
        "elapsed": timer(),
        "data": [game.to_dict() for game in data],
    }


@app.get("/health")
def health() -> dict:
    return {"status": "This should be changed! OK"}

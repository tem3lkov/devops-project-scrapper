from fastapi import FastAPI, Query, HTTPException
from backend.services.scraper import SteamScraper
from backend.utils.timer import elapsed

# FastApi is an asynchronous web framework that works with Uvicorn
app = FastAPI(title="Steam HTML Scraper", version="1.0.0")

# / – Main endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Steam HTML Scraper API!",
        "description": "This api helps fetch data from the steam store.",
    }

# /games – Endpoint to fetch game data
@app.get("/games")
async def games(
    rows: int = Query(..., ge=1, le=100, description="How many games to fetch?"),
    parallel: bool = Query(True, description="Should requests be parallel?"),
    concurrency: int = Query(20, ge=1, le=50, description="Number of concurrent requests"),
):
    with elapsed() as t:
        try:
            scraper = SteamScraper(rows, parallel=parallel, concurrency=concurrency)
            data = await scraper.fetch_games()
        except Exception as e:
            raise HTTPException(status_code=502, detail=str(e))
    return {
        "rows": len(data),
        "parallel": parallel,
        "concurrency": concurrency,
        "elapsed": t(),
        "data": [g.to_dict() for g in data],
    }

@app.get("/health")
def health():
    return {"status": "ok"}
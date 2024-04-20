import uvicorn
from fastapi import FastAPI, Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

from api.scrape import Vlr
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# It's creating an instance of the Limiter class.
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="vlrggapi",
    description="An Unofficial REST API for [vlr.gg](https://www.vlr.gg/), a site for Valorant Esports match and news "
                "coverage. Made by [Rehkloos](https://github.com/Rehkloos)",
    version="1.0.5",
    docs_url="/",
    redoc_url=None,
)
vlr = Vlr()

# It's setting the rate limit for the API.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")


@app.get("/news")
@cache(expire=300, namespace="vlrapi-news")
@limiter.limit("250/minute")
async def VLR_news(request: Request):
    return vlr.vlr_recent()


@app.get("/match/results")
@cache(expire=300, namespace="vlrapi-results")
@limiter.limit("250/minute")
async def VLR_results(request: Request):
    return vlr.vlr_results()


@app.get("/stats/{region}/{timespan}")
@cache(expire=300, namespace="vlrapi-stats")
@limiter.limit("250/minute")
async def VLR_stats(region, timespan, request: Request):
    """
    region shortnames:
        "na" -> "north-america",
        "eu" -> "europe",
        "ap" -> "asia-pacific",
        "sa" -> "latin-america",
        "jp" -> "japan",
        "oce" -> "oceania",
        "mn" -> "mena",

    timespan:
        "30" -> 30 days,
        "60" -> 60 days,
        "90" -> 90 days,
    """
    return vlr.vlr_stats(region, timespan)


@app.get("/rankings/{region}")
@cache(expire=300, namespace="vlrapi-rankings")
@limiter.limit("250/minute")
async def VLR_ranks(region, request: Request):
    """
    region shortnames:\n
        "na" -> "north-america",\n
        "eu" -> "europe",\n
        "ap" -> "asia-pacific",\n
        "la" -> "latin-america",\n
        "la-s" -> "la-s",\n
        "la-n" -> "la-n",\n
        "oce" -> "oceania",\n
        "kr" -> "korea",\n
        "mn" -> "mena",\n
        "gc" -> "game-changers",\n
        "br" -> "Brazil",\n
        "cn" -> "china",\n
    """
    return vlr.vlr_rankings(region)


@app.get("/match/upcoming")
@cache(expire=300, namespace="vlrapi-upcoming")
@limiter.limit("250/minute")
async def VLR_upcoming(request: Request):
    return vlr.vlr_upcoming()

@app.get("/match/upcoming_index")
@cache(expire=300, namespace="vlrapi-upcoming-index")
@limiter.limit("250/minute")
async def VLR_upcoming_index(request: Request):
    return vlr.vlr_upcoming_index()

@app.get("/match/live_score")
@cache(expire=300, namespace="vlrapi-live-score")
@limiter.limit("250/minute")
async def VLR_live_score(request: Request):
    return vlr.vlr_live_score()

@app.get("/match/streams/{match}")
@limiter.limit("250/minute")
@cache(expire=300, namespace="vlrapi-streams")
async def VLR_streams(match, request: Request):
    return vlr.vlr_streams(match)


@app.get('/health')
def health():
    return "Healthy: OK"

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3002)

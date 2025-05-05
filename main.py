import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from typing import Optional, List, AsyncGenerator
from contextlib import asynccontextmanager

from api.scrape import Vlr
from models.responses import NewsResponse, UpcomingMatchItem, CompletedMatchItem, PlayerStats, TeamRanking, LiveScoreItem, StreamInfo
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi.openapi.utils import get_openapi

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Define lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan event handler for the application.
    This replaces the deprecated on_event("startup") handler.
    """
    # Startup: Initialize cache - simplest possible approach
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    
    yield  # This is where the application runs

# Create FastAPI app with lifespan handler
app = FastAPI(
    title="vlrggapi",
    description="An Unofficial REST API for [vlr.gg](https://www.vlr.gg/), a site for Valorant Esports match and news "
                "coverage. Made by [Rehkloos](https://github.com/Rehkloos)",
    version="1.0.6",
    docs_url="/",
    redoc_url=None,
    lifespan=lifespan,
)

# Initialize the VLR client
vlr = Vlr()

# Set up rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/news", response_model=NewsResponse, tags=["News"])
@cache(expire=300, namespace="vlrapi-news")
@limiter.limit("250/minute")
async def get_news(request: Request):
    """
    Get recent news articles from VLR.GG
    """
    return vlr.vlr_recent()


@app.get("/match/results", response_model=dict, tags=["Matches"])
@cache(expire=300, namespace="vlrapi-results")
@limiter.limit("250/minute")
async def get_match_results(request: Request):
    """
    Get recent match results
    """
    return vlr.vlr_results()


@app.get("/stats/{region}/{timespan}", tags=["Statistics"])
@cache(expire=300, namespace="vlrapi-stats")
@limiter.limit("250/minute")
async def get_player_stats(
    region: str, 
    timespan: int, 
    request: Request
):
    """
    Get player statistics by region and timespan
    
    - **region**: Region shortcode (na, eu, ap, sa, oce, mn)
    - **timespan**: Time period in days (30, 60, 90)
    """
    if timespan not in [30, 60, 90]:
        raise HTTPException(status_code=400, detail="Timespan must be 30, 60, or 90 days")
    
    return vlr.vlr_stats(region, timespan)


@app.get("/rankings/{region}", tags=["Rankings"])
@cache(expire=300, namespace="vlrapi-rankings")
@limiter.limit("250/minute")
async def get_team_rankings(
    region: str, 
    request: Request
):
    """
    Get team rankings by region
    
    - **region**: Region shortcode:
        - "na" -> "north-america"
        - "eu" -> "europe"
        - "ap" -> "asia-pacific"
        - "la" -> "latin-america"
        - "la-s" -> "la-s"
        - "la-n" -> "la-n"
        - "oce" -> "oceania"
        - "kr" -> "korea"
        - "mn" -> "mena"
        - "gc" -> "game-changers"
        - "br" -> "Brazil"
        - "cn" -> "china"
    """
    return vlr.vlr_rankings(region)


@app.get("/match/upcoming", tags=["Matches"])
@cache(expire=300, namespace="vlrapi-upcoming")
@limiter.limit("250/minute")
async def get_upcoming_matches(request: Request):
    """
    Get upcoming matches
    """
    return vlr.vlr_upcoming()


@app.get("/match/live_score", tags=["Matches"])
@cache(expire=300, namespace="vlrapi-live-score")
@limiter.limit("250/minute")
async def get_live_scores(request: Request):
    """
    Get live match scores
    """
    return vlr.vlr_live_score()


@app.get("/match/streams/{match}", tags=["Streams"])
@limiter.limit("250/minute")
@cache(expire=300, namespace="vlrapi-streams")
async def get_match_streams(match: str, request: Request):
    """
    Get streams for a specific match
    
    - **match**: Match ID from VLR.GG
    """
    return vlr.vlr_streams(match)


@app.get('/health', tags=["System"])
def health():
    """
    Health check endpoint
    """
    return {"status": "healthy"}


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add additional metadata
    openapi_schema["info"]["x-logo"] = {
        "url": "https://valorantesports.com/static/favicon-32x32.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=3002, reload=True)

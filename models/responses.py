from typing import List, Optional
from pydantic import BaseModel, Field

class NewsItem(BaseModel):
    """Model for a news article from VLR.GG."""
    title: str = Field(description="Title of the news article")
    description: str = Field(description="Description or summary of the news article")
    date: str = Field(description="Publication date of the article")
    author: str = Field(description="Author of the article")
    url_path: str = Field(description="URL path to the full article")

class NewsResponse(BaseModel):
    """Response model for news API endpoint."""
    data: dict = Field(description="Response data container")
    
    class Config:
        schema_extra = {
            "example": {
                "data": {
                    "status": 200,
                    "segments": [
                        {
                            "title": "Team Liquid vs FUT Esports preview",
                            "description": "The battle for a spot in the upper bracket finals",
                            "date": "May 4, 2025",
                            "author": "John Doe",
                            "url_path": "/12345/team-liquid-vs-fut-esports-preview"
                        }
                    ]
                }
            }
        }

class StreamInfo(BaseModel):
    """Model for a stream information."""
    title: str = Field(description="Stream title")
    href: str = Field(description="Stream URL")
    platform: str = Field(description="Streaming platform (e.g., Twitch, YouTube)")

class MatchItem(BaseModel):
    """Model for a match item."""
    team1: str = Field(description="Name of team 1")
    team2: str = Field(description="Name of team 2")
    flag1: str = Field(description="Flag class for team 1")
    flag2: str = Field(description="Flag class for team 2")
    score1: str = Field(description="Score for team 1")
    score2: str = Field(description="Score for team 2")
    tournament_name: Optional[str] = Field(None, description="Tournament name")
    tournament_icon: str = Field(description="Tournament icon URL")
    round_info: str = Field(description="Match round information")
    match_page: str = Field(description="URL to the match page")
    match_stream: Optional[dict] = Field(None, description="Stream information if available")

class UpcomingMatchItem(MatchItem):
    """Model for an upcoming match."""
    time_until_match: str = Field(description="Time until the match starts")

class CompletedMatchItem(MatchItem):
    """Model for a completed match."""
    time_completed: str = Field(description="Time since the match was completed")

class LiveScoreItem(BaseModel):
    """Model for live scores."""
    team1: str = Field(description="Name of team 1")
    team2: str = Field(description="Name of team 2")
    flag1: str = Field(description="Flag class for team 1")
    flag2: str = Field(description="Flag class for team 2")
    score1: str = Field(description="Score for team 1")
    score2: str = Field(description="Score for team 2")
    round1: str = Field(description="Current round for team 1")
    round2: str = Field(description="Current round for team 2")
    time_until_match: str = Field(description="Match status or time")
    round_info: str = Field(description="Match round information")
    tournament_name: str = Field(description="Tournament name")
    unix_timestamp: int = Field(description="Match timestamp in Unix format")
    match_page: str = Field(description="URL to the match page")

class PlayerStats(BaseModel):
    """Model for player statistics."""
    player: str = Field(description="Player name")
    org: str = Field(description="Organization/team name")
    average_combat_score: str = Field(description="Average combat score")
    kill_deaths: str = Field(description="Kill/death ratio")
    average_damage_per_round: str = Field(description="Average damage per round")
    kills_per_round: str = Field(description="Kills per round")
    assists_per_round: str = Field(description="Assists per round")
    first_kills_per_round: str = Field(description="First kills per round")
    first_deaths_per_round: str = Field(description="First deaths per round")
    headshot_percentage: str = Field(description="Headshot percentage")
    clutch_success_percentage: str = Field(description="Clutch success percentage")

class TeamRanking(BaseModel):
    """Model for team rankings."""
    rank: str = Field(description="Team rank")
    team: str = Field(description="Team name")
    country: str = Field(description="Team country")
    last_played: str = Field(description="Last played match info")
    last_played_team: str = Field(description="Team from last played match")
    last_played_team_logo: str = Field(description="Logo of the team from last played match")
    record: str = Field(description="Team record")
    earnings: str = Field(description="Team earnings")
    logo: str = Field(description="Team logo URL")
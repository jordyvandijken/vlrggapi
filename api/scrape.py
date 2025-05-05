from typing import Dict, List, Any, Tuple
import re
import requests

from selectolax.parser import HTMLParser

from api.base_scraper import BaseScraper
from utils.constants import headers, region_map, BASE_URL, NEWS_URL, MATCHES_URL, RESULTS_URL, RANKINGS_URL
from utils.helpers import get_hostname, clean_text, extract_flags


class NewsScraper(BaseScraper):
    """Scraper for VLR news articles."""
    
    def get_recent_news(self) -> Dict[str, Any]:
        """
        Get recent news articles from VLR.
        
        Returns:
            Dictionary containing news data
        """
        html, status = self.get_parse(NEWS_URL)
        result = []
        
        for item in html.css('a.wf-module-item'):
            # Get date and author
            date_author = item.css_first("div.ge-text-light").text()
            date, author = date_author.split('by')
            
            # Get description
            desc = item.css_first("div").css_first("div:nth-child(2)").text().strip()
            
            # Get title
            title = item.css_first("div:nth-child(1)").text().strip().split('\n')[0]
            title = title.replace('\t', '')
            
            # Get URL
            url = item.css_first("a.wf-module-item").attributes['href']
            
            # Add to results
            result.append(
                {
                    "title": title,
                    "description": desc,
                    "date": date.split("\u2022")[1].strip(),
                    "author": author.strip(),
                    "url_path": url,
                }
            )
        
        data = {
            "data": {
                "status": status,
                "segments": result
            }
        }
        
        self.check_status(status)
        return data


class MatchScraper(BaseScraper):
    """Scraper for VLR matches."""
    
    def _get_teams(self, item: Any) -> List[str]:
        """Extract team names from match item."""
        teams = []
        team_items = item.css(".match-item-vs-team-name")
        for team in team_items:
            teams.append(team.text().strip())
        return teams
    
    def _get_scores(self, item: Any) -> List[str]:
        """Extract scores from match item."""
        scores = []
        score_items = item.css(".match-item-vs-team-score")
        for score in score_items:
            scores.append(score.text().strip())
        return scores
    
    def _get_eta(self, item: Any) -> str:
        """Extract ETA from match item."""
        eta = item.css_first(".match-item-eta").text().replace("\t", "").replace("\n", " ").strip()
        if eta != "LIVE":
            eta = eta + " from now"
        return eta
    
    def _get_tournament_icon(self, item: Any) -> str:
        """Extract tournament icon from match item."""
        tournament_icon = item.css_first("img").attributes['src']
        tournament_icon = f"https:{tournament_icon}"
        return tournament_icon
    
    def _get_match_info(self, html: HTMLParser) -> List[Dict[str, Any]]:
        """Extract match information from HTML."""
        result = []
        
        for item in html.css("a.wf-module-item"):
            teams = self._get_teams(item)
            flags = extract_flags(item.css('.flag'))
            scores = self._get_scores(item)
            tournament_icon = self._get_tournament_icon(item)
            eta = self._get_eta(item)
            match_url = item.attributes['href']
            rounds = item.css_first(".match-item-event-series").text().strip()
            
            tournament = None
            tournament_item = item.css_first(".match-item-event")
            if tournament_item is not None:
                tournament = tournament_item.text().strip()
                tournament = tournament.replace("\t", " ")
                tournament = tournament.strip().split("\n")
                if len(tournament) > 1:
                    tournament = tournament[1].strip()
            
            # Get streams if live or upcoming
            stream = []
            if eta == "LIVE" or "Upcoming" in eta:
                stream = self.get_streams(match_url[1:])
            
            result.append(
                {
                    "team1": teams[0],
                    "team2": teams[1],
                    "flag1": flags[0],
                    "flag2": flags[1],
                    "score1": scores[0],
                    "score2": scores[1],
                    "time_until_match": eta,
                    "round_info": rounds,
                    "tournament_name": tournament,
                    "match_page": match_url,
                    "match_stream": stream,
                    "tournament_icon": tournament_icon,
                }
            )
        
        return result
    
    def get_streams(self, match: str) -> Dict[str, Any]:
        """Get stream information for a match."""
        url = f"{BASE_URL}/{match}"
        resp = requests.get(url, headers=headers)
        html = HTMLParser(resp.text)
        status = resp.status_code
        
        result = []
        
        for stream in html.css("div.match-streams-container .match-streams-btn:not(.mod-expand)"):
            title = ""
            span = stream.css_first("span")
            if span is not None:
                title = span.text().strip()
            
            href = ""
            link = stream.css_first("a")
            if link is not None:
                href = link.attributes['href']
            
            if href == "":
                href = stream.attributes.get('href', "")
            
            platform = get_hostname(href)
            
            result.append(
                {
                    "title": title,
                    "href": href,
                    "platform": platform,
                }
            )
        
        data = {"status": status, "data": result}
        
        self.check_status(status)
        return data
    
    def get_upcoming_matches(self) -> Dict[str, Any]:
        """Get upcoming matches."""
        url = MATCHES_URL
        resp = requests.get(url, headers=headers)
        html = HTMLParser(resp.text)
        status = resp.status_code
        
        amount_of_pages = len(html.css(".action-container-pages a.mod-page"))
        
        result = self._get_match_info(html)
        
        for page_index in range(2, amount_of_pages + 1):
            next_url = f"{url}?page={page_index}"
            resp = requests.get(next_url, headers=headers)
            html = HTMLParser(resp.text)
            status = resp.status_code
            result += self._get_match_info(html)
        
        segments = {"status": status, "segments": result}
        
        data = {"data": segments}
        
        self.check_status(status)
        return data
    
    def get_match_results(self) -> Dict[str, Any]:
        """Get match results."""
        url = RESULTS_URL
        resp = requests.get(url, headers=headers)
        html = HTMLParser(resp.text)
        status = resp.status_code
        
        result = []
        for item in html.css("a.wf-module-item"):
            url_path = item.attributes['href']
            
            eta = item.css_first("div.ml-eta").text() + " ago"
            
            rounds = item.css_first("div.match-item-event-series").text()
            rounds = rounds.replace("\u2013", "-")
            rounds = clean_text(rounds)
            
            tourney = item.css_first("div.match-item-event").text()
            tourney = tourney.replace("\t", " ")
            tourney = tourney.strip().split("\n")[1]
            tourney = tourney.strip()
            
            tourney_icon_url = item.css_first("img").attributes['src']
            tourney_icon_url = f"https:{tourney_icon_url}"
            
            try:
                team_array = item.css_first("div.match-item-vs").css_first("div:nth-child(2)").text()
            except:
                team_array = "TBD"
            
            team_array = clean_text(team_array)
            team_array = team_array.strip().split("                                  ")
            
            # Parse team data
            team1 = team_array[0]
            score1 = team_array[1].replace(" ", "").strip()
            team2 = team_array[4].strip()
            score2 = team_array[-1].replace(" ", "").strip()
            
            # Get flag classes
            flag_list = extract_flags(item.css('.flag'))
            flag1 = flag_list[0]
            flag2 = flag_list[1]
            
            result.append(
                {
                    "team1": team1,
                    "team2": team2,
                    "score1": score1,
                    "score2": score2,
                    "flag1": flag1,
                    "flag2": flag2,
                    "time_completed": eta,
                    "round_info": rounds,
                    "tournament_name": tourney,
                    "match_page": url_path,
                    "tournament_icon": tourney_icon_url,
                }
            )
        
        segments = {"status": status, "segments": result}
        data = {"data": segments}
        
        self.check_status(status)
        return data
    
    def get_live_score(self) -> Dict[str, Any]:
        """Get live match scores."""
        url = BASE_URL
        resp = requests.get(url, headers=headers)
        html = HTMLParser(resp.text)
        status = resp.status_code
        
        result = []
        first_item = html.css(".js-home-matches-upcoming a.wf-module-item")[0]
        
        teams = []
        flags = []
        scores = []
        rounds = []
        for team in first_item.css(".h-match-team"):
            teams.append(team.css_first(".h-match-team-name").text().strip())
            flags.append(team.css_first(".flag").attributes["class"].replace(" mod-", "").replace("16", "_"))
            scores.append(team.css_first(".h-match-team-score").text().strip())
            
            round_elem = team.css_first(".h-match-team-rounds")
            if round_elem and round_elem.css_first('span.mod-t'):
                # Using css_first instead of find to match the code style
                rounds.append(round_elem.css_first('span.mod-t').text().strip())
            else:
                rounds.append("N/A")
        
        eta = first_item.css_first(".h-match-eta").text().strip()
        if eta != "LIVE":
            eta = eta + " from now"
        
        rounds_info = first_item.css_first(".h-match-preview-event").text().strip()
        tournament = first_item.css_first(".h-match-preview-series").text().strip()
        timestamp = int(first_item.css_first(".moment-tz-convert").attributes["data-utc-ts"])
        url_path = url + "/" + first_item.attributes["href"]
        
        result.append(
            {
                "team1": teams[0],
                "team2": teams[1],
                "flag1": flags[0],
                "flag2": flags[1],
                "score1": scores[0],
                "score2": scores[1],
                "round1": rounds[0],
                "round2": rounds[1],
                "time_until_match": eta,
                "round_info": rounds_info,
                "tournament_name": tournament,
                "unix_timestamp": timestamp,
                "match_page": url_path
            }
        )
        
        segments = {"status": status, "segments": result}
        data = {"data": segments}
        
        self.check_status(status)
        return data


class StatsScraper(BaseScraper):
    """Scraper for VLR player statistics."""
    
    def get_player_stats(self, region: str, timespan: int) -> Dict[str, Any]:
        """
        Get player statistics.
        
        Args:
            region: Region code
            timespan: Timespan in days
            
        Returns:
            Dictionary containing player stats
        """
        url = (f"{BASE_URL}/stats/?event_group_id=all&event_id=all&region={region}&country=all&min_rounds=200"
               f"&min_rating=1550&agent=all&map_id=all&timespan={timespan}d")
        
        resp = requests.get(url, headers=headers)
        html = HTMLParser(resp.text)
        status = resp.status_code
        
        result = []
        for item in html.css("tbody tr"):
            player = item.text().replace("\t", "").replace("\n", " ").strip()
            player = player.split()
            player_name = player[0]
            
            # Get org name
            try:
                org = player[1]
            except:
                org = "N/A"
            
            # Get stats
            color_sq = [stats.text() for stats in item.css("td.mod-color-sq")]
            acs = color_sq[0]
            kd = color_sq[1]
            kast = color_sq[2]
            adr = color_sq[3]
            kpr = color_sq[4]
            apr = color_sq[5]
            fkpr = color_sq[6]
            fdpr = color_sq[7]
            hs = color_sq[8]
            cl = color_sq[9]
            
            result.append(
                {
                    "player": player_name,
                    "org": org,
                    "average_combat_score": acs,
                    "kill_deaths": kd,
                    "average_damage_per_round": adr,
                    "kills_per_round": kpr,
                    "assists_per_round": apr,
                    "first_kills_per_round": fkpr,
                    "first_deaths_per_round": fdpr,
                    "headshot_percentage": hs,
                    "clutch_success_percentage": cl,
                }
            )
        
        segments = {"status": status, "segments": result}
        data = {"data": segments}
        
        self.check_status(status)
        return data


class RankingScraper(BaseScraper):
    """Scraper for VLR team rankings."""
    
    def get_rankings(self, region: str) -> Dict[str, Any]:
        """
        Get team rankings.
        
        Args:
            region: Region code
            
        Returns:
            Dictionary containing team rankings
        """
        url = f"{RANKINGS_URL}/{region_map[region]}"
        resp = requests.get(url, headers=headers)
        html = HTMLParser(resp.text)
        status = resp.status_code
        
        result = []
        for item in html.css("div.rank-item"):
            # Get team ranking
            rank = item.css_first("div.rank-item-rank-num").text().strip()
            
            # Get team name
            team = item.css_first("div.ge-text").text()
            team = team.split("#")[0]
            
            # Get logo URL
            logo = item.css_first("a.rank-item-team").css_first("img").attributes['src']
            logo = re.sub(r'\/img\/vlr\/tmp\/vlr.png', '', logo)
            
            # Get team country
            country = item.css_first("div.rank-item-team-country").text()
            
            # Process last played info
            last_played = item.css_first("a.rank-item-last").text()
            last_played = last_played.replace('\n', '').replace('\t', '').split('v')[0]
            
            last_played_team = item.css_first("a.rank-item-last").text()
            last_played_team = last_played_team.replace('\t', '').replace('\n', '').split('o')[1]
            last_played_team = last_played_team.replace('.', '. ')
            
            last_played_team_logo = item.css_first("a.rank-item-last").css_first("img").attributes['src']
            
            # Get record and earnings
            record = clean_text(item.css_first("div.rank-item-record").text())
            earnings = clean_text(item.css_first("div.rank-item-earnings").text())
            
            result.append(
                {
                    "rank": rank,
                    "team": team.strip(),
                    "country": country,
                    "last_played": last_played.strip(),
                    "last_played_team": last_played_team.strip(),
                    "last_played_team_logo": last_played_team_logo,
                    "record": record,
                    "earnings": earnings,
                    "logo": logo,
                }
            )
        
        data = {"status": status, "data": result}
        
        self.check_status(status)
        return data


class Vlr:
    """Main VLR API class that combines all scrapers."""
    
    def __init__(self):
        self.news_scraper = NewsScraper()
        self.match_scraper = MatchScraper()
        self.stats_scraper = StatsScraper()
        self.ranking_scraper = RankingScraper()
        # Initialize match results cache
        self.results_cache = []
        self.last_fetch_time = 0
        self.cache_refresh_interval = 300  # Refresh cache every 5 minutes
    
    def vlr_recent(self):
        """Get recent news."""
        return self.news_scraper.get_recent_news()
    
    def vlr_results(self):
        """Get match results with efficient caching."""
        import time
        current_time = time.time()
        
        # If cache is empty or refresh interval has passed, update the cache
        if not self.results_cache or (current_time - self.last_fetch_time) > self.cache_refresh_interval:
            fresh_results = self.match_scraper.get_match_results()
            
            if not self.results_cache:
                # First-time initialization
                self.results_cache = fresh_results
            else:
                # Only add new matches that aren't already in our cache
                # Using match_page as a unique identifier
                existing_match_ids = {match["match_page"] for match in self.results_cache["data"]["segments"]}
                
                new_matches = []
                for match in fresh_results["data"]["segments"]:
                    if match["match_page"] not in existing_match_ids:
                        new_matches.append(match)
                
                # Add new matches to the beginning of our cache
                if new_matches:
                    self.results_cache["data"]["segments"] = new_matches + self.results_cache["data"]["segments"]
            
            self.last_fetch_time = current_time
        
        return self.results_cache
    
    def vlr_stats(self, region: str, timespan: int):
        """Get player stats."""
        return self.stats_scraper.get_player_stats(region, timespan)
    
    def vlr_rankings(self, region: str):
        """Get team rankings."""
        return self.ranking_scraper.get_rankings(region)
    
    def vlr_upcoming(self):
        """Get upcoming matches."""
        return self.match_scraper.get_upcoming_matches()
    
    def vlr_live_score(self):
        """Get live scores."""
        return self.match_scraper.get_live_score()
    
    def vlr_streams(self, match: str):
        """Get match streams."""
        return self.match_scraper.get_streams(match)


if __name__ == '__main__':
    vlr = Vlr()
    print(vlr.vlr_upcoming())

import httpx
from selectolax.parser import HTMLParser
from typing import Tuple, Dict, Any, Optional

class BaseScraper:
    """Base class for all scrapers with common functionality."""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
        }
    
    async def get_parse(self, url: str, client: httpx.AsyncClient = None) -> Tuple[HTMLParser, int]:
        """
        Make an async request to a URL and return the HTML parser and status code.
        
        Args:
            url: The URL to request
            client: Optional async HTTP client (creates one if not provided)
            
        Returns:
            A tuple of (HTMLParser, status_code)
        """
        if client is None:
            async with httpx.AsyncClient(timeout=8.0) as async_client:
                resp = await async_client.get(url, headers=self.headers)
                html, status_code = resp.text, resp.status_code
        else:
            resp = await client.get(url, headers=self.headers)
            html, status_code = resp.text, resp.status_code
        return HTMLParser(html), status_code
    
    def check_status(self, status: int) -> None:
        """
        Check if the API response is successful.
        
        Args:
            status: HTTP status code
            
        Raises:
            Exception: If status is not 200
        """
        if status != 200:
            raise Exception(f"API response: {status}")
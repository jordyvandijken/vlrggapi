from urllib.parse import urlparse
from typing import List, Optional, Any

def get_hostname(url: str) -> str:
    """
    Extract the domain name from a URL.
    
    Args:
        url: The full URL
        
    Returns:
        The hostname/platform name
    """
    hostname = urlparse(url).hostname
    if not hostname:
        return ""
        
    parts = hostname.split('.')
    if len(parts) == 2:  # If there's only one dot, take the first part
        return parts[0]
    elif len(parts) > 2:  # If there are more than one dots, take the second part
        return parts[1]
    else:
        return hostname  # Return the hostname as is if no dots are found

def clean_text(text: str) -> str:
    """
    Remove unnecessary whitespace, tabs and newlines from text.
    
    Args:
        text: The text to clean
        
    Returns:
        Cleaned text
    """
    return text.replace("\t", " ").replace("\n", " ").strip()

def extract_flags(items: List[Any]) -> List[str]:
    """
    Extract flag classes from HTML elements.
    
    Args:
        items: List of HTML elements with flag classes
        
    Returns:
        List of flag class strings
    """
    return [item.attributes["class"].replace(" mod-", "_") for item in items]


def fetch_image_as_base64(src: str, default_host: str = "https://www.vlr.gg") -> str:
    """Fetch an image from `src`, return a data URI with base64-encoded bytes.

    Normalizes common src forms: absolute (http/https), protocol-relative (//...),
    and site-relative (/...). On failure returns an empty string.

    Args:
        src: The image `src` attribute value from the page
        default_host: Host to prefix when src is site-relative

    Returns:
        A string like "data:image/png;base64,<...>" or empty string on error
    """
    import base64
    import requests
    from utils.constants import headers

    if not src:
        return ""

    # Normalize src to a full URL
    src = src.strip()
    if src.startswith("//"):
        url = f"https:{src}"
    elif src.startswith("/"):
        url = f"{default_host}{src}"
    elif src.startswith("http://") or src.startswith("https://"):
        url = src
    else:
        # Treat as relative
        url = f"{default_host}/{src.lstrip('/') }"

    try:
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "image/png")
        b64 = base64.b64encode(resp.content).decode('ascii')
        return f"data:{content_type};base64,{b64}"
    except Exception:
        # On any failure return empty string so callers can decide fallback
        return ""
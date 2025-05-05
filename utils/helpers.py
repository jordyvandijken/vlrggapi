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
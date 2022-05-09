from typing import Optional
from bs4 import BeautifulSoup


def escape_html(string: str, builder: str = "lxml") -> str:
    return BeautifulSoup(string, builder).string


def escape_html_or_none(
    string: Optional[str],
    builder: str = "lxml",
) -> Optional[str]:
    if string:
        return escape_html(string, builder)
    return None

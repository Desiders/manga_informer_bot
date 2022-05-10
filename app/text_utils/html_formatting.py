import html
from typing import Optional

from bs4 import BeautifulSoup


def escape_html_tags(string: str, builder: str = "lxml") -> str:
    return BeautifulSoup(string, builder).text


def escape_html_tags_or_none(
    string: Optional[str],
    builder: str = "lxml",
) -> Optional[str]:
    if string:
        return escape_html_tags(string, builder)
    return None

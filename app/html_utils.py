from bs4 import BeautifulSoup


def escape_html(string: str, builder: str = "lxml") -> str:
    return BeautifulSoup(string, builder).text

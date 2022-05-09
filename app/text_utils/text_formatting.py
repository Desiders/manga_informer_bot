from typing import Optional

from aiogram.utils.text_decorations import html_decoration as html

UNKNOWN_TEXT = "unknown"
SOURCE_TEXT = "Source"


def is_correct_name(name: Optional[str]) -> bool:
    return name is not None


def formatting_titles(*titles) -> str:
    start = "\t"
    func_format = html.code
    func_check = is_correct_name
    sep = "\n\t"

    return start + sep.join(map(func_format, filter(func_check, titles)))


def formatting_description(description: str) -> str:
    func_format = html.code

    if description:
        return "\n" + func_format(description)
    else:
        return func_format(UNKNOWN_TEXT)


def formatting_genres(genres: list[str]) -> str:
    func_format = html.code

    if not genres:
        return func_format(UNKNOWN_TEXT)
    else:
        sep = ", "

        return sep.join(map(func_format, genres))


def formatting_source(url: str) -> str:
    func_format = html.link

    return func_format(SOURCE_TEXT, url)


def formatting_relation_type(relation_type: str) -> str:
    func_format = html.code

    return func_format(relation_type.capitalize())

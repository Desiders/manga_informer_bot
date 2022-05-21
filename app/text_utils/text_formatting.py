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


def formatting_titles_for_inline(*titles) -> str:
    func_check = is_correct_name
    sep = " | "

    return sep.join(filter(func_check, titles))


def formatting_title_format(title_format: str) -> str:
    func_format = html.code

    if title_format.startswith("TV") or title_format in {"OVA", "ONA"}:
        pass
    else:
        title_format = title_format.capitalize()

    return func_format(
        title_format.replace("_", " "),
    )


def formatting_title_format_for_inline(title_format: str) -> str:
    if title_format.startswith("TV") or title_format in {"OVA", "ONA"}:
        pass
    else:
        title_format = title_format.capitalize()

    return title_format.replace("_", " ")


def formatting_description(description: Optional[str]) -> str:
    func_format = html.code

    if description:
        return "\n" + func_format(description)
    else:
        return func_format(UNKNOWN_TEXT)


def formatting_description_for_inline(
    title_format: str, relation_type: str,
) -> str:
    sep = " | "

    return sep.join((title_format, relation_type))


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

    return func_format(
        relation_type.replace("_", " ").capitalize(),
    )


def formatting_relation_type_for_inline(relation_type: str) -> str:
    return relation_type.replace("_", " ").capitalize()


def cut_description(description: str, need_cut_length: int) -> str:
    return description[:-need_cut_length]

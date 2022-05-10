from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from aiogram.utils.text_decorations import html_decoration as html
from app.services.manga.anilist import AnilistApi
from app.services.manga.anilist.exceptions import MangaNotFound, ServerError
from app.text_utils.html_formatting import escape_html_tags
from app.text_utils.text_checker import all_text_length, utf8_length
from app.text_utils.text_formatting import (cut_description,
                                            formatting_description,
                                            formatting_genres,
                                            formatting_relation_type,
                                            formatting_source,
                                            formatting_title_format,
                                            formatting_titles)
from structlog import get_logger
from structlog.stdlib import BoundLogger

MAX_TEXT_LENGHT = 4000

logger: BoundLogger = get_logger()


async def manga_preview_cmd(m: Message, anilist: AnilistApi):
    text = (
        "Wait one second, please! Searching..."
    )

    wait_msg = await m.reply(
        text=text,
        parse_mode=None,
        disable_web_page_preview=True,
        disable_notification=True,
    )

    page = 1
    manga_name = m.text

    try:
        manga = await anilist.manga_preview_by_name(manga_name)
    except MangaNotFound:
        text = (
            "Manga with this name not found!"
        )

        await wait_msg.edit_text(
            text=text,
            parse_mode=None,
            disable_web_page_preview=True,
        )
        return
    except ServerError as e:
        logger.exception(e, message=m)

        text = (
            "The source have some problems, repeat your request later!"
        )

        await wait_msg.edit_text(
            text=text,
            parse_mode=None,
            disable_web_page_preview=True,
        )
        return

    if utf8_length(manga_name) > 64:
        text = (
            "This manga name is so long!"
        )

        await wait_msg.edit_text(
            text=text,
            parse_mode=None,
            disable_web_page_preview=True,
        )
        return
    
    titles = formatting_titles(
        manga.english_name,
        manga.romaji_name,
        manga.native_name,
    )
    title_format = formatting_title_format(manga.title_format)
    description = formatting_description(manga.description)
    genres = formatting_genres(manga.genres)
    source = formatting_source(manga.url)

    text_length = all_text_length(
        titles, description,
        genres, source,
    )

    if text_length > MAX_TEXT_LENGHT:
        need_cut_length = text_length - MAX_TEXT_LENGHT

        description = formatting_description(
            cut_description(
                escape_html_tags(description, "lxml"),
                need_cut_length,
            ),
        ) + "... (so long description)"

    text = (
        "Titles:\n{titles}\n\n"
        "Format: {title_format}\n\n"
        "Description: {description}\n\n"
        "Genres: {genres}\n\n"
        "{source}"
    ).format(
        titles=titles,
        title_format=title_format,
        description=description,
        genres=genres,
        source=source,
    )

    buttons = [
        InlineKeyboardButton(
            text="⬅️ Previous",
            callback_data=f"manga_preview_page {page - 1} {manga_name}"
        ),
        InlineKeyboardButton(
            text="Next ➡️",
            callback_data=f"manga_preview_page {page + 1} {manga_name}"
        ),
        InlineKeyboardButton(
            text="Relations",
            callback_data=f"manga_relations {manga.id}",
        ),
    ]

    await wait_msg.delete()
    await m.answer(
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=False,
        disable_notification=False,
        reply_markup=InlineKeyboardMarkup(row_width=2).add(*buttons)
    )


async def manga_preview_incorrect_cmd(m: Message):
    text = (
        "Bot receive only text for search!\n"
        "Send any manga's name. For example: "
        f"{html.code('Tokyo Ghoul')}.\n\n"
    )

    await m.reply(
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        disable_notification=False,
    )


async def manga_preview_switch_cmd(q: CallbackQuery, anilist: AnilistApi):
    _, page, manga_name = q.data.split(maxsplit=2)
    page = int(page)

    if page <= 0:
        text = (
            "Manga not found!"
        )

        await q.answer(
            text=text,
            show_alert=True,
            cache_time=86400,
        )
        return

    try:
        manga = await anilist.manga_preview_page_by_name(
            page=page, name=manga_name,
        )
    except MangaNotFound:
        text = (
            "Manga not found!"
        )

        await q.answer(
            text=text,
            show_alert=True,
            cache_time=30,
        )
        return
    except ServerError as e:
        logger.exception(e, query=q)

        text = (
            "The source have some problems, repeat your request later!"
        )

        await q.answer(
            text=text,
            show_alert=True,
            cache_time=5,
        )
        return

    titles = formatting_titles(
        manga.english_name,
        manga.romaji_name,
        manga.native_name,
    )
    title_format = formatting_title_format(manga.title_format)
    description = formatting_description(manga.description)
    genres = formatting_genres(manga.genres)
    source = formatting_source(manga.url)

    text_length = all_text_length(
        titles, description,
        genres, source,
    )

    if text_length > MAX_TEXT_LENGHT:
        need_cut_length = text_length - MAX_TEXT_LENGHT

        description = formatting_description(
            cut_description(
                escape_html_tags(description, "lxml"),
                need_cut_length,
            ),
        ) + "... (so long description)"

    text = (
        "Titles:\n{titles}\n\n"
        "Format: {title_format}\n\n"
        "Description: {description}\n\n"
        "Genres: {genres}\n\n"
        "{source}"
    ).format(
        titles=titles,
        title_format=title_format,
        description=description,
        genres=genres,
        source=source,
    )

    m = q.message

    buttons = m.reply_markup.inline_keyboard
    for row_index, row in enumerate(buttons):
        for button_index, button in enumerate(row):
            button_text = button.text.lower()

            if button_text.endswith("previous"):
                buttons[row_index][button_index].callback_data = (
                    f"manga_preview_page {page - 1} {manga_name}"
                )
            elif button_text.startswith("next"):
                buttons[row_index][button_index].callback_data = (
                    f"manga_preview_page {page + 1} {manga_name}"
                )
            elif button_text.startswith("relations"):
                buttons[row_index][button_index].callback_data = (
                    f"manga_relations {manga.id}"
                )

    await m.edit_text(
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=False,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await q.answer()


async def manga_relations_cmd(q: CallbackQuery, anilist: AnilistApi):
    _, manga_id = q.data.split(maxsplit=1)

    try:
        relations = await anilist.manga_relations_by_id(manga_id)
    except ServerError as e:
        logger.exception(e, query=q)

        text = (
            "The source have some problems, repeat your request later!"
        )

        await q.answer(
            text=text,
            show_alert=True,
            cache_time=5,
        )
        return

    if not relations:
        text = (
            "Relations for this manga not found!"
        )

        await q.answer(
            text=text,
            show_alert=True,
            cache_time=30,
        )
        return

    pre_texts = []
    for index, manga in enumerate(relations, start=1):
        titles = formatting_titles(
            manga.english_name,
            manga.romaji_name,
            manga.native_name,
        )
        title_format = formatting_title_format(manga.title_format)
        relation_type = formatting_relation_type(manga.relation_type)
        source = formatting_source(manga.url)

        pre_text = (
            "{index}. "
            "Titles:\n{titles}\n\n"
            "Format: {title_format}\n"
            "Relation: {relation_type}\n\n"
            "{source}"
        ).format(
            index=index,
            titles=titles,
            title_format=title_format,
            relation_type=relation_type,
            source=source,
        )

        pre_texts.append(pre_text)

    text = "Relations:\n\n" + "\n--------\n".join(pre_texts)

    await q.message.reply(
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        disable_notification=False,
    )
    await q.answer()


def register_manga_handlers(dp: Dispatcher):
    dp.register_message_handler(
        manga_preview_cmd,
        content_types=["text"],
        state="*",
    )
    dp.register_message_handler(
        manga_preview_incorrect_cmd,
        content_types=["any"],
        state="*",
    )
    dp.register_callback_query_handler(
        manga_preview_switch_cmd,
        Text(startswith="manga_preview_page"),
        state="*",
    )
    dp.register_callback_query_handler(
        manga_relations_cmd,
        Text(startswith="manga_relations"),
        state="*",
    )

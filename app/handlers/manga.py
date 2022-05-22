from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, InlineQuery,
                           InlineQueryResultArticle, InputTextMessageContent,
                           Message)
from aiogram.utils.text_decorations import html_decoration as html
from app.filters import CorrectId
from app.services.manga.anilist import AnilistApi
from app.services.manga.anilist.exceptions import MangaNotFound, ServerError
from app.text_utils.html_formatting import (escape_html_tags,
                                            escape_html_tags_or_none)
from app.text_utils.text_checker import all_text_length, utf8_length
from app.text_utils.text_formatting import (
    cut_description, formatting_description, formatting_description_for_inline,
    formatting_genres, formatting_relation_type_for_inline, formatting_source,
    formatting_title_format, formatting_title_format_for_inline,
    formatting_titles, formatting_titles_for_inline)
from structlog import get_logger
from structlog.stdlib import BoundLogger

MAX_TEXT_LENGHT = 4000
MAX_COUNT_RELATIONS = 18

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
        logger.exception(
            "Handling error!",
            error=e,
            message=m,
        )

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
        ) + html.bold("... (so long description)")

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
            callback_data=f"preview {page - 1} {manga_name}"
        ),
        InlineKeyboardButton(
            text="Next ➡️",
            callback_data=f"preview {page + 1} {manga_name}"
        ),
        InlineKeyboardButton(
            text="Relations",
            switch_inline_query_current_chat=f"relations {manga.id}",
        ),
        InlineKeyboardButton(
            text="Share",
            switch_inline_query=f"share {manga.id}",
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
        logger.exception(
            "Handling error!",
            error=e,
            query=q,
        )

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
    description = formatting_description(
        escape_html_tags_or_none(manga.description, "lxml"),
    )
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
        ) + html.bold("... (so long description)")

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
                    f"preview {page - 1} {manga_name}"
                )
            elif button_text.startswith("next"):
                buttons[row_index][button_index].callback_data = (
                    f"preview {page + 1} {manga_name}"
                )
            elif button_text.startswith("relations"):
                buttons[row_index][button_index]\
                    .switch_inline_query_current_chat = (
                    f"relations {manga.id}"
                )
            elif button_text.startswith("share"):
                buttons[row_index][button_index].switch_inline_query = (
                    f"share {manga.id}"
                )

    await m.edit_text(
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=False,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await q.answer()


async def manga_share_cmd(q: InlineQuery, anilist: AnilistApi):
    _, manga_id = q.query.split(maxsplit=1)
    manga_id = int(manga_id)

    try:
        manga = await anilist.manga_preview_by_id(manga_id)
    except MangaNotFound:
        return
    except ServerError as e:
        logger.exception(
            "Handling error!",
            error=e,
            query=q,
        )
        return

    if utf8_length(str(manga_id)) > 64:
        return

    titles = formatting_titles(
        manga.english_name,
        manga.romaji_name,
        manga.native_name,
    )
    titles_for_inline = formatting_titles_for_inline(
        manga.english_name,
        manga.romaji_name,
        manga.native_name,
    )
    title_format = formatting_title_format(manga.title_format)
    description = formatting_description(
        escape_html_tags_or_none(manga.description, "lxml"),
    )
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
        ) + html.bold("... (so long description)")

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

    description_for_inline = formatting_title_format_for_inline(
        manga.title_format,
    )

    manga_preview = InlineQueryResultArticle(
        id=manga_id,
        title=titles_for_inline,
        input_message_content=InputTextMessageContent(
            message_text=text,
            parse_mode="HTML",
            disable_web_page_preview=False,
        ),
        description=description_for_inline,
        thumb_url=manga.banner_image_url,
    )

    await q.answer(
        results=[manga_preview],
        cache_time=3,
        is_personal=False,
    )


async def manga_relations_cmd(q: InlineQuery, anilist: AnilistApi):
    _, manga_id = q.query.split(maxsplit=1)
    manga_id = int(manga_id)

    try:
        manga_relations = await anilist.manga_relations_by_id(manga_id)
    except MangaNotFound:
        return
    except ServerError as e:
        logger.exception(
            "Handling error!",
            error=e,
            query=q,
        )

        return

    if not manga_relations:
        return

    results = []
    for manga in manga_relations:
        titles = formatting_titles(
            manga.english_name,
            manga.romaji_name,
            manga.native_name,
        )
        titles_for_inline = formatting_titles_for_inline(
            manga.english_name,
            manga.romaji_name,
            manga.native_name,
        )

        title_format = formatting_title_format(manga.title_format)

        description = formatting_description(
            escape_html_tags_or_none(manga.description, "lxml"),
        )
        description_for_inline = formatting_description_for_inline(
            title_format=formatting_title_format_for_inline(
                manga.title_format,
            ),
            relation_type=formatting_relation_type_for_inline(
                manga.relation_type,
            ),
        )

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
            ) + html.bold("... (so long description)")

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

        manga_relation_preview = InlineQueryResultArticle(
            id=manga.id,
            title=titles_for_inline,
            input_message_content=InputTextMessageContent(
                message_text=text,
                parse_mode="HTML",
                disable_web_page_preview=False,
            ),
            description=description_for_inline,
            thumb_url=manga.banner_image_url,
        )

        results.append(manga_relation_preview)

    await q.answer(
        results=results,
        cache_time=3,
        is_personal=False,
    )


def register_manga_handlers(dp: Dispatcher):
    dp.register_message_handler(
        manga_preview_cmd,
        content_types={"text"},
        state="*",
    )
    dp.register_message_handler(
        manga_preview_incorrect_cmd,
        content_types={"any"},
        state="*",
    )
    dp.register_callback_query_handler(
        manga_preview_switch_cmd,
        Text(startswith="preview"),
        state="*",
    )
    dp.register_inline_handler(
        manga_share_cmd,
        Text(startswith="share"),
        CorrectId(is_correct_id=True),
        state="*",
    )
    dp.register_inline_handler(
        manga_relations_cmd,
        Text(startswith="relations"),
        CorrectId(is_correct_id=True),
        state="*",
    )

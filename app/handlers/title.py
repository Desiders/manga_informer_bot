from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, InlineQuery,
                           InlineQueryResultArticle, InputTextMessageContent,
                           Message)
from aiogram.utils.text_decorations import html_decoration as html
from app.filters import CorrectId
from app.services.title.anilist import AnilistApi
from app.services.title.anilist.dto import TitleFormat
from app.services.title.anilist.exceptions import ServerError, TitleNotFound
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


async def title_format_cmd(m: Message):
    text = (
        "What title format do you want to see?"
    )

    buttons = [
        InlineKeyboardButton(
            text="Anime (anime, OVA, etc.)",
            callback_data="format anime",
        ),
        InlineKeyboardButton(
            text="Manga (manga, novel, etc.)",
            callback_data="format manga",
        ),
        InlineKeyboardButton(
            text="Everything",
            callback_data="format everything",
        ),
    ]

    await m.reply(
        text=text,
        parse_mode=None,
        disable_web_page_preview=True,
        disable_notification=False,
        reply_markup=InlineKeyboardMarkup(row_width=1).add(*buttons)
    )


async def title_preview_cmd(q: CallbackQuery, anilist: AnilistApi):
    _, title_format_pure = q.data.split(maxsplit=2)
    if title_format_pure == "anime":
        title_format = TitleFormat.ANIME
    elif title_format_pure == "manga":
        title_format = TitleFormat.MANGA
    elif title_format_pure == "everything":
        title_format = TitleFormat.EVERYTHING

    text = (
        "Wait one second, please! Searching..."
    )

    m = q.message.reply_to_message

    wait_msg = await m.reply(
        text=text,
        parse_mode=None,
        disable_web_page_preview=True,
        disable_notification=True,
    )

    page = 1
    name = m.text

    try:
        title = await anilist.title_preview_by_name(
            name=name, title_format=title_format,
        )
    except TitleNotFound:
        text = (
            "Title with this name not found!"
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
        await q.answer(cache_time=10)
        return

    if utf8_length(name) > 64:
        text = (
            "This title name is so long!"
        )

        await wait_msg.edit_text(
            text=text,
            parse_mode=None,
            disable_web_page_preview=True,
        )
        await q.answer()
        return

    titles = formatting_titles(
        title.english_name,
        title.romaji_name,
        title.native_name,
    )
    title_format = formatting_title_format(title.title_format)
    description = formatting_description(title.description)
    genres = formatting_genres(title.genres)
    source = formatting_source(title.url)

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

    title_format_small = title_format_pure[0]

    buttons = [
        InlineKeyboardButton(
            text="⬅️ Previous",
            callback_data=f"preview {title_format_small} {page - 1} {name}"
        ),
        InlineKeyboardButton(
            text="Next ➡️",
            callback_data=f"preview {title_format_small} {page + 1} {name}"
        ),
        InlineKeyboardButton(
            text="Relations",
            switch_inline_query_current_chat=f"relations {title.id}",
        ),
        InlineKeyboardButton(
            text="Share",
            switch_inline_query=f"share {title.id}",
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
    await q.answer(
        text="Thanks for using the bot!",
        show_alert=False,
    )


async def title_preview_incorrect_cmd(m: Message):
    text = (
        "Bot receive only text for search!\n"
        "Send any title's name. For example: "
        f"{html.code('Tokyo Ghoul')}.\n\n"
    )

    await m.reply(
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        disable_notification=False,
    )


async def title_preview_switch_cmd(q: CallbackQuery, anilist: AnilistApi):
    _, title_format_small, page, name = q.data.split(maxsplit=3)
    page = int(page)

    title_format_pure = {
        "a": "anime",
        "m": "manga",
        "e": "everything",
    }[title_format_small]

    if title_format_pure == "anime":
        title_format = TitleFormat.ANIME
    elif title_format_pure == "manga":
        title_format = TitleFormat.MANGA
    elif title_format_pure == "everything":
        title_format = TitleFormat.EVERYTHING

    if page <= 0:
        text = (
            "Title not found!"
        )

        await q.answer(
            text=text,
            show_alert=True,
            cache_time=86400,
        )
        return

    try:
        title = await anilist.title_preview_page_by_name(
            page=page, name=name, title_format=title_format,
        )
    except TitleNotFound:
        text = (
            "Title not found!"
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
            cache_time=10,
        )
        return

    titles = formatting_titles(
        title.english_name,
        title.romaji_name,
        title.native_name,
    )
    title_format = formatting_title_format(title.title_format)
    description = formatting_description(
        escape_html_tags_or_none(title.description, "lxml"),
    )
    genres = formatting_genres(title.genres)
    source = formatting_source(title.url)

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
                    f"preview {title_format_small} {page - 1} {name}"
                )
            elif button_text.startswith("next"):
                buttons[row_index][button_index].callback_data = (
                    f"preview {title_format_small} {page + 1} {name}"
                )
            elif button_text.startswith("relations"):
                buttons[row_index][button_index]\
                    .switch_inline_query_current_chat = (
                    f"relations {title.id}"
                )
            elif button_text.startswith("share"):
                buttons[row_index][button_index].switch_inline_query = (
                    f"share {title.id}"
                )

    await m.edit_text(
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=False,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await q.answer(cache_time=3)


async def title_share_cmd(q: InlineQuery, anilist: AnilistApi):
    _, title_id = q.query.split(maxsplit=1)
    title_id = int(title_id)

    try:
        title = await anilist.title_preview_by_id(title_id)
    except TitleNotFound:
        return
    except ServerError as e:
        logger.exception(
            "Handling error!",
            error=e,
            query=q,
        )
        return

    if utf8_length(str(title_id)) > 64:
        return

    titles = formatting_titles(
        title.english_name,
        title.romaji_name,
        title.native_name,
    )
    titles_for_inline = formatting_titles_for_inline(
        title.english_name,
        title.romaji_name,
        title.native_name,
    )
    title_format = formatting_title_format(title.title_format)
    description = formatting_description(
        escape_html_tags_or_none(title.description, "lxml"),
    )
    genres = formatting_genres(title.genres)
    source = formatting_source(title.url)

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
        title.title_format,
    )

    preview = InlineQueryResultArticle(
        id=title_id,
        title=titles_for_inline,
        input_message_content=InputTextMessageContent(
            message_text=text,
            parse_mode="HTML",
            disable_web_page_preview=False,
        ),
        description=description_for_inline,
        thumb_url=title.banner_image_url,
    )

    await q.answer(
        results=[preview],
        cache_time=3,
        is_personal=False,
    )


async def title_relations_cmd(q: InlineQuery, anilist: AnilistApi):
    _, title_id = q.query.split(maxsplit=1)
    title_id = int(title_id)

    try:
        relations = await anilist.title_relations_by_id(title_id)
    except TitleNotFound:
        return
    except ServerError as e:
        logger.exception(
            "Handling error!",
            error=e,
            query=q,
        )

        return

    if not relations:
        return

    results = []
    for title in relations:
        titles = formatting_titles(
            title.english_name,
            title.romaji_name,
            title.native_name,
        )
        titles_for_inline = formatting_titles_for_inline(
            title.english_name,
            title.romaji_name,
            title.native_name,
        )

        title_format = formatting_title_format(title.title_format)

        description = formatting_description(
            escape_html_tags_or_none(title.description, "lxml"),
        )
        description_for_inline = formatting_description_for_inline(
            title_format=formatting_title_format_for_inline(
                title.title_format,
            ),
            relation_type=formatting_relation_type_for_inline(
                title.relation_type,
            ),
        )

        genres = formatting_genres(title.genres)
        source = formatting_source(title.url)

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

        preview = InlineQueryResultArticle(
            id=title.id,
            title=titles_for_inline,
            input_message_content=InputTextMessageContent(
                message_text=text,
                parse_mode="HTML",
                disable_web_page_preview=False,
            ),
            description=description_for_inline,
            thumb_url=title.banner_image_url,
        )

        results.append(preview)

    await q.answer(
        results=results,
        cache_time=3,
        is_personal=False,
    )


def register_title_handlers(dp: Dispatcher):
    dp.register_message_handler(
        title_format_cmd,
        content_types={"text"},
        state="*",
    )
    dp.register_callback_query_handler(
        title_preview_cmd,
        Text(startswith="format"),
        state="*",
    )
    dp.register_message_handler(
        title_preview_incorrect_cmd,
        content_types={"any"},
        state="*",
    )
    dp.register_callback_query_handler(
        title_preview_switch_cmd,
        Text(startswith="preview"),
        state="*",
    )
    dp.register_inline_handler(
        title_share_cmd,
        Text(startswith="share"),
        CorrectId(is_correct_id=True),
        state="*",
    )
    dp.register_inline_handler(
        title_relations_cmd,
        Text(startswith="relations"),
        CorrectId(is_correct_id=True),
        state="*",
    )

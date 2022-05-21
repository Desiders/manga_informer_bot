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
from app.text_utils.html_formatting import escape_html_tags
from app.text_utils.text_checker import all_text_length, utf8_length
from app.text_utils.text_formatting import (cut_description,
                                            formatting_description, formatting_description_for_inline,
                                            formatting_genres,
                                            formatting_relation_type, formatting_relation_type_for_inline,
                                            formatting_source,
                                            formatting_title_format, formatting_title_format_for_inline,
                                            formatting_titles,
                                            formatting_titles_for_inline)
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
        InlineKeyboardButton(
            text="Share",
            switch_inline_query=f"manga_inline_preview_by_id {manga.id}",
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
            elif button_text.startswith("share"):
                buttons[row_index][button_index].switch_inline_query = (
                    f"manga_inline_preview_by_id {manga.id}"
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
        manga_relations = await anilist.manga_relations_by_id(manga_id)
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

    relations = manga_relations.relations

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

    texts = []
    for index, manga in enumerate(relations, start=1):
        titles = formatting_titles(
            manga.english_name,
            manga.romaji_name,
            manga.native_name,
        )
        title_format = formatting_title_format(manga.title_format)
        relation_type = formatting_relation_type(manga.relation_type)
        source = formatting_source(manga.url)

        text = (
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

        texts.append(text)

        if index == MAX_COUNT_RELATIONS:
            text = html.bold(
                "\nSo many relations! " + 
                html.link("To the original", manga_relations.url)
            )

            texts.append(text)
            break

    text = "Relations:\n\n" + "\n--------\n".join(texts)

    await q.message.reply(
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        disable_notification=False,
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
        logger.exception(
            "So long utf8_length!",
            error=e,
            query=q,
        )
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

    description_for_inline = formatting_title_format_for_inline(
        manga.title_format,
    )

    buttons = [
        InlineKeyboardButton(
            text="Relations",
            switch_inline_query=f"manga_inline_relations {manga.id}",
        ),
    ]
    manga_preview = InlineQueryResultArticle(
        id=manga_id,
        title=titles_for_inline,
        input_message_content=InputTextMessageContent(
            message_text=text,
            parse_mode="HTML",
            disable_web_page_preview=False,
        ),
        reply_markup=InlineKeyboardMarkup(row_width=2).add(*buttons),
        description=description_for_inline,
        thumb_url=manga.banner_image_url,
    )

    await q.answer(
        results=[manga_preview],
        cache_time=3,
        is_personal=False,
    )


async def manga_relations_inline_cmd(q: InlineQuery, anilist: AnilistApi):
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

    relations = manga_relations.relations

    if not relations:
        return

    results = []
    texts = []
    for index, manga in enumerate(relations, start=1):
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
        relation_type = formatting_relation_type(manga.relation_type)
        source = formatting_source(manga.url)

        text = (
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
        text_for_inline = text + html.bold(
            "\n\nUse bot's functional for more info!",
        )

        description_for_inline = formatting_description_for_inline(
            title_format=formatting_title_format_for_inline(
                manga.title_format,
            ),
            relation_type=formatting_relation_type_for_inline(
                manga.relation_type,
            ),
        )

        manga_relation_preview = InlineQueryResultArticle(
            id=manga.id,
            title=titles_for_inline,
            input_message_content=InputTextMessageContent(
                message_text=text_for_inline,
                parse_mode="HTML",
                disable_web_page_preview=True,
            ),
            description=description_for_inline,
            thumb_url=manga.banner_image_url,
        )

        results.append(manga_relation_preview)

        if index == MAX_COUNT_RELATIONS:
            text = html.bold(
                "\nSo many relations. " + 
                html.link("To the original", manga_relations.url)
            )

            texts.append(text)
        elif index < MAX_COUNT_RELATIONS:
            texts.append(text)

    text = "Relations:\n\n" + "\n--------\n".join(texts)

    manga_relations_preview = InlineQueryResultArticle(
        id=manga_id,
        title="Click for send the manga's relations together!",
        input_message_content=InputTextMessageContent(
            message_text=text,
            parse_mode="HTML",
            disable_web_page_preview=True,
        ),
    )
    results.insert(0, manga_relations_preview)

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
        Text(startswith="manga_preview_page"),
        state="*",
    )
    dp.register_callback_query_handler(
        manga_relations_cmd,
        Text(startswith="manga_relations"),
        state="*",
    )
    dp.register_inline_handler(
        manga_share_cmd,
        Text(startswith="manga_inline_preview_by_id"),
        CorrectId(is_correct_id=True),
        state="*",
    )
    dp.register_inline_handler(
        manga_relations_inline_cmd,
        Text(startswith="manga_inline_relations"),
        CorrectId(is_correct_id=True),
        state="*",
    )

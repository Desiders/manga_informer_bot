from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.utils.text_decorations import html_decoration as html
from app.config_reader import Config


async def source_cmd(m: Message, config: Config):
    text = (
        "The code of this bot: "
        f"{html.link('source', config.source.url)}"
    )

    await m.answer(
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=False,
        disable_notification=False,
    )


def register_source_handlers(dp: Dispatcher):
    dp.register_message_handler(
        callback=source_cmd,
        commands={"source", "code"},
        content_types={"text"},
        state="*",
    )

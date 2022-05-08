import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.environment import EnvironmentMiddleware
from structlog import get_logger
from structlog.stdlib import BoundLogger

from app.config_reader import load_config
from app.handlers import (register_introduction_handlers,
                          register_manga_handlers, register_source_handlers)
from app.logging import logging_configure
from app.services.manga.anilist import AnilistApi

logger: BoundLogger = get_logger()


async def main() -> None:
    logging_configure()
    logger.info("Logging is configured")

    config = load_config("config.ini")
    logger.info("Configuration loaded")

    bot = Bot(
        token=config.bot.token,
        parse_mode=None,
        disable_web_page_preview=None,
    )
    dp = Dispatcher(
        bot=bot,
        storage=MemoryStorage(),
    )

    anilist = AnilistApi()

    dp.setup_middleware(
        EnvironmentMiddleware(
            {"anilist": anilist, "config": config},
        ),
    )
    logger.info("Middlewares are setup!")

    register_introduction_handlers(dp)
    register_source_handlers(dp)
    register_manga_handlers(dp)
    logger.info("Handlers are registered!")

    logger.warning("Bot starting!")
    try:
        await dp.start_polling(
            allowed_updates=[
                "message_handlers", "callback_query_handlers",
            ],
        )
    finally:
        logger.warning("Bot stopped!")

        bot_session = await bot.get_session()
        if bot_session is not None:
            await bot_session.close()

        await anilist.close()

        logger.info("Bye!")


asyncio.run(main())

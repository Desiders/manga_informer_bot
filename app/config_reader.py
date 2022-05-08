from os import getenv

from pydantic import BaseModel


class Bot(BaseModel):
    token: str


class Source(BaseModel):
    url: str


class Config(BaseModel):
    bot: Bot
    source: Source


def load_config() -> Config:
    return Config(
        bot=Bot(
            token=getenv("BOT_TOKEN"),
        ),
        source=Source(
            url=getenv("SOURCE_URL"),
        ),
    )

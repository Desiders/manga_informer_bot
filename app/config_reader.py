from configparser import ConfigParser

from pydantic import BaseModel


class Bot(BaseModel):
    token: str


class Source(BaseModel):
    url: str


class Config(BaseModel):
    bot: Bot
    source: Source


def load_config(path: str) -> Config:
    config = ConfigParser()
    config.read(path)

    bot = config["bot"]
    source = config["source"]

    return Config(
        bot=Bot(
            token=bot["token"],
        ),
        source=Source(
            url=source["url"],
        ),
    )

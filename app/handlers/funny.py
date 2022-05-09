import random

from aiogram import Dispatcher
from aiogram.types import Message

STICKERS_FILE_IDS = [
    # KanekiKen
    "CAACAgQAAxkBAAEPsb1ieQXvAAHgo0bdEfJJ7CA-AAHKgdmBAAJPAQACgALNBQcDO7JDwJvjJAQ",
    "CAACAgQAAxkBAAEPsb9ieQYOk0tb0TfAx5irk_-eI9iqXAACSwEAAoACzQXHx8lgfd3RNyQE",
    # LINE_Cat_ear_girl_Necoco
    "CAACAgIAAxkBAAEPscNieQaatAqYD6QO3XjFAAFcXoP81LYAAo9oAALgo4IH_x-II5lUEdokBA",
    "CAACAgIAAxkBAAEPscVieQbRTgvKNIDLweza27QJhKFRkAACpWgAAuCjggclFgRYTz00xyQE",
    # LINE_Dong_Jin_Rice_hime
    "CAACAgIAAxkBAAEPscdieQcGOYEOlYn_QYG8YS-4XPFtlAACdjcAAuCjggfnHhRQKW121CQE",
    "CAACAgIAAxkBAAEPsclieQc6eP_j0KEZi4_cbstvuKYHOwACczcAAuCjggcBM4mGuZCcriQE",
    # LINE_nachonekodayo
    "CAACAgIAAxkBAAEPsctieQdSQ8yjNmxGqgXgc08eDpewNQAC7WoAAuCjggefr1M1mI4DFCQE",
    "CAACAgIAAxkBAAEPsc1ieQdq2kAIwCb9kWmQG4M-uxOLhwAC-WoAAuCjggfjboP1BOsFECQE",
    # SeiranElenoir
    "CAACAgQAAxkBAAEPsdFieQeWXMwg9LXqmh5z_45YDl7GDwACkwIAAqN9MRXdCfPXqqnJjyQE",
    # yamy_tyan_nyasticks
    "CAACAgIAAxkBAAEPsddieQfXtCGLze2VUQzmgX6vnF-BzQACSxAAAtvmwUoX1EPwOmuGFyQE",
    "CAACAgIAAxkBAAEPsdtieQf9NIQXHfOo2Ft7Ll5sorUzEAAC5Q4AApjWwUrJ7aDKQKi7yCQE",
    "CAACAgIAAxkBAAEPsd1ieQgXqlScTV6v99sd_c9iBwjRJwACFQ8AAoxnuUqhX6LFvIDsZyQE",
    # LINE_Puu_Moody_Girl_4
    "CAACAgIAAxkBAAEPsd9ieQgqSfFx_yWW1nmaSv_Q8k37owAC5FkAAuCjgge-sw2IUzU8uSQE",
    "CAACAgIAAxkBAAEPseFieQhClqo8K8pWSUXO_Fo8igWvegAC7lkAAuCjggeBNrgK-DmHkSQE",
    # Magic_Cat_Mori
    "CAACAgQAAxkBAAEPseNieQhoVFtGqqfqqLm81QQMwkxVvwACBAMAAifSHAfxjj_0cnNR2yQE",
    "CAACAgQAAxkBAAEPseVieQiEU_1jhsgVlSh_RJl6T-5HOAADAwACJ9IcB7sdrTNTL2OxJAQ",
    # Flandrenice,
    "CAACAgIAAxkBAAEPsedieQilLFQ4Db917vuuI2QL0NKOEAACTgADfLufDoPlfvHf69lLJAQ",
    # LINE_Girl_with_black_hair_TL
    "CAACAgIAAxkBAAEPselieQkAAXXRaT3wEugEYeA3jB3U-YUAAutjAALgo4IHgUlpWZWXoUwkBA",
    # LINE_CatGirl_Sticker_ENG
    "CAACAgIAAxkBAAEPsetieQk9ZdE98Eb7DDnvTQoghzk-GQACLzoAAuCjggfEE_UdZYKIniQE",
    "CAACAgIAAxkBAAEPse1ieQlRiEOqiD-yvmWwm6DNhAABO9kAAkE6AALgo4IHDvGsE3ppFjIkBA",
    # LINE_Puni_never_smile
    "CAACAgIAAxkBAAEPse9ieQlhVB8tLC_znwUl88PItokN4AACyzMAAuCjggd8e9cLC7I2FyQE",
    "CAACAgIAAxkBAAEPsfFieQmb84SfOmeSiYo8JncAATgM4CkAAt0zAALgo4IHdSnFUI87DDIkBA",
    # LINE_Puniko_eat_everyday
    "CAACAgIAAxkBAAEPsfNieQmvQz025I6uFgjEPcdCAULbhwACViYAAuCjggcainPeqUtZuyQE",
    "CAACAgIAAxkBAAEPsfVieQnDJEdqFqByZvYT9K1cni9P_AACQCYAAuCjggfKnhdj9-bboiQE",
    # LINE_Girls_Love_Story_2
    "CAACAgIAAxkBAAEPsfdieQnfhqcbiNSqAAGdn8XSohlaBxUAAmYmAALgo4IHHGLslzpuZ-kkBA",
    "CAACAgIAAxkBAAEPsflieQoSqKMhJJ2er57PYfnYTjPlQAACdCYAAuCjggc3zD9fRBWICCQE",
    # LINE_MochiChan_V2
    "CAACAgIAAxkBAAEPsf1ieQpomhxPtLMR0y0giDCKumu9NgACnCUAAuCjggdqvf1Er4pWISQE",
]


async def sticker_cmd(m: Message):
    sticker_file_id = random.choice(STICKERS_FILE_IDS)

    await m.answer_sticker(
        sticker=sticker_file_id,
        disable_notification=True,
    )


def register_funny_handlers(dp: Dispatcher):
    dp.register_message_handler(
        callback=sticker_cmd,
        content_types=["sticker"],
        state="*",
    )

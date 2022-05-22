from typing import Union

from aiogram.dispatcher.filters.filters import Filter
from aiogram.types import CallbackQuery, InlineQuery, Message, Poll


class CorrectId(Filter):
    def __init__(self, is_correct_id: bool):
        self.is_correct_id = is_correct_id

    async def check(self, obj: Union[Message, CallbackQuery,
                                     InlineQuery, Poll]):
        if isinstance(obj, Message):
            text = obj.text or obj.caption or ''
            if not text and obj.poll:
                text = obj.poll.question
        elif isinstance(obj, CallbackQuery):
            text = obj.data
        elif isinstance(obj, InlineQuery):
            text = obj.query
        elif isinstance(obj, Poll):
            text = obj.question
        else:
            return not self.is_correct_id

        try:
            _, manga_id = text.split(maxsplit=1)
        except ValueError:
            return not self.is_correct_id

        return manga_id.isdecimal() is self.is_correct_id

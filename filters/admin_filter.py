from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from data.config import ADMINS

# filter, that checks if user's id  is in ADMINS list
class ForAdmins(BoundFilter):
    async def check(self, callback: types.CallbackQuery) -> bool:
        return str(callback.from_user.id) in ADMINS

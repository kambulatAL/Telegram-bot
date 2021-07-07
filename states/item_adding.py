from aiogram.dispatcher.filters.state import StatesGroup, State


class ItemAdding(StatesGroup):
    item_name = State()
    item_price = State()
    item_photo = State()
    item_description = State()
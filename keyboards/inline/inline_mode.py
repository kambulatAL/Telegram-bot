from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.deep_linking import get_start_link


async def get_show_item_button(item_id: str):
    bot_link = await get_start_link(f'item_{item_id}')
    show_item_button = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Показать товар', url=bot_link)
    ]])
    return show_item_button

from aiogram import types

from keyboards.inline.inline_mode import get_show_item_button
from utils.db_api.db_commands import select_ordered_items, realtime_items


# function for a showing items in the inline mode
async def generate_item_list():
    # select all items in the alphabetical order
    items = await select_ordered_items()
    result = []
    for item in items:
        result.append(
            types.InlineQueryResultArticle(id=str(item.id), title=item.name,
                                           input_message_content=types.InputMessageContent(
                                               message_text=f'{item.name}'),
                                           description=f'Цена товара: ${item.price}', thumb_url=item.photo,
                                           reply_markup=await get_show_item_button(str(item.id))
                                           )
        )
    return result


# function for the searching items on the first letter from the user
async def show_query(query: types.InlineQuery):
    items = await realtime_items(query)
    result = []
    for item in items:
        result.append(
            types.InlineQueryResultArticle(id=str(item.id), title=item.name,
                                           input_message_content=types.InputTextMessageContent(
                                               message_text=f'{item.name}'),
                                           description=f'Цена товара: ${item.price}', thumb_url=item.photo,
                                           reply_markup=await get_show_item_button(str(item.id))
                                           )
        )
    return result

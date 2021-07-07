from aiogram import types

from loader import dp
from utils.inline_data_request import generate_item_list, show_query


# shows items in  inline mode
@dp.inline_handler()
async def show_all_items(query: types.InlineQuery):
    # if a users writes some letters to the search row, then starts to find a similar word in the names of items
    if len(query.query) > 1:
        data = await show_query(query.query)
    else:
        # if there is nothing in the search row, then show list of the items in the alphabetical order
        data = await generate_item_list()
    await query.answer(results=[*data], cache_time=20)

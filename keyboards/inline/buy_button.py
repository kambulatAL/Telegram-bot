from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData


buy_callback = CallbackData('buy', 'item_id')


# function, that creates buy keyboard for an item and adds its id to the callback
def buy(item_id):
    buy_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Купить товар', callback_data=buy_callback.new(item_id=item_id))],
        [InlineKeyboardButton(text='Отмена покупки', callback_data='cancel_purchase')]
    ])
    return buy_keyboard


# pay keyboard to top up a user  balance
paid_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пополнено', callback_data='paid')],
    [InlineKeyboardButton(text='Отмена пополнения', callback_data='cancel_top_up')]
])

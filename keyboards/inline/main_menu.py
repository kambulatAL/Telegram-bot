from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Реферальная система 👥', callback_data='referral_system')],
    [InlineKeyboardButton(text='Админка 👨‍💻', callback_data='for_admins')],
    [InlineKeyboardButton(text='Ваш баланс 💵', callback_data='balance')],
    [InlineKeyboardButton(text='Выбрать товар 👜', switch_inline_query_current_chat='')]
])

back = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text='Назад', callback_data='return_to_menu')
]])

add_items = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить товар', callback_data='add_item')],
    [InlineKeyboardButton(text='Назад', callback_data='return_to_menu')]
])

balance = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пополнить счет', callback_data='top_up_balance')],
    [InlineKeyboardButton(text='Назад', callback_data='return_to_menu')]
])

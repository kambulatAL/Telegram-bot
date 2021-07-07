import re
import base64
from aiogram import types
from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.utils.deep_linking import get_start_link

from keyboards.inline.buy_button import buy
from keyboards.inline.main_menu import menu
from loader import dp, bot
from utils.db_api.db_commands import add_user, select_user, add_referral, bonus_for_referer, get_item
from utils.misc import rate_limit


# handler where comes command /start with an encoded referral link
@dp.message_handler(CommandStart(deep_link=re.compile(r'.+'), encoded=True))
async def registration(message: types.Message):
    # try to get user, that sent a referral link if he exists
    already_exists = await select_user(user_id=message.from_user.id)

    if already_exists is None:

        try:
            # attempt to decode a referral link to get user_id
            referer_id = int(base64.b64decode(message.get_args() + '=='))
        except ValueError:
            await message.answer('Некорректная реферальная ссылка. Попробуйте еще раз')
            return
        # try to find a referer in the database
        referer = await select_user(user_id=referer_id)

        if referer is None:
            await message.answer('Реферальная ссылка не существует. Попробуйте еще раз')
        else:
            # creating of a new referral link for a new user
            ref_link = await get_start_link(message.from_user.id, encode=True)
            # adding a new user to the User table of the database
            await add_user(user_id=message.from_user.id, name=message.from_user.full_name,
                           username=message.from_user.username, ref_link=ref_link)
            # adding a new user as a referral to the Referral table of the database
            await add_referral(referer_id=referer_id, referral_id=message.from_user.id,
                               name=message.from_user.full_name, username=message.from_user.username)
            # giving bonus for the referer, that invited a new user with his ref link
            await bonus_for_referer(user_id=referer_id)
            await message.answer('Вы успешно зарегистрировались.\n'
                                 'Для получения доступа к функциям бота введите /start')

    else:
        await message.answer('Вы уже зарегистрированы.\n'
                             'Для получения доступа к функциям бота введите /start')


@rate_limit(limit=3)
# handler, that catches /start command without  a deeplink
@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    # attempt to get user from the database
    user = await select_user(user_id=message.from_user.id)
    # get channel and its invite link
    chat = await bot.get_chat(chat_id=-1001583189441)
    chat_invite_link = await chat.export_invite_link()
    # checks if a user is a member of the channel
    member = await dp.bot.get_chat_member(chat_id=chat.id, user_id=message.from_user.id)
    subscribed = member.is_chat_member()
    # checks if a user isn't in the database and isn't subscribed
    if (user is None) and (subscribed is False):
        await message.answer(f'Чтобы получить доступ к боту перейдите по '
                             f'реферальной ссылкe, либо введите код приглашения в формате: "/start NjQ1NjQ1MzU2NA"\n'
                             f'Если вам недоступно ничего из вышеперечисленного,\n'
                             f'то можете подписаться на канал: {chat_invite_link} \n'
                             f' после чего вам станет доступен бот')
        return
    # checks if user is subscribed but isn't in the database
    elif subscribed and (user is None):
        # create ref link for a user and add to the User table (he don't have a referer)
        ref_link = await get_start_link(message.from_user.id, encode=True)
        await add_user(user_id=message.from_user.id, name=message.from_user.full_name,
                       username=message.from_user.username, ref_link=ref_link)

        await message.answer('Вы успешно зарегистрировались через подписку на канал.\n'
                             'Для получения доступа к функциям бота введите /start')
        return

    await message.answer(f'Добро пожаловать, {user.name} 👋\n', reply_markup=menu)


# handler catches /start command with a deeplink that starts with pattern "item_"
@dp.message_handler(CommandStart(deep_link=re.compile(r'item_\d+')))
async def buy_item(message: types.Message):
    # attempt to get the user, that wants to buy something and the channel link
    user = await select_user(user_id=message.from_user.id)
    chat = await bot.get_chat(chat_id=-1001583189441)
    chat_invite_link = await chat.export_invite_link()

    if user is None:
        await message.answer(f'Чтобы получить доступ к боту перейдите по '
                             f'реферальной ссылкe, либо введите код приглашения в формате: "/start NjQ1NjQ1MzU2NA"\n'
                             f'Если вам недоступно ничего из вышеперечисленного,\n'
                             f'то можете подписаться на канал: {chat_invite_link} \n'
                             f' после чего вам станет доступен бот')
    else:
        # getting an item id from the deeplink a try to find it
        item_id = message.get_args().split('_')[1]
        item = await get_item(item_id=int(item_id))
        # show the item's photo, description and price with buttons "buy" and "cancel"
        await message.answer_photo(photo=item.photo, caption=f'<b>Товар</b>: {item.name}\n'
                                                             f'<b>Описание</b>: {item.description}\n\n'
                                                             f'<b>Цена:</b> {item.price} USD',
                                   reply_markup=buy(item.id))

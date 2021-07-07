from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from loader import dp

from utils.db_api.db_commands import get_item, select_user, create_purchase, commit_payment


# reacts on pressed buy item
@dp.callback_query_handler(text_contains='buy')
async def buy_item(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=30)
    user = await select_user(call.from_user.id)
    # gets item_id from callback of buy button
    item_id = int(call.data.split(':')[1])
    item = await get_item(item_id)
    # checks that the user has enough money on his balance for a purchase
    if user.balance >= item.price:
        await call.message.answer('Введите количество товара:')
        await state.set_state('quantity')
        await state.update_data(item=item)
    else:
        await call.message.answer('На вашем счете недостаточно средств.\n'
                                  'Для покупки пополните баланс')


# gets the number of items from the user's message
@dp.message_handler(state='quantity')
async def item_quantity(message: types.Message, state: FSMContext):
    item = (await state.get_data()).get('item')
    user = await select_user(user_id=message.from_user.id)

    try:
        quantity = int(message.text)
    except ValueError:
        await message.answer('Некорректное значение. Попробуйте снова')
        return
    # if the user wrote the quantity more then he actually can buy then  send: "you are too greedy"
    if item.price * quantity > user.balance:
        await message.answer('На вашем счете недостаточно средств для покупки такого количества товаров\n'
                             'Введите меньшее количество товара')
        return
    # ask a phone number with the button and hide it after a pressing
    await message.answer('Пришлите номер телефона', reply_markup=ReplyKeyboardMarkup(one_time_keyboard=True,
                                                                                     keyboard=[[
                                                                                         KeyboardButton(
                                                                                             text='Прислать номер',
                                                                                             request_contact=True)
                                                                                     ]], resize_keyboard=True))
    # save the whole amount and the quantity
    amount = item.price * quantity
    await state.update_data(quantity=quantity, amount=amount)
    await state.set_state('get_phone_number')


@dp.message_handler(state='get_phone_number', content_types=types.ContentType.CONTACT)
async def phone_number(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone_number=phone)
    await message.answer('Пришлите адрес доставки в формате: "Страна, Город, Почтовый индекс"')
    await state.set_state('get_address')


@dp.message_handler(state='get_address')
async def add_address(message: types.Message, state: FSMContext):
    await state.update_data(shipping_address=message.text)
    await message.answer('Введите ФИО получателя:')
    await state.set_state('name_of_the_receiver')


@dp.message_handler(state='name_of_the_receiver')
async def make_purchase(message: types.Message, state: FSMContext):
    data = await state.get_data()

    buyer_id = message.from_user.id
    receiver = message.text
    item_id = data['item'].id
    item_quantity = data['quantity']
    amount = data['amount']
    phone = data['phone_number']
    address = data['shipping_address']
    # take the amount from a user's balance
    await commit_payment(user_id=buyer_id, amount=amount)
    # create purchase in the Purchase table of the database
    await create_purchase(buyer=buyer_id, receiver=receiver, item_id=item_id, quantity=item_quantity, amount=amount,
                          phone_number=phone, shipping_address=address, paid=True)
    await message.answer('Покупка оформлена 👌\n'
                         'В ближайшее время с вами свяжутся(скорее всего нет)')
    await state.finish()


@dp.callback_query_handler(text_contains='cancel_purchase')
async def cancel_purchase(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=30)
    await state.finish()
    await call.message.delete_reply_markup()

from aiogram import types
from aiogram.dispatcher import FSMContext

from forex_python.bitcoin import BtcConverter

from loader import dp
from data import config
from filters import ForAdmins
from keyboards.inline.buy_button import paid_keyboard
from keyboards.inline.main_menu import menu, back, add_items, balance
from states import ItemAdding
from utils.db_api.db_commands import check_referrals_quantity, select_user, add_item, increase_balance
from utils.misc.bitcoin_payments import Payment, NotConfirmed, NoPaymentFound


# handler, that returns a user to the main menu
@dp.callback_query_handler(text='return_to_menu')
async def return_button(call: types.CallbackQuery):
    await call.message.edit_text(f'Добро пожаловать, {call.from_user.full_name} 👋\n',
                                 reply_markup=menu)


# referral system, where a user can see his referral link and a number of his referrals
@dp.callback_query_handler(text='referral_system')
async def show_ref_info(call: types.CallbackQuery):
    await call.answer()
    user = await select_user(user_id=call.from_user.id)
    number_of_referrals = await check_referrals_quantity(user.user_id)
    await call.message.edit_text(f'За каждого реферала вы получаете $10\n'
                                 f'Количество ваших рефералов: {number_of_referrals}\n'
                                 f'Ваша реферальная ссылка: {user.ref_link}', reply_markup=back)


# balance account, where a user can see his balance and top up it
@dp.callback_query_handler(text='balance')
async def fet_balance(call: types.CallbackQuery):
    await call.answer()
    user = await select_user(user_id=call.from_user.id)
    await call.message.edit_text(f'Ваш баланс: ${user.balance}',
                                 reply_markup=balance)


# if user press "top up" button then he should set an amount
@dp.callback_query_handler(text='top_up_balance')
async def add_money(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=20)
    await call.message.answer('Введите сумму пополнения:')
    await state.set_state('money')


# after setting the amount will be shown a wallet for money transfer and the amount in BTC
@dp.message_handler(state='money')
async def add_money(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer('Вы ввели некорректную сумму. Попробуйте снова')
        return

    # converting the amount to the BTC
    converter = BtcConverter()
    amount_in_btc = converter.convert_to_btc(amount, 'USD')
    # creating a payment
    payment = Payment(amount=amount_in_btc)
    payment.create()
    # gives pay keyboard with answer message
    await message.answer(f'Оплатите <b>{amount_in_btc:.8f} BTC</b> по адресу: \n\n'
                         f'{config.BTC_WALLET}', reply_markup=paid_keyboard)
    await state.set_state('btc')
    # saving the payment and the amount in memory
    await state.update_data(payment=payment, amount=amount)


# if pressed paid button comes here
@dp.callback_query_handler(text='paid', state='btc')
async def check_payment(call: types.CallbackQuery, state: FSMContext):
    await call.answer(cache_time=30)
    data = await state.get_data()
    payment = data.get('payment')
    amount = data.get('amount')
    # checks payment transfer
    try:
        payment.check_payments()
    except NotConfirmed:
        await call.message.answer('Транзакция в процессе подтверждения. Попробуйте позже')
        return
    except NoPaymentFound:
        await call.message.answer('Транзакция не найдена')
        return
    else:
        # if topping up is successed then add the amount to the user's balance
        await increase_balance(user_id=call.from_user.id, amount=amount)
        await call.message.answer(f'Баланс успешно пополнен на сумму ${amount}')

    await call.message.delete_reply_markup()
    await state.finish()


# if pressed cancel button comes here
@dp.callback_query_handler(text='cancel_top_up', state='btc')
async def check_payment(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(text='Пополнение отменено')
    await state.finish()


# reacts on admin button and check a user with the filter if he is an admin
@dp.callback_query_handler(ForAdmins(), text='for_admins')
async def admin_profile(call: types.CallbackQuery):
    await call.answer()
    await call.message.edit_text(f'Администратор {call.from_user.full_name} 🛠\n\n'
                                 f'Вы можете добавить товар по кнопке ниже👇', reply_markup=add_items)


# if admin wants to add item/product then ItemAdding state sets
@dp.callback_query_handler(text='add_item')
async def adding_of_item(call: types.CallbackQuery):
    await call.answer(cache_time=30)
    await call.message.answer('Введите название товара')
    await ItemAdding.item_name.set()


@dp.message_handler(state=ItemAdding.item_name)
async def add_item_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(item_name=name)
    await message.answer('Введите цену товара')
    await ItemAdding.item_price.set()


@dp.message_handler(state=ItemAdding.item_price)
async def add_item_price(message: types.Message, state: FSMContext):
    try:
        check_text = float(message.text)
        price = message.text
    except ValueError:
        await message.answer('Цена введена некорректно. Попробуйте снова')
        return

    await state.update_data(item_price=price)
    await message.answer('Введите ссылку на фото товара')
    await ItemAdding.item_photo.set()


@dp.message_handler(state=ItemAdding.item_photo)
async def add_item_photo(message: types.Message, state: FSMContext):
    photo = message.text
    await state.update_data(photo_link=photo)
    await message.answer('Введите описание товара')
    await ItemAdding.item_description.set()


@dp.message_handler(state=ItemAdding.item_description)
async def add_item_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('item_name')
    price = data.get('item_price')
    photo = data.get('photo_link')
    description = message.text
    # when all states were set, creates an item in the Items table
    await add_item(name=name, price=price, photo=photo, description=description)
    await message.answer('Товар успешно добавлен в базу данных 👍')
    await state.finish()


# if a user isn't an admin the show alert
@dp.callback_query_handler(text='for_admins')
async def admin_profile(call: types.CallbackQuery):
    await call.answer(text='Вы не являетесь администратором. Доступ запрещен ❌', show_alert=True)

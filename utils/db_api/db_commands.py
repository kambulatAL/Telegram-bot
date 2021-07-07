from asyncpg import UniqueViolationError
from decimal import Decimal
from sqlalchemy import asc

from utils.db_api.database import db
from utils.db_api.models import User, Referral, Item, Purchase


async def select_user(user_id: int):
    user = await User.query.where(User.user_id == user_id).gino.first()
    return user


async def add_user(user_id: int, name: str, ref_link: str, username: str = None, email: str = None):
    try:
        user = User(user_id=int(user_id), name=name, username=username, email=email, ref_link=ref_link)
        await user.create()
    except UniqueViolationError:
        await select_user(user_id=int(user_id))


async def add_referral(referral_id: int, referer_id: int, name: str, username: str = None):
    referral = Referral(referral_id=referral_id, referer_id=referer_id,
                        name=name, username=username)
    await referral.create()


async def select_all_users():
    users = await User.query.gino.all()
    return users


async def count_users():
    count = await db.func.count(User.user_id).gino.scalar()
    return count


# adding money and increasing the number of referrals for the user, that invited a referral
async def bonus_for_referer(user_id: int):
    user = await select_user(user_id=user_id)
    await user.update(balance=user.balance + Decimal('10.00'),
                      number_of_referrals=user.number_of_referrals + 1).apply()


# checks that the number of referrals in the Referral table and in the User table are equal
async def check_referrals_quantity(user_id: int):
    user = await select_user(user_id=user_id)
    user_referrals = user.number_of_referrals
    referral_referrals = await (db.select([db.func.count()]).where(Referral.referer_id == user_id).gino.scalar())

    if user_referrals - referral_referrals == 0:
        return user_referrals
    elif user_referrals > referral_referrals:
        await user.update(number_of_referrals=referral_referrals).apply()
        return referral_referrals


async def add_item(name: str, price: float, photo: str, description: str = None):
    item = Item(name=name, price=price, photo=photo, description=description)
    await item.create()


async def select_ordered_items():
    ordered_items = await Item.query.order_by(asc(Item.name)).gino.all()
    return ordered_items


async def realtime_items(query):
    result = await Item.query.where(Item.name.ilike(f'%{query}%')).gino.all()
    return result


async def get_item(item_id: int):
    item = await Item.query.where(Item.id == item_id).gino.first()
    return item


async def increase_balance(user_id: int, amount: float):
    user = await select_user(user_id=user_id)
    await user.update(balance=user.balance + amount).apply()


async def create_purchase(**kwargs):
    purchase = Purchase(**kwargs)
    await purchase.create()


# take money from a user's balance when he bought something
async def commit_payment(user_id: int, amount: float):
    user = await select_user(user_id=user_id)
    await user.update(balance=user.balance - amount).apply()

from utils.db_api.database import db
from sqlalchemy import Integer, String, BigInteger, Column, Numeric, DateTime, ForeignKey, Sequence, Boolean



class TimedBaseModel(db.Model):
    __abstract__ = True

    created_at = Column(DateTime(True), server_default=db.func.now())


class User(TimedBaseModel):
    __tablename__ = 'users'

    user_id = Column(BigInteger, unique=True, primary_key=True)
    name = Column(String(200))
    username = Column(String(200), nullable=True)
    email = Column(String(200), nullable=True)
    balance = Column(Numeric(precision=10,scale=2), default=0)
    ref_link = Column(String(150))
    number_of_referrals = Column(Integer, default=0)


class Referral(TimedBaseModel):
    __tablename__ = 'referrals'

    referral_id = Column(BigInteger, unique=True, primary_key=True)
    referer_id = Column(Integer, ForeignKey(column=User.user_id, ondelete='CASCADE'))
    name = Column(String(200))
    username = Column(String(200), nullable=True)


class Item(TimedBaseModel):
    __tablename__ = 'items'

    id = Column(Integer, Sequence('items_id_seq'), primary_key=True)
    name = Column(String(250))
    price = Column(Numeric(precision=10,scale=2))
    photo = Column(String(300), nullable=True)
    description = Column(String(400), nullable=True)


class Purchase(TimedBaseModel):
    __tablename__ = 'Purchase'

    id = Column(Integer, Sequence('purchase_id_seq'), primary_key=True)
    buyer = Column(Integer, ForeignKey(column=User.user_id, ondelete='SET NULL'))
    item_id = Column(Integer, ForeignKey(column=Item.id, ondelete='CASCADE'))
    quantity = Column(Integer)
    amount = Column(Numeric(precision=10,scale=2))
    phone_number = Column(String(30))
    shipping_address = Column(String(250), nullable=True)
    receiver = Column(String(200), nullable=True)
    paid = Column(Boolean, default=False)

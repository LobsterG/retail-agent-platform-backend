from . import BaseModel
from peewee import *
from app import db
from .countries import Country
from .users import User

class Merchant(BaseModel):
    # id = AutoField(primary_key=True)
    name = CharField()
    country_code = ForeignKeyField(Country, backref='merchant')
    user_id = ForeignKeyField(User, backref='merchant')

    # class Meta:
    #     indexes = {
    #         (('id', 'country_code'), True),
    #     }


    @classmethod
    def seed(cls, user_id, country_code, count=1):
        from scripts.seed import MerchantFactory

        fake_merchant = MerchantFactory.create_batch(count, user_id=user_id, country_code=country_code)
        with db.atomic():
            merchant_list = [merchant.__dict__['__data__'] for merchant in fake_merchant]
            for merchant in merchant_list:
                cls.create(**merchant)
        return fake_merchant

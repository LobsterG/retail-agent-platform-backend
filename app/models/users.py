from . import BaseModel
from .countries import Country
from peewee import *
from app import db


class User(BaseModel):
    first_name = CharField()
    last_name = CharField()
    email = CharField(unique=True)
    id = CharField(primary_key=True)
    password_salt = CharField()
    password_hash = CharField()
    account_status = CharField()
    country_code = ForeignKeyField(Country, backref='users')


    @classmethod
    def seed(cls, country_code, count=1):
        from scripts.seed import UserFactory

        fake_users = UserFactory.create_batch(count, country_code=country_code)
        with db.atomic():
            user_list = [user.__dict__['__data__'] for user in fake_users]
            for user in user_list:
                cls.create(**user)
        return fake_users
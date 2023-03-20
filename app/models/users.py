from . import BaseModel
from .countries import Country
from peewee import *
from app import db


class User(BaseModel):
    first_name = CharField()
    last_name = CharField()
    email = CharField(unique=True)
    username = CharField(primary_key=True)
    password_salt = BlobField()
    password_hash = BlobField()
    account_status = CharField()
    country_code = ForeignKeyField(Country, backref='users')


    @classmethod
    def seed(cls, count):
        from scripts.seed import UserFactory

        fake_users = UserFactory.create_batch(count)
        with db.atomic():
            user_list = [user.__dict__['__data__'] for user in fake_users]
            for user in user_list:
                cls.create(**user)
            # for user in fake_users:
            #     user.save()
                # print("User created:", user.username, user.first_name, user.email)
            #     # cls.create(**user)

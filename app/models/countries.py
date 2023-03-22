from . import BaseModel
from peewee import *
from app import db

class Country(BaseModel):
    code = CharField(primary_key=True)
    name = CharField()
    

    @classmethod
    def seed(cls):
        countries = [
            {'code': 'US', 'name': 'United States'},
            {'code': 'CA', 'name': 'Canada'},
            {'code': 'GB', 'name': 'United Kingdom'},
            {'code': 'AU', 'name': 'Australia'},
        ]
        with db.atomic():
            for country in countries:
                cls.create(**country)

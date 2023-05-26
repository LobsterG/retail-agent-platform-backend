from . import BaseModel
from peewee import *
from enum import Enum


class Country(BaseModel):
    code = CharField(primary_key=True)
    name = CharField()
    

    @classmethod
    def seed(cls, count):
        from scripts.seed import CountryFactory

        fake_Countries = CountryFactory.create_batch(count)
        with BaseModel._meta.database.atomic():
            country_list = [country.__dict__['__data__'] for country in fake_Countries]
            for country in country_list:
                cls.create(**country)
        return fake_Countries

from peewee import Model, CharField
from app import db


class BaseModel(Model):
    class Meta:
        database = db

class Ingredient(BaseModel):
    name = CharField()
    food_type = CharField(unique=True)

    @classmethod
    def seed(cls):
        ingredients = [
            {'name': 'Apple', 'food_type': 'fruits'},
            {'name': 'Milk', 'food_type': 'dairy'}
        ]

        with db.atomic():
            for ingredient in ingredients:
                cls.create(**ingredient)
                
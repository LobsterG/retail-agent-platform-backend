from peewee import *
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
                
class Recipe(BaseModel):
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
                
class Menu(BaseModel):
    menu_name = CharField(unique=True)
    timestamp = TimestampField()

    @classmethod
    def seed(cls):
        ingredients = [
            {'name': 'Apple', 'food_type': 'fruits'},
            {'name': 'Milk', 'food_type': 'dairy'}
        ]

        with db.atomic():
            for ingredient in ingredients:
                cls.create(**ingredient)

class Review(BaseModel):
    username = CharField()
    review_content = TextField()
    timestamp = TimestampField()

    @classmethod
    def seed(cls):
        ingredients = [
            {'name': 'Apple', 'food_type': 'fruits'},
            {'name': 'Milk', 'food_type': 'dairy'}
        ]

        with db.atomic():
            for ingredient in ingredients:
                cls.create(**ingredient)

from . import BaseModel
from peewee import *
from enum import Enum
from .merchants import Merchant


class StockStatus(Enum):
    OUT_OF_STOCK = 'Out of Stock'
    IN_STOCK = 'In stock'
    LOW_ON_STOCK = 'Low on Stock (less than 5)'


class EnumField(CharField):
    """
    This class enable an Enum like field for Peewee
    """

    def __init__(self, choices, *args, **kwargs) -> None:
        super(CharField, self).__init__(*args, **kwargs)
        self.choices = choices
        self.max_length = 255

    def db_value(self, value):
        return value

    def python_value(self, value):
        return self.choices(type(list(self.choices)[0].value)(value))


class Product(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField()
    price = FloatField()
    status = EnumField(choices=StockStatus)
    stock_level = IntegerField()
    merchant_id = ForeignKeyField(Merchant, backref='products')


    @classmethod
    def seed(cls, merchant_id, count=1):
        from scripts.seed import ProductFactory

        fake_product = ProductFactory.create_batch(count, merchant_id=merchant_id)
        with BaseModel._meta.database.atomic():
            product_list = [product.__dict__['__data__'] for product in fake_product]
            for product in product_list:
                cls.create(**product)
        return fake_product
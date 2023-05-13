from . import BaseModel
from peewee import *
from app import db
from .orders import Order
from .products import Product


class OrderItem(BaseModel):
    id = AutoField(primary_key=True)
    price = FloatField()
    quantity = IntegerField()
    order_id = ForeignKeyField(Order, backref='order_items')
    product_id = ForeignKeyField(Product, backref='order_items')


    @classmethod
    def seed(cls, order_id, product_id, count=1):
        from scripts.seed import OrderItemFactory

        fake_item = OrderItemFactory.create_batch(count, order_id=order_id, product_id=product_id)
        with db.atomic():
            item_list = [item.__dict__['__data__'] for item in fake_item]
            for item in item_list:
                cls.create(**item)
        return fake_item
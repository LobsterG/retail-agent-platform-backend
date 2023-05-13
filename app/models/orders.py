from . import BaseModel
from peewee import *
from app import db
from enum import Enum
from .users import User


class OrderStatus(Enum):
    ORDERED = 'Ordered'
    IN_PROGRESS = 'In Progress'
    CANCELLED = 'Cancelled'
    COMPLETED = 'Completed'
    FAILED = 'Failed'
    

class PaymentStatus(Enum):
    RECEIVED = "Received"
    NOT_PAID = "Not Paid"
    PROCESSING = "Processing"
    REJECTED = "Rejected"


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


class Order(BaseModel):
    id = AutoField(primary_key=True)
    total_price = FloatField()
    payment_status = EnumField(choices=PaymentStatus)
    order_status = EnumField(choices=OrderStatus)
    user_id = ForeignKeyField(User, backref='orders')


    @classmethod
    def seed(cls, user_id, count=1):
        from scripts.seed import OrderFactory

        fake_order = OrderFactory.create_batch(count, user_id=user_id)
        with db.atomic():
            order_list = [order.__dict__['__data__'] for order in fake_order]
            for order in order_list:
                cls.create(**order)
        return fake_order
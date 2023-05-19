import datetime
import peewee
import math

from app import db
from peewee import *

class BaseModel(Model):
    class Meta:
        database = db
        
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def to_dict(self):
        return {'id': self.id}

    @classmethod
    def get_by_id(cls, id):
        return cls.get(cls.id == id)

from .merchants import Merchant
from .countries import Country
from .order_items import OrderItem
from .products import Product
from .orders import Order, PaymentStatus, OrderStatus
from .users import User
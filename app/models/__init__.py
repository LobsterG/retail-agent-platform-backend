import datetime
import peewee
import math

from app import db_initialize
from peewee import *


class BaseModel(Model):
    class Meta:
        # database = PostgresqlDatabase(None) 
        database = db_initialize('prod')
    
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def to_dict(self):
        return {'id': self.id}

    @classmethod
    def update_env(cls, environment):
        cls._meta.database.init(db_initialize(environment))

    @classmethod
    def get_by_id(cls, id):
        return cls.get(cls.id == id)

from .merchants import Merchant
from .countries import Country
from .order_items import OrderItem
from .products import Product
from .orders import Order, PaymentStatus, OrderStatus
from .users import User
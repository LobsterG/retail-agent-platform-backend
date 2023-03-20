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

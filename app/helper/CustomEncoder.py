import datetime
import json

from flask.json.provider import JSONProvider
from ..models import PaymentStatus, OrderStatus, StockStatus

class CustomEncoder(json.JSONEncoder):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.default = self._default

    # @staticmethod
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
            
        if isinstance(obj, StockStatus) or\
            isinstance(obj, PaymentStatus) or \
            isinstance(obj, OrderStatus):

            return obj.value
        raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")

class CustomJsonProvider(JSONProvider):
    """JSON Provider for Flask app to use CustomEncoder."""

    ensure_ascii: bool = True
    sort_keys: bool = True

    def dumps(self, obj, **kwargs):
        kwargs.setdefault("ensure_ascii", self.ensure_ascii)
        kwargs.setdefault("sort_keys", self.sort_keys)
        return json.dumps(obj, **kwargs, cls=CustomEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)
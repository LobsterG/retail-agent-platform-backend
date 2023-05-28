import factory
from factory.faker import Faker
from factory.fuzzy import FuzzyText, FuzzyChoice
from app.models.users import User
from app.models.products import Product, StockStatus
from app.models.merchants import Merchant
from app.models.countries import Country
from app.models.orders import Order, PaymentStatus, OrderStatus
from app.models.order_items import OrderItem


# Generate some fake data for the models
class CountryFactory(factory.Factory):
    class Meta:
        model = Country

    code = FuzzyText(length=2)
    name = FuzzyText(length=20)


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: 'user{}'.format(n))
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    email = Faker('email')
    password_salt = Faker('pystr', max_chars=64)
    password_hash = Faker('pystr', max_chars=64)
    account_status = Faker('random_element', elements=('active', 'inactive'))
    country_code = factory.SubFactory(CountryFactory)


class MerchantFactory(factory.Factory):
    class Meta:
        model = Merchant
    id = factory.Sequence(lambda n: n)
    name = Faker('company')
    country_code = factory.SubFactory(CountryFactory)
    user_id = factory.SubFactory(UserFactory)


class ProductFactory(factory.Factory):
    class Meta:
        model = Product
    id = factory.Sequence(lambda n: n)
    name = Faker('word')
    price = Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    status = FuzzyChoice(choices=[s.value for s in StockStatus])
    stock_level = Faker('pyint', min_value=1, max_value=9999)
    merchant_id = factory.SubFactory(MerchantFactory)
       

class OrderFactory(factory.Factory):
    class Meta:
        model = Order
    id = factory.Sequence(lambda n: n)
    payment_status = FuzzyChoice(choices=[s.value for s in PaymentStatus])
    order_status = FuzzyChoice(choices=[s.value for s in OrderStatus])
    user_id = factory.SubFactory(UserFactory)


class OrderItemFactory(factory.Factory):
    class Meta:
        model = OrderItem
    id = factory.Sequence(lambda n: n)
    price = Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    quantity = Faker('pyint', min_value=1, max_value=9999)
    order_id = factory.SubFactory(OrderFactory)
    product_id = factory.SubFactory(ProductFactory)

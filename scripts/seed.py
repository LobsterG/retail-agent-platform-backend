import factory
from factory.faker import Faker
from app.models.users import User
from app import db


# Generate some fake data for the User model
class UserFactory(factory.Factory):
    class Meta:
        model = User
        # DATABASE = db

    username = factory.Sequence(lambda n: 'user{}'.format(n))
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    email = Faker('email')
    password_salt = Faker('pystr', max_chars=64)
    password_hash = Faker('pystr', max_chars=64)
    account_status = Faker('random_element', elements=('active', 'inactive'))
    country_code = 'US' # Assuming the country code is a string


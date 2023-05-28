import json
import unittest

from functools import wraps
from app import create_app, db_initialize
from app.models import MODELS
from unittest.mock import patch, MagicMock
from playhouse.shortcuts import model_to_dict


# TODO: Add test cases for operations that would expect to fail. Currently only successful operations are tested
api_version = 'v1'
class MerchantTestCase(unittest.TestCase):

    @classmethod
    def bypass_auth(cls):
        # MUST BE BEFORE THE UUT GETS IMPORTED ANYWHERE!
        # Source: https://stackoverflow.com/questions/7667567/can-i-patch-a-python-decorator-before-it-wraps-a-function
        from mock import patch, MagicMock
        def mock_verify_jwt_token(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                return f(cls.user_data, *args, **kwargs)
            return decorated_function
        # Patch the verify_jwt_token decorator with the mock function
        patch('app.auth.verify_jwt_token', side_effect=mock_verify_jwt_token).start()

    @classmethod
    def initalize_data(cls):
        print('Initalizing Data...')        
        countr_code = 'TC'
        user_id = 'test_user_id'
        merchant_id = 'test_merchant_id'
        product_id = 'test_product_id'
        cls.country_data = {
            "code": countr_code,
            "name": "test_country"
        }
        cls.user_data = {
            "id": user_id,
            "account_status": "active",
            "country_code": countr_code,
            "email": "test2_email@example.com",
            "first_name": "Bob2",
            "last_name": "Moyer Third",
            "password_hash": "TrEtnhWdeNykWngFBUObCbmUGyDFhiPVFhELzTptIfTsNRSqudxMnOfOCzaxUeZA",
            "password_salt": "hUsqDnfwtRhbOyRWxsTXuxmzxVEwjjeGFUgcohQUZQFSBYeXToZrszhIZmTqGTJM"
        }
        cls.merchant_data = {
            "name": merchant_id,
            "country_code": countr_code,
            "user_id": user_id
        }
        cls.product_data = {
            "name": product_id,
            "price": 9.99,
            "status": "In stock",
            "stock_level": 10,
            "merchant_id": 1
        }
        print('Initalizing Data Completed.')     

    @classmethod
    def setUpClass(cls):
        cls.initalize_data()
        cls.bypass_auth()
        cls.database = db_initialize('test')
        cls.app = create_app('test')
        cls.client = cls.app.test_client() 
        with cls.app.app_context():
            cls.database.bind(MODELS)
            cls.database.create_tables(MODELS)
    
    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            cls.database.drop_tables(MODELS)
            cls.database.close()

    # This is to create the base data for all tests to share. Note that the DB instance is created at the class level
    def setUp(self):
        with self.app.app_context():
            from app.models import User, Merchant, Country, Product, Product
            # Using atomic operation ensures all commands are done in one transaction, hence more efficeint
            with self.database.atomic():
                Country.create(**self.country_data)
                User.create(**self.user_data)
                Merchant.create(**self.merchant_data)
                Product.create(**self.product_data)

    def tearDown(self):
        with self.app.app_context():
            from app.models import User, Merchant, Country, Product, Product
            # Using atomic operation ensures all commands are done in one transaction, hence more efficeint
            with self.database.atomic():
                Product.truncate_table(restart_identity=True, cascade=True)
                Merchant.truncate_table(restart_identity=True, cascade=True)
                User.truncate_table(restart_identity=True, cascade=True)
                Country.truncate_table(restart_identity=True, cascade=True)


    def test_create_product(self):
        product_data = {
            "name": "test_create_product",
            "price": 10.90,
            "stock_level": 20,
            "merchant_id": 1
        }

        number_of_products = 0
        with self.app.app_context():
            from app.models import Product
            with self.database.atomic():
                number_of_products =  len(Product.select())

        response = self.client.post(
            f'/api/{api_version}/product/', 
            data=json.dumps(product_data), 
            content_type='application/json')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 201)

        from app.models import StockStatus
        self.assertEqual(data["status"], StockStatus.IN_STOCK.value)
        
        with self.app.app_context():
            from app.models import Product
            with self.database.atomic():
                new_number_of_products =  len(Product.select())
                self.assertGreater(new_number_of_products, number_of_products)
        

    def test_get_products(self):
        user_id = self.user_data['id']
        response = self.client.get(f'/api/{api_version}/product/')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(data), list)
        self.assertEqual(len(data), 1)
    

    def test_get_product(self):
        product_id = 1
        response = self.client.get(f'/api/{api_version}/product/{product_id}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(data), 0)
        self.assertEqual(data['id'], product_id)
        self.assertEqual(data['name'], self.product_data['name'])
        self.assertEqual(type(data), dict)


    def test_update_product(self):
        product_id = 1
        update_product_data = {
            "name": 'test_new_product_name',
            "status": 'Out of Stock'
        }

        # Verify the product status is different from what the new value is
        with self.app.app_context():
            from app.models import Product
            with self.database.atomic():
                original_product = Product.get(Product.id == product_id)
                self.assertNotEqual(original_product.status.value, update_product_data['status'])
                self.assertNotEqual(original_product.name, update_product_data['name'])

        response = self.client.patch(
            f'/api/{api_version}/product/{product_id}', 
            data=json.dumps(update_product_data), 
            content_type='application/json')
        self.assertEqual(response.status_code, 204)

        with self.app.app_context():
            from app.models import Product
            with self.database.atomic():
                updated_product = Product.get(Product.id == product_id)
                self.assertEqual(updated_product.status.value, update_product_data['status'])
                self.assertEqual(updated_product.name, update_product_data['name'])


    def test_delete_product(self):
        product_id = 1
        response = self.client.delete(f'/api/{api_version}/product/{product_id}')
        self.assertEqual(response.status_code, 204)

        with self.app.app_context():
            from app.models import Product
            with self.database.atomic():
                deleted_product = Product \
                                .select() \
                                .where(Product.id == product_id)
                products = [model_to_dict(product) for product in deleted_product]
                self.assertEqual(len(products), 0)

if __name__ == '__main__':
    unittest.main()

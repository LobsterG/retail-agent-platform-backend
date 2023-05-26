import json
import unittest

from functools import wraps
from peewee import PostgresqlDatabase
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
                return f(cls.buyer_data, *args, **kwargs)
            return decorated_function
        # Patch the verify_jwt_token decorator with the mock function
        patch('app.auth.verify_jwt_token', side_effect=mock_verify_jwt_token).start()

    @classmethod
    def initalize_data(cls):
        print('Initalizing Data...')        
        countr_code = 'TC'
        buyer_id = 'test_buyer_id'
        seller_id = 'test_seller_id'
        merchant_id = 'test_merchant_id'
        product_id = 'test_product_id'
        cls.country_data = {
            "code": countr_code,
            "name": "test_country"
        }
        cls.seller_data = {
            "id": seller_id,
            "account_status": "active",
            "country_code": countr_code,
            "email": "test_email@example.com",
            "first_name": "Bob",
            "last_name": "Moyer Second",
            "password_hash": "TrEtnhWdeNykWngFBUObCbmUGyDFhiPVFhELzTptIfTsNRSqudxMnOfOCzaxUeZA",
            "password_salt": "hUsqDnfwtRhbOyRWxsTXuxmzxVEwjjeGFUgcohQUZQFSBYeXToZrszhIZmTqGTJM"
        }
        cls.buyer_data = {
            "id": buyer_id,
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
            "user_id": seller_id
        }
        cls.product_data = {
            "name": product_id,
            "price": 9.99,
            "status": "In stock",
            "stock_level": 10,
            "merchant_id": 1
        }
        cls.order_data = {
            "id": buyer_id,
            "orders": [
                {
                    "product": 1,
                    "merchant": 1,
                    "quantity": 2,
                    "unit_price": 8.99
                }
            ],
            "payment_status": "Received"
        }
        cls.empty_order_data = {
            "payment_status": "Received",
            "order_status": "Ordered",
            "user_id": buyer_id
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
            from app.models import User, Merchant, Country, Product, Order
            # Using atomic operation ensures all commands are done in one transaction, hence more efficeint
            with self.database.atomic():
                Country.create(**self.country_data)
                User.create(**self.seller_data)
                User.create(**self.buyer_data)
                Merchant.create(**self.merchant_data)
                Product.create(**self.product_data)
                Order.create(**self.empty_order_data)

    def tearDown(self):
        with self.app.app_context():
            from app.models import User, Merchant, Country, Product, Order
            # Using atomic operation ensures all commands are done in one transaction, hence more efficeint
            with self.database.atomic():
                Order.truncate_table(restart_identity=True, cascade=True)
                Product.truncate_table(restart_identity=True, cascade=True)
                Merchant.truncate_table(restart_identity=True, cascade=True)
                User.truncate_table(restart_identity=True, cascade=True)
                User.truncate_table(restart_identity=True, cascade=True)
                Country.truncate_table(restart_identity=True, cascade=True)


    def test_create_order(self):
        order_data = {
            "buyer_id": self.buyer_data['id'],
            "orders": [
                {
                    "product": 1,
                    "merchant": 1,
                    "quantity": 2,
                    "unit_price": 8.99
                }, 
                {
                    "product": 1,
                    "merchant": 1,
                    "quantity": 5,
                    "unit_price": 2.5
                }
            ],
            "payment_status": "Processing"
        }

        # Get the stock level before the order is placed
        order_volumn, old_stock_level = {}, {}
        for preorder in order_data["orders"]:
            if preorder["product"] not in order_volumn:
                order_volumn[preorder["product"]] = preorder["quantity"]
            else:
                order_volumn[preorder["product"]] += preorder["quantity"]
        for product_id, _ in order_volumn.items():
            with self.app.app_context():
                from app.models import Product
                with self.database.atomic():
                    current_stock = Product \
                                    .select(Product.stock_level) \
                                    .where(Product.id == product_id).execute()
                    old_stock_level[product_id] = list(current_stock)[0].stock_level

        response = self.client.post(
            f'/api/{api_version}/order/', 
            data=json.dumps(order_data), 
            content_type='application/json')
        data = json.loads(response.get_json())
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data["order_items"]), len(order_data["orders"]))
        
        # Confirm the stock level has been updated
        for product_id, stock_level in old_stock_level.items():
            with self.app.app_context():
                from app.models import Product
                with self.database.atomic():
                    current_stock = Product \
                                    .select(Product.stock_level) \
                                    .where(Product.id == product_id).execute()
                    new_stock_level = list(current_stock)[0].stock_level
                    self.assertEqual(new_stock_level, stock_level - order_volumn[product_id])
        
        assert True == True


    def test_get_orders(self):
        user_id = self.buyer_data['id']
        response = self.client.get(f'/api/{api_version}/order/{user_id}')
        data = json.loads(response.get_json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(data), list)
        self.assertGreater(len(data), 0)
    

    def test_get_order(self):
        user_id = self.buyer_data['id']
        order_id = 1
        response = self.client.get(f'/api/{api_version}/order/{user_id}/{order_id}')
        data = json.loads(response.get_json())
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(data), 0)
        self.assertEqual(data["id"], order_id)
        self.assertEqual(type(data), dict)


    def test_update_order(self):
        order_id = 1
        update_order_data = {
            "order_status": 'Cancelled'
        }

        # Verify the order status is different from what the new value is
        with self.app.app_context():
            from app.models import Order
            with self.database.atomic():
                original_order = Order.get(Order.id == order_id)
                self.assertNotEqual(original_order.order_status.value, update_order_data['order_status'])

        response = self.client.patch(
            f'/api/{api_version}/order/{order_id}', 
            data=json.dumps(update_order_data), 
            content_type='application/json')
        self.assertEqual(response.status_code, 204)

        with self.app.app_context():
            from app.models import Order
            with self.database.atomic():
                updated_order = Order.get(Order.id == order_id)
                self.assertEqual(updated_order.order_status.value, update_order_data['order_status'])


    def test_delete_order(self):
        order_id = 1
        response = self.client.delete(f'/api/{api_version}/order/{order_id}')
        self.assertEqual(response.status_code, 204)

        with self.app.app_context():
            from app.models import Order
            with self.database.atomic():
                deleted_order = Order \
                                .select() \
                                .where(Order.id == order_id)
                orders = [model_to_dict(order) for order in deleted_order]
                self.assertEqual(len(orders), 0)

if __name__ == '__main__':
    unittest.main()

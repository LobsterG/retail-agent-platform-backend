import json
import unittest



from functools import wraps
from peewee import PostgresqlDatabase
from app import create_app, db_initialize
from app.models import MODELS
from unittest.mock import patch, MagicMock
from playhouse.shortcuts import model_to_dict

# TODO: this needs to be refactored. The test database should already have exiting merchant created. 
# So each test could test their own instance of merchant
# This is to avoid delete or update operation corrupting the data in the test data.
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
                return f(cls.data_objects['user'], *args, **kwargs)
            return decorated_function
        # Patch the verify_jwt_token decorator with the mock function
        patch('app.auth.verify_jwt_token', side_effect=mock_verify_jwt_token).start()

    @classmethod
    def initalize_data(cls):
        countr_code = 'TC'
        user_id = 'test_user_id'
        merchant_id = 'test_merchant_id'
        country_data = {
            "code": countr_code,
            "name": "test_country"
        }
        user_data = {
            "id": user_id,
            "account_status": "active",
            "country_code": countr_code,
            "email": "test_email@example.com",
            "first_name": "Bob",
            "last_name": "Moyer Second",
            "password_hash": "TrEtnhWdeNykWngFBUObCbmUGyDFhiPVFhELzTptIfTsNRSqudxMnOfOCzaxUeZA",
            "password_salt": "hUsqDnfwtRhbOyRWxsTXuxmzxVEwjjeGFUgcohQUZQFSBYeXToZrszhIZmTqGTJM"
        }
        merchant_data = {
            "name": merchant_id,
            "country_code": countr_code,
            "user_id": user_id
        }
        print('Initalizing Data...')        
        cls.data_objects = {}
        cls.data_objects['country'] = country_data
        cls.data_objects['user'] = user_data
        cls.data_objects['merchant'] = merchant_data
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

    # 01 is added to the test case name as this should be the first test case to be run.
    # Other test cases will create data in the test db so the assert equal to 0 will no longer work
    # Pytest sort the test cases in alphabatical order
    def test_01_get_merchants(self):
        response = self.client.get(f'/api/{api_version}/merchant/')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 0)  # No merchants created yet
    
    def test_create_merchant(self):
        from app.models import User, Country, Merchant
        Country.create(**self.data_objects['country'])
        User.create(**self.data_objects['user'])

        ressponse = self.client.post(
            f'/api/{api_version}/merchant/', 
            data=json.dumps(self.data_objects['merchant']), 
            content_type='application/json')
        assert ressponse.status_code == 201

        # Confirm if the merchant is created with the given info
        response = self.client.get(f'/api/{api_version}/merchant/')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], self.data_objects['merchant']['name'])

    # This test is dependent on test_create_merchant
    def test_get_merchant(self):
        merchant_id = 1
        response = self.client.get(f'/api/{api_version}/merchant/{merchant_id}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["name"], self.data_objects['merchant']['name'])

    def test_update_merchant(self):
        update_merchant_data = {
            "name": 'test_changed_merchant_id'
        }

        merchant_id = 1
        response = self.client.put(
            f'/api/{api_version}/merchant/{merchant_id}', 
            data=json.dumps(update_merchant_data), 
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(f'/api/{api_version}/merchant/{merchant_id}')        
        data = response.get_json()
        self.assertEqual(data["name"], update_merchant_data['name'])

    # Adding z in the test name so this will execute last
    def test_z_delete_merchant(self):
        merchant_id = 1
        response = self.client.delete(f'/api/{api_version}/merchant/{merchant_id}')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(f'/api/{api_version}/merchant/')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 0)

if __name__ == '__main__':
    unittest.main()

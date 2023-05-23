import json
import unittest



from functools import wraps
from peewee import PostgresqlDatabase
from app import create_app, db_initialize
from app.models import MODELS
from unittest.mock import patch, MagicMock
from playhouse.shortcuts import model_to_dict

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

    # TODO: make sure this test is run first before other tests
    def test_get_merchants(self):
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

    # this test is dependent on test_create_merchant
    def test_get_merchant(self):
        merchant_id = 1
        response = self.client.get(f'/api/{api_version}/merchant/{merchant_id}')
        data = response.get_json()
        self.assertEqual(response.status_code, 200)

    # def test_update_merchant(self):
    #     assert True == True
    
    # def test_delete_merchant(self):
    #     assert True == True

if __name__ == '__main__':
    unittest.main()

import json
import pytest
import unittest

from flask import jsonify
from app import create_app, db_initialize
from app.models import MODELS
from app.models import User
from playhouse.shortcuts import model_to_dict

api_version = "v1"
class UserTestCase(unittest.TestCase):

    @classmethod
    def initalize_data(cls):
        print('Initalizing Data...')        
        user_id = "test_user"
        country_code = 'TC'

        cls.country_data = {
            "code": country_code,
            "name": "test_country"
        }
        cls.user_data = {
            "id": user_id,
            "account_status": "active",
            "country_code": country_code,
            "email": "test_email@example.com",
            "first_name": "Bob",
            "last_name": "Moyer Second",
            "password_hash": "TrEtnhWdeNykWngFBUObCbmUGyDFhiPVFhELzTptIfTsNRSqudxMnOfOCzaxUeZA",
            "password_salt": "hUsqDnfwtRhbOyRWxsTXuxmzxVEwjjeGFUgcohQUZQFSBYeXToZrszhIZmTqGTJM"
        }
        print('Initalizing Data Completed.')     

    @classmethod
    def setUpClass(cls):
        cls.initalize_data()
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
            from app.models import User, Country
            # Using atomic operation ensures all commands are done in one transaction, hence more efficeint
            with self.database.atomic():
                Country.create(**self.country_data)
                User.create(**self.user_data)

    def tearDown(self):
        with self.app.app_context():
            from app.models import User, Country
            # Using atomic operation ensures all commands are done in one transaction, hence more efficeint
            with self.database.atomic():
                User.truncate_table(restart_identity=True, cascade=True)
                Country.truncate_table(restart_identity=True, cascade=True)

    def test_get_users(self):
        res = self.client.get(f'/api/{api_version}/user/')
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], self.user_data['id'])

    def test_create_user(self):
        new_user_id = 'new_test_id'
        user_data = {
            "id": new_user_id,
            "account_status": "active",
            "country_code": self.country_data['code'],
            "email": "test2_email@example.com",
            "first_name": "Bob2",
            "last_name": "Moyer Second",
            "password_hash": "TrEtnhWdeNykWngFBUObCbmUGyDFhiPVFhELzTptIfTsNRSqudxMnOfOCzaxUeZA",
            "password_salt": "hUsqDnfwtRhbOyRWxsTXuxmzxVEwjjeGFUgcohQUZQFSBYeXToZrszhIZmTqGTJM"
        }

        res = self.client.post(
                    f'/api/{api_version}/user/',\
                    data=json.dumps(user_data),\
                    content_type='application/json')
        data = json.loads(res.data.decode('utf-8'))
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json['id'], user_data['id'])

    def test_get_user(self):
        res = self.client.get(f'/api/{api_version}/user/{self.user_data["id"]}')

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['id'], self.user_data["id"])

    def test_update_user(self):
        self.user_data["first_name"] = "NotBob"
        res = self.client.patch(
                    f'/api/{api_version}/user/{self.user_data["id"]}', \
                    data=json.dumps(self.user_data), \
                    content_type='application/json')
        
        assert res.status_code == 204
        with self.app.app_context():
            from app.models import User
            with self.database.atomic():
                updated_user = User.get(User.id == self.user_data["id"])
                self.assertEqual(updated_user.first_name, self.user_data['first_name'])

    def test_delete_user(self):    
        # Confirm if the data exists before the deletion
        with self.app.app_context():
            from app.models import User
            with self.database.atomic():
                deleted_user = User \
                                .select() \
                                .where(User.id == self.user_data["id"])
                orders = [model_to_dict(user) for user in deleted_user]
                self.assertEqual(len(orders), 1)    

        res = self.client.delete(
                    f'/api/{api_version}/user/{self.user_data["id"]}', \
                    content_type='application/json')

        assert res.status_code == 200
        assert res.get_json()['message'] == 'User deleted successfully'

        with self.app.app_context():
            from app.models import User
            with self.database.atomic():
                deleted_user = User \
                                .select() \
                                .where(User.id == self.user_data["id"])
                orders = [model_to_dict(user) for user in deleted_user]
                self.assertEqual(len(orders), 0)

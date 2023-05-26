import json
import pytest
import peewee

# from . import conftest
from flask import jsonify
from unittest.mock import patch, MagicMock
from app.models.users import User
from playhouse.shortcuts import model_to_dict

api_version = "v1"

@patch('app.models.users.User.select')
def test_get_users(mock_users_select, client, user):
        
    mock_users_select.return_value = [User(**user)]
    res = client.get(f'/api/{api_version}/user/')
    
    assert res.status_code == 200
    assert len(json.loads(res.data.decode('utf-8'))) == 1
    assert json.loads(res.data.decode('utf-8'))[0]['id'] == user['id']

@patch('app.models.users.User.create')
def test_create_user(mock_user_create, client, user):
    
    mock_user_create.return_value = User(**user)
    res = client.post(f'/api/{api_version}/user/', data=json.dumps(user), content_type='application/json')
    
    assert res.status_code == 201
    assert res.json['id'] == user['id']

@patch('app.models.users.User.get')
def test_get_user(mock_user_get, client, user):

    mock_user = User(**user)
    mock_user_get.return_value = mock_user
    res = client.get(f'/api/{api_version}/user/{mock_user.id}')
    assert res.status_code == 200
    assert res.json['id'] == mock_user.id

@patch('app.models.users.User.update')
@patch('peewee.Query.where')
def test_update_user(mock_where, mock_user_update, client, user):
    
    updated_user = User(**user)

    # Configure mock_user_update to return the updated user
    mock_user_update.return_value = peewee.Query()
    mock_where = updated_user
    
    # Make a request to the API endpoint
    res = client.put(f'/api/{api_version}/user/{updated_user.id}', data=json.dumps(user), content_type='application/json')

    assert res.status_code == 200
    assert res.get_json()['message'] == 'User updated successfully'

@patch('app.models.users.User.delete')
@patch('peewee.Query.where')
def test_delete_user(mock_where, mock_user_delete, client, user):
    
    delete_user = User(**user)

    mock_user_delete.return_value = peewee.Query()
    mock_where = delete_user
    
    # Make a request to the API endpoint
    res = client.delete(f'/api/{api_version}/user/{delete_user.id}', data=json.dumps(user), content_type='application/json')

    assert res.status_code == 200
    assert res.get_json()['message'] == 'User deleted successfully'

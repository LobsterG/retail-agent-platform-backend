from flask import jsonify, request
from flask import Blueprint
from app import csrf
from app.models.users import User
from playhouse.shortcuts import model_to_dict

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/', methods=['GET', 'POST'])
def get_users():
    if request.method == 'GET':
        users = User.select()
        user_data = [model_to_dict(user) for user in users]
        return jsonify(user_data)
    elif request.method == 'POST':
        data = request.json
        user = User(
            first_name = data['first_name'],
            last_name = data['last_name'],
            email = data['email'],
            password_salt = data['pystr'],
            password_hash = data['pystr'],
            account_status = data['account_status'],
            country_code = data['country_code']
        )
        try:
            user.save()
        # TODO: have more specific error handling logic
        except Exception as e:
            print(f'Error: {e}')
        return jsonify(model_to_dict(user)), 201
    return ''

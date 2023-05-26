import logging 
import datetime
import jwt

from flask import jsonify, request, abort
from flask import Blueprint
from app import csrf
from app.models.users import User
from playhouse.shortcuts import model_to_dict
from config import Config
from peewee import DoesNotExist
from werkzeug.security import check_password_hash, generate_password_hash

user_bp = Blueprint('user_bp', __name__)
logger = logging.getLogger(Config.LOGGER_NAME)

@user_bp.route('/', methods=['GET'])
def get_users():
    try:
        users = User.select()
        user_data = [user.to_dict() for user in users]
        logger.debug("Successfully retrieved all users.")
        return jsonify(user_data), 200
    except Exception as e:
        logger.exception("Error getting errors:", exc_info=e)
        return jsonify({"error": "Unable to retrieve users"}), 500

@user_bp.route('/', methods=['POST'])
def create_user():
    try:
        data = request.json
        data['password_hash'] = generate_password_hash(data['password_hash'])
        user = User.create(**data)
        return jsonify(user.to_dict()), 201
    except Exception as e:
        logger.exception(f"Error creating user", exc_info=e)
        return jsonify({"error": "Unable to create user"}), 400

@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        if not data or 'email' not in data or 'password' not in data:
            abort(400, "Please provide user credentials")

        email = data['email']
        password = data['password']

        # Check if user exists
        user = User().get_or_none(email=email)
        if not user:
            return {
                "message": "Invalid credentials",
                "data": None,
                "error": "Unauthorized"
            }, 401
        logger.debug(f"Email found: {user.email}")

        # Verify password
        if not check_password_hash(user.password_hash, password):
            return {
                "message": "Invalid credentials",
                "data": None,
                "error": "Unauthorized"
            }, 401
        logger.debug(f"Password matched for user {user.email}")

        # Generate JWT token
        exp = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        jwt_token = jwt.encode({'email': email, 'exp': exp}, Config.SECRET_KEY, algorithm='HS256')

        return {
            "message": "Successfully logged in",
            "data": {"token": jwt_token},
            "error": None
        }, 200
    except Exception as e:
        logger.exception(f"Error logging into user", exc_info=e)
        return jsonify({"error": "Unable to login"}), 400

@user_bp.route('/<username>', methods=["GET"])
def get_user(username):
    try:
        user = User.get(User.id == username)
        return jsonify(user.to_dict()), 200
    except DoesNotExist:
        logger.debug(f"Error user not found {username}")
        return jsonify({"Error": "User not found"}), 404
    except Exception as e:
        logger.exception(f"Error getting user", exc_info=e)
        return jsonify({"error": "Unable to retrieve user"}),500

@user_bp.route('/<username>', methods=["PATCH"])
def update_user(username):
    try:
        data = request.get_json()
        # TODO: need to somehow filter the data given by user
        query = User.update(**data).where(User.id == username)
        rows_updated = query.execute()
        if rows_updated:
            return jsonify({"message": "User updated successfully"}), 204
        else:
            return jsonify({"Message": "No changes were made"}), 400
    except DoesNotExist:
        logger.debug(f"Error user not found {username}")
        return jsonify({"Error": "User not found"}), 404
    except Exception as e:
        logger.exception(f"Error getting user", exc_info=e)
        return jsonify({"error": "Unable to update user"}), 500


@user_bp.route('/<username>', methods=["DELETE"])
def delete_user(username):
    try:
        query = User.delete().where(User.id == username)
        query.execute()
        logger.debug(f"User {username} has been deleted.")
        return jsonify({"message": "User deleted successfully"}), 200
    except DoesNotExist:
        logger.debug(f"Error user not found {username}")
        return jsonify({"Error": "User not found"}), 404
    except Exception as e:
        logger.exception(f"Error deleting user", exc_info=e)
        return jsonify({"error": "Unable to delete user"}), 500
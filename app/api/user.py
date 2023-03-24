import logging 

from flask import jsonify, request
from flask import Blueprint
from app import csrf
from app.models.users import User
from playhouse.shortcuts import model_to_dict
from config import Config
from peewee import DoesNotExist

user_bp = Blueprint('user_bp', __name__)
logger = logging.getLogger(Config.LOGGER_NAME)

@user_bp.route('/', methods=['GET'])
def get_users():
    try:
        users = User.select()
        user_data = [model_to_dict(user) for user in users]
        logger.debug("Successfully retrieved all users.")
        return jsonify(user_data), 200
    except Exception as e:
        logger.exception("Error getting errors:", exc_info=e)
        return jsonify({"error": "Unable to retrieve users"}), 500

@user_bp.route('/', methods=['POST'])
def create_user():
    try:
        data = request.json
        user = User.create(**data)
        return jsonify(user.to_dict()), 201
    except Exception as e:
        logger.exception(f"Error creating user", exc_info=e)
        return jsonify({"error": "Unable to create user"}), 400

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

@user_bp.route('/<username>', methods=["PUT"])
def update_user(username):
    try:
        data = request.get_json()
        # TODO: need to somehow filter the data given by user
        query = User.update(**data).where(User.id == username)
        query.execute()
        update_user = User.get(User.id == username)
        return jsonify(updated_user.to_dict()), 200
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
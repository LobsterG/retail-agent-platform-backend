import logging 

from flask import jsonify, request
from flask import Blueprint
from app import csrf
from app.models.merchants import Merchant
from playhouse.shortcuts import model_to_dict
from config import Config
from peewee import DoesNotExist
from app.auth import verify_jwt_token


merchant_bp = Blueprint('merchant_bp', __name__)
logger = logging.getLogger(Config.LOGGER_NAME)

@merchant_bp.route('/', methods=['GET'])
def get_merchants():
    try:
        merchants = Merchant.select()
        merchant_data = [model_to_dict(merchant) for merchant in merchants]
        logger.debug("Successfully retrieved all merchants.")
        return jsonify(merchant_data), 200
    except Exception as e:
        logger.exception("Error getting errors:", exc_info=e)
        return jsonify({"error": "Unable to retrieve merchants"}), 500

@merchant_bp.route('/', methods=['POST'])
@verify_jwt_token
def create_merchant(user):
    try:
        data = request.json
        merchant = Merchant.create(**data)
        return jsonify(merchant.to_dict()), 201
    except Exception as e:
        logger.exception(f"Error creating merchant", exc_info=e)
        return jsonify({"error": "Unable to create merchant"}), 400

@merchant_bp.route('/<merchantname>', methods=["GET"])
@verify_jwt_token
def get_merchant(user, merchantname):
    try:
        merchant = Merchant.get(Merchant.id == merchantname)
        return jsonify(model_to_dict(merchant)), 200
    except DoesNotExist:
        logger.debug(f"Error merchant not found {merchantname}")
        return jsonify({"Error": "Merchant not found"}), 404
    except Exception as e:
        logger.exception(f"Error getting merchant", exc_info=e)
        return jsonify({"error": "Unable to retrieve merchant"}),500

@merchant_bp.route('/<merchantname>', methods=["PUT"])
@verify_jwt_token
def update_merchant(user, merchantname):
    try:
        data = request.get_json()
        # TODO: need to somehow filter the data given by merchant
        query = Merchant.update(**data).where(Merchant.id == merchantname)
        query.execute()
        logger.debug(f"Successfully updated merchant {merchantname}.")
        updated_merchant = Merchant.get(Merchant.id == merchantname)
        return jsonify(updated_merchant.to_dict()), 200
    except DoesNotExist:
        logger.debug(f"Error merchant not found {merchantname}")
        return jsonify({"Error": "Merchant not found"}), 404
    except Exception as e:
        logger.exception(f"Error getting merchant", exc_info=e)
        return jsonify({"error": "Unable to update merchant"}), 500


@merchant_bp.route('/<merchantname>', methods=["DELETE"])
@verify_jwt_token
def delete_merchant(user, merchantname):
    try:
        query = Merchant.delete().where(Merchant.id == merchantname)
        query.execute()
        logger.debug(f"Merchant {merchantname} has been deleted.")
        return jsonify({"message": "Merchant deleted successfully"}), 200
    except DoesNotExist:
        logger.debug(f"Error merchant not found {merchantname}")
        return jsonify({"Error": "Merchant not found"}), 404
    except Exception as e:
        logger.exception(f"Error deleting merchant", exc_info=e)
        return jsonify({"error": "Unable to delete merchant"}), 500
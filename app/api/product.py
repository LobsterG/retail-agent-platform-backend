import logging 
import json
import datetime
from flask import jsonify, request
from flask import Blueprint
from app import csrf
from app.helper import CustomEncoder
from app.models import Product, Merchant, StockStatus, User
from playhouse.shortcuts import model_to_dict
from config import Config
from peewee import DoesNotExist
from app.auth import verify_jwt_token


product_bp = Blueprint('product_bp', __name__)
logger = logging.getLogger(Config.LOGGER_NAME)


# Confirms if the user is the owner of the merchant
def _is_merchant_same_as_user(merchant_id, user_id):
    merchant = Merchant.get_or_none(Merchant.id == merchant_id)
    if merchant and merchant.user_id.id == user_id:
        return True
    return False

@product_bp.route('/', methods=['GET'])
def get_products():
    try:
        products = Product.select()
        product_data = [model_to_dict(product) for product in products]
        logger.debug("Successfully retrieved all products.")
        return jsonify(product_data), 200
    except Exception as e:
        logger.exception("Error getting errors:", exc_info=e)
        return jsonify({"error": "Unable to retrieve products"}), 500

@product_bp.route('/<product_id>', methods=["GET"])
def get_product(product_id):
    try:
        product = Product.get(Product.id == product_id)
        logger.debug(f"Successfully retrieved product {product_id}.")
        return jsonify(model_to_dict(product)), 200
    except DoesNotExist:
        logger.debug(f"Error product not found {product_id}")
        return jsonify({"Error": "Product not found"}), 404
    except Exception as e:
        logger.exception(f"Error getting product", exc_info=e)
        return jsonify({"error": "Unable to retrieve product"}),500

"""
Expected data structure:
{
    "name": "product_name",
    "price": 10.90,
    "stock_level": 20,
    "merchant_id": 1
}
"""
@product_bp.route('/', methods=['POST'])
@verify_jwt_token
def create_product(user):
    try:
        data = request.json

        if _is_merchant_same_as_user(data['merchant_id'], user['id']):
            if data['stock_level'] > 5:
                data['status'] = StockStatus.IN_STOCK.value
            elif data['stock_level'] > 0:
                data['status'] = StockStatus.LOW_ON_STOCK.value
            else:
                data['stock_level'] = 0
                data['status'] = StockStatus.OUT_OF_STOCK.value
            product = Product.create(**data)
            return jsonify(model_to_dict(product)), 201
        else:
            logger.exception(f"User {user['id']} tried creating product with merchant {data['merchant_id']}")
            return jsonify({"error": f"Not authorized to create product using {data['merchant_id']}"}), 403
        
    except Exception as e:
        logger.exception(f"Error creating product", exc_info=e)
        return jsonify({"error": "Unable to create product"}), 400

@product_bp.route('/<product_id>', methods=["PATCH"])
@verify_jwt_token
def update_product(user, product_id):
    try:
        data = request.get_json()
        # product = Product.get_or_none((Product.id == product_id) & (Product.merchant_id.user_id.id == user['id']))
        product = Product.select().join(Merchant).join(User).where((Product.id == product_id) & (User.id == user['id'])).first()
        if product:
            # Update the fields with the provided data
            for field, value in data.items():
                if field in Product._meta.fields:
                    setattr(product, field, value)
            logger.debug(f"Successfully updated product {product_id}.")
            product.save()
            return jsonify({"Message": "Updated successfully"}), 204
        else:
            logger.exception(f"User {user['id']} tried updating product with merchant {data['merchant_id']}")
            return jsonify({"error": f"Not authorized to create product using {data['merchant_id']}"}), 403
    except DoesNotExist:
        logger.debug(f"Error product not found {product_id}")
        return jsonify({"Error": "Product not found"}), 404
    except Exception as e:
        logger.exception(f"Error getting product", exc_info=e)
        return jsonify({"error": "Unable to update product"}), 500

@product_bp.route('/<product_id>', methods=["DELETE"])
@verify_jwt_token
def delete_product(user, product_id):
    try:
        product = Product.get(Product.id == product_id)
        # Check if the requesting user is the owner of the associated merchant
        if product.merchant_id.user_id.id != user['id']:
            logger.exception(f"User {user['id']} tried deleting product {product_id} with merchant {product.merchant_id}")
            return jsonify({"error": f"Not authorized to delete product using {user['id']}"}), 403

        product.delete_instance()
        logger.debug(f"Product {product_id} has been deleted.")
        return jsonify({"message": "Product deleted successfully"}), 204
    except DoesNotExist:
        logger.debug(f"Error product not found {product_id}")
        return jsonify({"Error": "Product not found"}), 404
    except Exception as e:
        logger.exception(f"Error deleting product", exc_info=e)
        return jsonify({"error": "Unable to delete product"}), 500
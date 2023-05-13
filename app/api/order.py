import logging 

from flask import jsonify, request
from flask import Blueprint
from app import csrf
from app.models.orders import Order
from app.models.order_items import OrderItem
from playhouse.shortcuts import model_to_dict
from config import Config
from peewee import DoesNotExist
from app.auth import verify_jwt_token


order_bp = Blueprint('order_bp', __name__)
logger = logging.getLogger(Config.LOGGER_NAME)

@order_bp.route('/<userid>', methods=['GET'])
@verify_jwt_token
def get_orders(user, jwt_token, user_id):
    try:
        orders = Order \
                    .select() \
                    .where(Order.user_id == user_id) \
                    .order_by(Order.created_at)
        order_data = [model_to_dict(order) for order in orders]
        logger.debug("Successfully retrieved all orders.")
        return jsonify(order_data), 200
    except Exception as e:
        logger.exception("Error getting errors:", exc_info=e)
        return jsonify({"error": "Unable to retrieve orders"}), 500

@order_bp.route('/', methods=['POST'])
@verify_jwt_token
def create_order(user):
    try:
        data = request.json
        order = Order.create(**data)
        return jsonify(order.to_dict()), 201
    except Exception as e:
        logger.exception(f"Error creating order", exc_info=e)
        return jsonify({"error": "Unable to create order"}), 400

@order_bp.route('/<userid>/<orderid>', methods=["GET"])
@verify_jwt_token
def get_order(user, jwt_token, ordername):
    try:
        order = Order.get(Order.id == ordername)
        return jsonify(order.to_dict()), 200
    except DoesNotExist:
        logger.debug(f"Error order not found {ordername}")
        return jsonify({"Error": "Order not found"}), 404
    except Exception as e:
        logger.exception(f"Error getting order", exc_info=e)
        return jsonify({"error": "Unable to retrieve order"}),500

@order_bp.route('/<ordername>', methods=["PUT"])
@verify_jwt_token
def update_order(user, jwt_token, ordername):
    try:
        data = request.get_json()
        # TODO: need to somehow filter the data given by order
        query = Order.update(**data).where(Order.id == ordername)
        query.execute()
        update_order = Order.get(Order.id == ordername)
        return jsonify(updated_order.to_dict()), 200
    except DoesNotExist:
        logger.debug(f"Error order not found {ordername}")
        return jsonify({"Error": "Order not found"}), 404
    except Exception as e:
        logger.exception(f"Error getting order", exc_info=e)
        return jsonify({"error": "Unable to update order"}), 500


@order_bp.route('/<ordername>', methods=["DELETE"])
@verify_jwt_token
def delete_order(user, jwt_token, ordername):
    try:
        query = Order.delete().where(Order.id == ordername)
        query.execute()
        logger.debug(f"Order {ordername} has been deleted.")
        return jsonify({"message": "Order deleted successfully"}), 200
    except DoesNotExist:
        logger.debug(f"Error order not found {ordername}")
        return jsonify({"Error": "Order not found"}), 404
    except Exception as e:
        logger.exception(f"Error deleting order", exc_info=e)
        return jsonify({"error": "Unable to delete order"}), 500
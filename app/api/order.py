import logging 

from flask import jsonify, request
from flask import Blueprint
from app import csrf
from app.models import Order, OrderStatus, PaymentStatus, OrderItem, Product, Merchant
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


def generate_order_id(buyer_id, payment_status):
    order = Order.create(
                user_id=buy_id,
                payment_status = payment_status,
                order_status = OrderStatus.ORDERED
            )


"""
1. Create an order with the user id, order status and payment should be use default
2. Data should contain the product, quantity and price; use this info to create one or more order_items
3. Update product stock level if order and order item are created successfully
4. Endpoint should check if:
    - products' stock level is >= ordered amount
    - ordered person is different from the merchant
Expected data structure:
{
    "id": "user_id",
    "orders": [
        {
            "product": "product_id",
            "merchant": "merchant_id",
            "quantitiy": "integer",
            "unit_price": "float"
        }
    ],
    "payment_status": "PaymentStatus enum"
}
"""
@order_bp.route('/', methods=['POST'])
@verify_jwt_token
def create_order(user):
    try:        
        # TODO: assume the data structure has already been validated at an API gateway?
        data = request.json

        if data["payment_status"] not in PaymentStatus:
            logger.debug(f"Invalid payment status, {data['payment_status']}.")
            return jsonify({"error": "Invalid payment status."}), 400

        # Get all the product and merchant IDs and query at once to reduct server load
        buyer_id = data["id"]
        product_ids = [p["product"] for p in data["orders"]]
        purchase_products = (
            Product.select(Product, Merchant, User)    
            .join(Merchant)
            .join(User)
            .where(
                    (Merchant.user_id != buyer_id) &
                    (Product.id.in_(product_ids))
                )
        )
        
        if not purchase_products:
            logger.debug(f"No valid products found for user {buyer_id} with products {product_ids}.")
            return jsonify({"error": "No valid products found."}), 400

        # So product can be quickly accessed via ID
        product_dict = {product.id: product for product in purchase_products}

        order_id = None
        orders = []
        for purchase_info in data["orders"]:
            # Check if stock level is enough to create the order and 
            if purchase_info["product"] in product_dict and \
                purchase_info["quantitiy"] <= product_dict[purchase_info["product"]]["stock_level"]:
                
                if order_id is None:
                    order_id = generate_order_id(buyer_id, data["payment_status"])
                
                # Create order for item
                orders.append(
                    OrderItem.create(
                        price = purchase_info["unit_price"],
                        quantity = purchase_info["quantity"],
                        order_id = order_id,
                        product_id = purchase_info["product"]
                    )
                )
                # Update stock level
                query = Product \
                            .update(stocket_level=Product.stock_level - purchase_info["quantitiy"]) \
                            .where(Product.id == purchase_info["product"])
                query.execute()
                # product_dict[purchase_info["product"]].stock_level -= purchase_info["quantitiy"]
                # product_dict[purchase_info["product"]].save()

        if not orders:
            logger.debug(f"No valid orders can be created for user {buyer_id} with products {product_ids}.")
            return jsonify({"error": "No valid orders can be created."}), 400

        result = {
            "order_id": order_id,
            "order_items": orders.to_dict()
        }
        return jsonify(result), 201
    except Exception as e:
        logger.exception(f"Error creating order", exc_info=e)
        return jsonify({"error": "Unable to create order"}), 400

@order_bp.route('/<userid>/<orderid>', methods=["GET"])
@verify_jwt_token
def get_order(user, jwt_token, user_id, order_id):
    try:
        # TODO: need to handle a case where user and user_id has a mismatch
        order = Order.get(Order.id == order_id)

        if order.user_id != user_id:
            logger.debug(f"Error user {user_id} tried accessing order {order_id}")
            return jsonify({"Error": "Order does not belong to you."}), 401

        return jsonify(order.to_dict()), 200
    except DoesNotExist:
        logger.debug(f"Error order not found {order_id}")
        return jsonify({"Error": "Order not found"}), 404
    except Exception as e:
        logger.exception(f"Error getting order", exc_info=e)
        return jsonify({"error": "Unable to retrieve order"}),500

"""
Only payment_status and order_status can be updated, so the expected data structure should be
data = {
    "payment_status": "enum",
    "order_status": "enum"
}
This would be a request from the payment service and logistic service, so would not be from the end user directly
"""
@order_bp.route('/<orderid>', methods=["PATCH"])
@verify_jwt_token
def update_order(user, jwt_token, order_id):
    try:
        data = request.get_json()
        query = Order.update(**data).where(Order.id == order_id)
        rows_updated = query.execute()
        if rows_updated:
            return jsonify({"Message": "Updated successfully"}), 204
        else:
            return jsonify({"Message": "No changes were made"}), 400
    except DoesNotExist:
        logger.debug(f"Error order not found {order_id}")
        return jsonify({"Error": "Order not found"}), 404
    except Exception as e:
        logger.exception(f"Error getting order", exc_info=e)
        return jsonify({"error": "Unable to update order"}), 500


@order_bp.route('/<order_id>', methods=["DELETE"])
@verify_jwt_token
def delete_order(user, jwt_token, order_id):
    try:
        query = Order.delete().where(Order.id == order_id)
        query.execute()
        logger.debug(f"Order {order_id} has been deleted.")
        return jsonify({"Message": "Order deleted successfully"}), 204
    except DoesNotExist:
        logger.debug(f"Error order not found {order_id}")
        return jsonify({"Error": "Order not found"}), 404
    except Exception as e:
        logger.exception(f"Error deleting order", exc_info=e)
        return jsonify({"error": "Unable to delete order"}), 500
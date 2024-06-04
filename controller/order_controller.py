from app import app
from model.order_model import OrderModel
from flask import request, send_file, jsonify, redirect
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
    jwt_required
)
from configs.config_thread import lock
size_model = OrderModel()

@app.route("/test/value_discount", methods=["GET"])
def get_all_size1():
    with lock:
        return size_model.get_discount_amount_product(request.json)

@app.route("/api/orders", methods=["POST"])
@jwt_required()
def order_products():
    with lock:
        return size_model.order_product(request.json)

@app.route("/api/admin/orders", methods=["GET"])
@jwt_required()
def get_all_order():
    with lock:
        return size_model.get_all_order()

@app.route("/api/admin/orders/<string:id>", methods=["PUT"])
@jwt_required()
def update_status_order(id):
    with lock:
        return size_model.update_status_order(id, request.json)

@app.route("/api/orders/users/<int:userId>", methods=["GET"])
@jwt_required()
def get_order_by_user(userId):
    with lock:
        return size_model.get_order_by_user(userId)


@app.route("/api/orders/<string:orderId>", methods=["GET"])
@jwt_required()
def get_order_detail(orderId):
    with lock:
        return size_model.get_order_detail(orderId)

@app.route("/api/orders/<string:orderId>", methods=["PUT"])
@jwt_required()
def cancel_order(orderId):
    with lock:
        return size_model.cancel_order(orderId)

@app.route('/vnpay_return', methods=['GET'])
def vnpay_return():
    return size_model.vnpay_return()

@app.route("/api/orders/users/<int:userId>/order-items",methods= ['GET'])
@jwt_required()
def get_orderItem_received(userId):
    with lock:
        return size_model.get_order_received(userId)

@app.route("/api/comment",methods = ['POST'])
@jwt_required()
def sent_comment():
    return size_model.send_comment()

@app.route("/api/admin/orders/revenue", methods=["GET"])
@jwt_required()
def revenue_statistic_year():
    with lock:
        return size_model.revenue_statistic_year()

@app.route("/api/admin/orders/year", methods=["GET"])
@jwt_required()
def get_year_order():
    with lock:
        return size_model.get_year_order()

@app.route("/api/admin/orders/status", methods=["GET"])
@jwt_required()
def get_status_order():
    with lock:
        return size_model.get_status_order()
    
    
@app.route("/api/admin/orders/count", methods=['GET'])
@jwt_required()
def get_count_order():
    with lock:
        return size_model.get_count_order()
    
@app.route("/api/admin/search_orders_admin", methods=['GET'])
@jwt_required()
def search_order_admin():
    with lock:
        return size_model.search_order_admin()
    
@app.route("/api/admin/get-order-month-year", methods=['GET'])
# @jwt_required()
def get_orders_by_month_year():
    with lock:
        return size_model.get_orders_by_month_year()
    
@app.route("/api/admin/get-status-month-year", methods=['GET'])
@jwt_required()
def get_order_status_by_month_year():
    with lock:
        return size_model.get_order_status_by_month_year()

@app.route("/api/admin/order-items/<string:id>", methods=['GET'])
# @jwt_required()
def get_detail_product_orders(id):
    return size_model.get_detail_product_order(id)
from app import app
from model.order_model import OrderModel
from flask import request, send_file, jsonify, redirect
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
    jwt_required
)
size_model = OrderModel()

@app.route("/test/value_discount", methods=["GET"])
def get_all_size1():
    return size_model.get_discount_amount_product(request.json)

@app.route("/api/orders", methods=["POST"])
@jwt_required()
def order_products():
    return size_model.order_product(request.json)

@app.route("/api/admin/orders", methods=["GET"])
@jwt_required()
def get_all_order():
    return size_model.get_all_order()

@app.route("/api/admin/orders/<int:id>", methods=["PUT"])
@jwt_required()
def update_status_order(id):
    return size_model.update_status_order(id, request.json)

@app.route("/api/orders/users/<int:userId>", methods=["GET"])
@jwt_required()
def get_order_by_user(userId):
    return size_model.get_order_by_user(userId)


@app.route("/api/orders/<int:orderId>", methods=["GET"])
@jwt_required()
def get_order_detail(orderId):
    return size_model.get_order_detail(orderId)

@app.route("/api/orders/<int:orderId>", methods=["PUT"])
@jwt_required()
def cancel_order(orderId):
    return size_model.cancel_order(orderId)

@app.route('/vnpay_return', methods=['GET'])
def vnpay_return():
    vnp_ResponseCode = request.args.get('vnp_ResponseCode')
    print("vnp_ResponseCode", vnp_ResponseCode)
    if vnp_ResponseCode == '00':
        return redirect('/vnpay_return?state=1')
    else:
        return redirect('/vnpay_return?state=0')
    
    
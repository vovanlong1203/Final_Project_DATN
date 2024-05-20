from app import app
from model.order_model import OrderModel
from flask import request, send_file, jsonify
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
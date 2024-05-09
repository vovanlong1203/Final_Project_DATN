from app import app
from model.product_size_model import ProductSizeModel
from flask import request, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
    jwt_required
)
productsize_model = ProductSizeModel()

@app.route("/api/product_size/admin", methods=["GET"])
@jwt_required()
def get_data_product_size():
    return productsize_model.get_data()

@app.route("/api/product_size/admin", methods=["POST"])
@jwt_required()
def insert_data_product_size():
    return productsize_model.add_data(request.json)
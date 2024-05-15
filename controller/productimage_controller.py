from app import app
from model.product_image_model import ProductImageModel
from flask import request, send_file, jsonify
from flask_jwt_extended import (
    jwt_required
)
product_image_model = ProductImageModel()

@app.route("/api/admin/product_image/admin", methods=["GET"])
@jwt_required()
def get_dataProductImage():
    return product_image_model.get_data()

@app.route("/api/admin/product_image/admin", methods=["POST"])
@jwt_required()
def add_dataProductImage():
    print("adasdasdasdad ", request.form)
    return product_image_model.add_data(request.form)


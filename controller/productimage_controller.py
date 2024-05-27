from app import app
from model.product_image_model import ProductImageModel
from flask import request, send_file, jsonify
from flask_jwt_extended import (
    jwt_required
)
product_image_model = ProductImageModel()
from configs.config_thread import lock

@app.route("/api/admin/product_image", methods=["GET"])
@jwt_required()
def get_dataProductImage():
    with lock:
        return product_image_model.get_data()

@app.route("/api/admin/product_image", methods=["POST"])
@jwt_required()
def add_dataProductImage():
    with lock:
        return product_image_model.add_data(request.form)

@app.route("/api/admin/product_image/<int:id>", methods=['DELETE'])
@jwt_required()
def delete_product_images(id):
    with lock:
        return product_image_model.delete_data(id)
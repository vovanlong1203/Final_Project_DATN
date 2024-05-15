from app import app
from model.product_model import ProductModel
from flask import request, send_file, jsonify
from flask_jwt_extended import (
    jwt_required
)
product_model = ProductModel()


@app.route("/products/all", methods=["GET"])
def get_all_products():
    return product_model.get_all_products()

@app.route("/api/product/product/searchAll", methods=["GET"])
def search_products():
    return product_model.search_products()

@app.route("/products/product_detail", methods=["GET"])
def get_product_detail():
    return product_model.get_product_detail()

@app.route("/api/category", methods=["GET"])
def get_category():
    return product_model.get_category_name()
  
@app.route("/api/admin/product", methods=['GET'])
@jwt_required()
def get_product():
    return product_model.get_product()

@app.route("/api/admin/product", methods=['POST'])
@jwt_required()
def add_product():
    return product_model.add_product(request.json)
  
@app.route("/api/admin/product", methods=['PUT'])
@jwt_required()
def update_product():
    return product_model.update_product(request.json)
  
@app.route("/api/admin/product/<int:id>", methods=['DELETE'])
@jwt_required()
def delete_product(id):
    return product_model.delete_product(id)


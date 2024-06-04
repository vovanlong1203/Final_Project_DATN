from app import app
from model.product_model import ProductModel
from flask_caching import Cache
from flask import request, send_file, jsonify
from flask_jwt_extended import (
    jwt_required
)
from configs.config_thread import lock
product_model = ProductModel()
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)


@app.route("/products/all", methods=["GET"])
@cache.cached(timeout=60, key_prefix='all_products')
def get_all_products():
    with lock:
        return product_model.get_all_products()
    

@app.route("/products", methods=["GET"])
def get_products():
    with lock:
        return product_model.get_products()



@app.route("/api/product/product/searchAll", methods=["GET"])
def search_products():
    with lock:
        return product_model.search_products()

def make_cache_key():
    return request.full_path

@app.route("/products/product_detail/<int:id>", methods=["GET"])
@cache.cached(timeout=60, key_prefix=make_cache_key)
def get_product_detail(id):
    with lock:
        return product_model.get_product_detail(id)

@app.route("/api/category", methods=["GET"])
def get_category():
    with lock:
        return product_model.get_category_name()
  
@app.route("/api/admin/product", methods=['GET'])
@jwt_required()
def get_product():
    with lock:
        return product_model.get_product()

@app.route("/api/admin/product", methods=['POST'])
@jwt_required()
def add_product():
    with lock:
        return product_model.add_product(request.json)
  
@app.route("/api/admin/product", methods=['PUT'])
@jwt_required()
def update_product():
    with lock:
        return product_model.update_product(request.json)
  
@app.route("/api/admin/product/<int:id>", methods=['DELETE'])
@jwt_required()
def delete_product(id):
    with lock:
        return product_model.delete_product(id)
    
    
@app.route("/api/admin/product/count", methods=['GET'])
@jwt_required()
def get_count_product():
    with lock:
        return product_model.get_count_product()


@app.route("/api/admin/products", methods=['GET'])
@jwt_required()
def get_products_pagination():
    with lock:
        return product_model.get_products_pagination()

@app.route("/api/admin/search_products_admin", methods=['GET'])
@jwt_required()
def search_products_admin():
    with lock:
        return product_model.search_products_admin()



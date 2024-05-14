from app import app
from model.cartitem_model import CartIemModel
from flask import request, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    create_refresh_token,
    get_jwt_identity, set_access_cookies,
    set_refresh_cookies, unset_jwt_cookies
)
    
cartitem_model = CartIemModel()

@app.route("/api/carts/user/<int:user_id>", methods=["GET"])
@jwt_required()
def view_cart_item(user_id):
    return cartitem_model.view_cart_items(user_id)

@app.route("/api/carts/user/<int:user_id>", methods=["POST"])
@jwt_required()
def add_product_into_cartitems(user_id):
    print("user_id: ", user_id)
    print("json : ", request.json)
    return cartitem_model.add_product_into_cart_items(user_id, request.json)

@app.route("/api/carts/user/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_product_into_cartitem(user_id):
    print("user_id: ", user_id)
    print('json : ', request.json)
    return cartitem_model.delete_product_in_cart_items(user_id, request.json)

@app.route("/api/carts/user/<int:user_id>/<int:cart_items_id>", methods=["PUT"])
@jwt_required()
def update_product_into_cart_item(user_id, cart_items_id):
    print("user_id: ", user_id)
    print("cart_items_id: ", cart_items_id)
    try:
        print("request.json: ", request.json)
        return cartitem_model.update_product_in_cart_items(user_id, cart_items_id, request.json)
    except Exception as e:
        return str(e), 500
    